"""Idempotent ingredient catalog loader (keyed by catalog slug)."""

from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from importlib import resources

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

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

    Catalog JSON ``slug`` is the Italian identity; English defaults to that
    slug when no ``slug_en`` is provided.
    """
    slug_it = row.get("slug_it") or row["slug"]
    slug_en = row.get("slug_en") or slug_it
    name_it = row.get("name_it") or slug_it
    name_en = row.get("name_en") or _provisional_en_name(slug_en)
    return name_en, name_it, slug_en, slug_it


def _find_by_catalog_slug(model, catalog_slug: str, slug_en: str | None = None):
    """Resolve a row by Italian catalog slug (or English) under modeltranslation."""
    qs = model.objects.all()
    if hasattr(model, "slug_it"):
        obj = qs.filter(slug_it=catalog_slug).first()
        if obj is not None:
            return obj
    if slug_en and hasattr(model, "slug_en"):
        obj = qs.filter(slug_en=slug_en).first()
        if obj is not None:
            return obj
    return qs.filter(slug=catalog_slug).first()


def _apply_i18n(
    obj,
    name_en,
    name_it,
    slug_en,
    slug_it,
    description_en="",
    description_it="",
):
    # Default language is English: write identity onto slug/name first.
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


class Command(BaseCommand):
    help = (
        "Load ingredient types, categories, ingredients and allergen presence "
        "idempotently by catalog slug. Ensures allergen catalog is loaded first."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-allergens",
            action="store_true",
            help="Do not call load_allergen_catalog first.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if not options["skip_allergens"]:
            call_command("load_allergen_catalog")

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
        created = updated = 0
        for row in _read_json("types.json"):
            name_en, name_it, slug_en, slug_it = _names_and_slugs(row)
            obj = _find_by_catalog_slug(IngredientType, row["slug"], slug_en)
            was_created = obj is None
            if was_created:
                obj = IngredientType(slug=slug_en, name=name_en)
            _apply_i18n(obj, name_en, name_it, slug_en, slug_it)
            obj.save()
            created += int(was_created)
            updated += int(not was_created)
        return f"{created}/{updated}"

    def _load_categories(self):
        created = updated = 0
        for row in _read_json("categories.json"):
            itype = _find_by_catalog_slug(IngredientType, row["type_slug"])
            if itype is None:
                raise IngredientType.DoesNotExist(
                    f"IngredientType catalog slug={row['type_slug']!r} missing"
                )
            name_en, name_it, slug_en, slug_it = _names_and_slugs(row)
            description_en = row.get("description_en") or ""
            description_it = row.get("description_it") or ""
            obj = _find_by_catalog_slug(IngredientCategory, row["slug"], slug_en)
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
            obj.save()
            created += int(was_created)
            updated += int(not was_created)
        return f"{created}/{updated}"

    def _load_ingredients(self):
        created = updated = 0
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
            obj = _find_by_catalog_slug(Ingredient, row["slug"], slug_en)
            was_created = obj is None
            if was_created:
                obj = Ingredient(slug=slug_en, name=name_en, **defaults_extra)
            else:
                for key, value in defaults_extra.items():
                    setattr(obj, key, value)
            _apply_i18n(obj, name_en, name_it, slug_en, slug_it)
            obj.save()
            created += int(was_created)
            updated += int(not was_created)
        return f"{created}/{updated}"

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
            allergen = Allergen.objects.get(slug=row["allergen_slug"])
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
