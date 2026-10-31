"""Idempotent ingredient catalog loader (keyed by English catalog slug)."""

from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from importlib import resources

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from allergens.filer_seed import ensure_folder, ensure_image_from_package
from allergens.models import Allergen
from ingredients.models import (
    Ingredient,
    IngredientAllergenPresence,
    IngredientCategory,
    IngredientType,
)

NUTRITION_FIELDS = (
    "price",
    "glycemic_index",
    "calories",
    "carbohydrate",
    "sugar",
    "protein",
    "fat",
    "saturatedfat",
    "fiber",
    "cholesterol",
    "sodium",
    "potassium",
    "zinco",
    "calcium",
    "ferrum",
    "phosphorus",
    "vit_a",
    "vit_a_eq",
    "vit_a_beta",
    "vit_b1",
    "vit_b2",
    "vit_b3",
    "vit_b6",
    "vit_b9",
    "vit_c",
    "vit_d",
    "vit_e",
)


def _read_json(name: str) -> list[dict]:
    package = resources.files("ingredients").joinpath("data")
    return json.loads(package.joinpath(name).read_text(encoding="utf-8"))


def _dec(value):
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError):
        return None


def _provisional_en_name(slug: str) -> str:
    return slug.replace("-", " ").replace("_", " ").title()


def _names_and_slugs(row: dict) -> tuple[str, str, str, str]:
    """Return name_en, name_it, slug_en, slug_it.

    Catalog JSON ``slug`` is the English identity (default language).
    """
    slug_en = row.get("slug_en") or row["slug"]
    slug_it = row.get("slug_it") or slug_en
    name_en = row.get("name_en") or _provisional_en_name(slug_en)
    name_it = row.get("name_it") or name_en
    return name_en, name_it, slug_en, slug_it


def _find_by_catalog_slug(model, catalog_slug: str, slug_it: str | None = None):
    """Resolve by English catalog slug first, then Italian, then bare slug."""
    qs = model.objects.all()
    if hasattr(model, "slug_en"):
        obj = qs.filter(slug_en=catalog_slug).first()
        if obj is not None:
            return obj
    obj = qs.filter(slug=catalog_slug).first()
    if obj is not None:
        return obj
    if slug_it and hasattr(model, "slug_it"):
        obj = qs.filter(slug_it=slug_it).first()
        if obj is not None:
            return obj
    if hasattr(model, "slug_it"):
        obj = qs.filter(slug_it=catalog_slug).first()
        if obj is not None:
            return obj
    return None


def _apply_i18n(
    obj,
    name_en,
    name_it,
    slug_en,
    slug_it,
    description_en="",
    description_it="",
):
    obj.name = name_en
    obj.slug = slug_en
    if hasattr(obj, "name_en"):
        obj.name_en = name_en
    if hasattr(obj, "name_it"):
        obj.name_it = name_it
    if hasattr(obj, "slug_en"):
        obj.slug_en = slug_en
    if hasattr(obj, "slug_it"):
        obj.slug_it = slug_it
    if hasattr(obj, "description_en"):
        obj.description_en = description_en or ""
    if hasattr(obj, "description_it"):
        obj.description_it = description_it or ""
    if hasattr(obj, "description") and description_en is not None:
        obj.description = description_en or description_it or ""


def _attach_image(obj, relative: str | None, folder, name: str) -> bool:
    if not relative or obj.image_id or folder is None:
        return False
    image = ensure_image_from_package(
        package="ingredients",
        relative=f"images/{relative}"
        if not relative.startswith("images/")
        else relative,
        folder=folder,
        name=name,
    )
    if image is None:
        return False
    obj.image = image
    return True


class Command(BaseCommand):
    help = (
        "Load ingredient types, categories, ingredients and allergen presence "
        "idempotently by English catalog slug. Ensures allergen catalog and "
        "Filer folders/images are seeded."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-allergens",
            action="store_true",
            help="Do not call load_allergen_catalog first.",
        )
        parser.add_argument(
            "--skip-images",
            action="store_true",
            help="Do not import package Filer images.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if not options["skip_allergens"]:
            call_command(
                "load_allergen_catalog",
                skip_images=options["skip_images"],
            )

        self._skip_images = options["skip_images"]
        self._folders = {}
        if not self._skip_images:
            self._folders["type"] = ensure_folder("ingredient-type")
            self._folders["category"] = ensure_folder("ingredient-category")
            self._folders["ingredient"] = ensure_folder("ingredient")

        type_counts = self._load_types()
        cat_counts = self._load_categories()
        ing_counts = self._load_ingredients()
        presence_counts = self._load_presence()

        self.stdout.write(
            self.style.SUCCESS(
                "Ingredient catalog: "
                f"types {type_counts}, categories {cat_counts}, "
                f"ingredients {ing_counts}, presence {presence_counts}."
            )
        )

    def _load_types(self):
        created = updated = images = 0
        folder = self._folders.get("type")
        for row in _read_json("types.json"):
            name_en, name_it, slug_en, slug_it = _names_and_slugs(row)
            obj = _find_by_catalog_slug(IngredientType, slug_en, slug_it)
            was_created = obj is None
            if was_created:
                obj = IngredientType(slug=slug_en, name=name_en)
            _apply_i18n(obj, name_en, name_it, slug_en, slug_it)
            if _attach_image(obj, row.get("image"), folder, name_en):
                images += 1
            obj.save()
            created += int(was_created)
            updated += int(not was_created)
        return f"{created}/{updated}/img:{images}"

    def _load_categories(self):
        created = updated = images = 0
        folder = self._folders.get("category")
        for row in _read_json("categories.json"):
            itype = _find_by_catalog_slug(IngredientType, row["type_slug"])
            if itype is None:
                raise IngredientType.DoesNotExist(
                    f"IngredientType catalog slug={row['type_slug']!r} missing"
                )
            name_en, name_it, slug_en, slug_it = _names_and_slugs(row)
            description_en = row.get("description_en") or ""
            description_it = row.get("description_it") or ""
            obj = _find_by_catalog_slug(IngredientCategory, slug_en, slug_it)
            was_created = obj is None
            if was_created:
                obj = IngredientCategory(
                    slug=slug_en,
                    name=name_en,
                    type=itype,
                    description=description_en or description_it,
                )
            else:
                obj.type = itype
            _apply_i18n(
                obj,
                name_en,
                name_it,
                slug_en,
                slug_it,
                description_en,
                description_it,
            )
            if _attach_image(obj, row.get("image"), folder, name_en):
                images += 1
            obj.save()
            created += int(was_created)
            updated += int(not was_created)
        return f"{created}/{updated}/img:{images}"

    def _load_ingredients(self):
        created = updated = images = 0
        root = self._folders.get("ingredient")
        for row in _read_json("ingredients.json"):
            category = _find_by_catalog_slug(
                IngredientCategory, row["category_slug"]
            )
            if category is None:
                raise IngredientCategory.DoesNotExist(
                    f"IngredientCategory catalog slug={row['category_slug']!r} missing"
                )
            name_en, name_it, slug_en, slug_it = _names_and_slugs(row)
            defaults_extra = {
                "category": category,
                "fodmap": row.get("fodmap") or "unknown",
            }
            for field in NUTRITION_FIELDS:
                if field == "glycemic_index":
                    defaults_extra[field] = int(row.get(field) or 0)
                elif field == "price":
                    defaults_extra[field] = _dec(row.get(field)) or Decimal("0")
                else:
                    defaults_extra[field] = _dec(row.get(field))
            obj = _find_by_catalog_slug(Ingredient, slug_en, slug_it)
            was_created = obj is None
            if was_created:
                obj = Ingredient(slug=slug_en, name=name_en, **defaults_extra)
            else:
                for key, value in defaults_extra.items():
                    setattr(obj, key, value)
            _apply_i18n(obj, name_en, name_it, slug_en, slug_it)
            folder = root
            if root is not None:
                folder = ensure_folder(category.slug_en or category.slug, parent=root)
            if _attach_image(obj, row.get("image"), folder, name_en):
                images += 1
            obj.save()
            created += int(was_created)
            updated += int(not was_created)
        return f"{created}/{updated}/img:{images}"

    def _load_presence(self):
        created = updated = 0
        for row in _read_json("presence.json"):
            ingredient = _find_by_catalog_slug(
                Ingredient, row["ingredient_slug"]
            )
            if ingredient is None:
                raise Ingredient.DoesNotExist(
                    f"Ingredient catalog slug={row['ingredient_slug']!r} missing"
                )
            allergen_slug = row["allergen_slug"]
            allergen = Allergen.objects.filter(slug=allergen_slug).first()
            if allergen is None and hasattr(Allergen, "slug_en"):
                allergen = Allergen.objects.filter(slug_en=allergen_slug).first()
            if allergen is None:
                raise Allergen.DoesNotExist(
                    f"Allergen catalog slug={allergen_slug!r} missing"
                )
            obj, was_created = IngredientAllergenPresence.objects.update_or_create(
                ingredient=ingredient,
                allergen=allergen,
                defaults={
                    "present": bool(row.get("present")),
                    "may_be_present": bool(row.get("may_be_present")),
                    "quantity": row.get("quantity") or "free",
                },
            )
            created += int(was_created)
            updated += int(not was_created)
        return f"{created}/{updated}"
