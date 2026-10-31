"""Idempotent ingredient catalog loader (keyed by slug)."""

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


def _apply_translations(obj, row, fields):
    for field in fields:
        it_key = f"{field}_it"
        en_key = f"{field}_en"
        if hasattr(obj, f"{field}_it") and row.get(it_key) is not None:
            setattr(obj, f"{field}_it", row[it_key])
        if hasattr(obj, f"{field}_en") and row.get(en_key):
            setattr(obj, f"{field}_en", row[en_key])
        elif hasattr(obj, f"{field}_en") and field == "name" and row.get("name_it"):
            # Keep English empty placeholder when only Italian catalog exists.
            if not getattr(obj, f"{field}_en", None):
                setattr(obj, f"{field}_en", row.get("name_en") or "")


class Command(BaseCommand):
    help = (
        "Load ingredient types, categories, ingredients and allergen presence "
        "idempotently by slug. Ensures allergen catalog is loaded first."
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
            name = row.get("name_en") or row.get("name_it") or row["slug"]
            obj, was_created = IngredientType.objects.update_or_create(
                slug=row["slug"],
                defaults={"name": name},
            )
            _apply_translations(obj, row, ("name", "slug"))
            if hasattr(obj, "slug_it"):
                obj.slug_it = row["slug"]
            if hasattr(obj, "slug_en"):
                obj.slug_en = row["slug"]
            obj.save()
            created += int(was_created)
            updated += int(not was_created)
        return f"{created}/{updated}"

    def _load_categories(self):
        created = updated = 0
        for row in _read_json("categories.json"):
            itype = IngredientType.objects.get(slug=row["type_slug"])
            name = row.get("name_en") or row.get("name_it") or row["slug"]
            obj, was_created = IngredientCategory.objects.update_or_create(
                slug=row["slug"],
                defaults={
                    "name": name,
                    "description": row.get("description_en")
                    or row.get("description_it")
                    or "",
                    "type": itype,
                },
            )
            _apply_translations(obj, row, ("name", "slug", "description"))
            if hasattr(obj, "slug_it"):
                obj.slug_it = row["slug"]
            if hasattr(obj, "slug_en"):
                obj.slug_en = row["slug"]
            obj.save()
            created += int(was_created)
            updated += int(not was_created)
        return f"{created}/{updated}"

    def _load_ingredients(self):
        created = updated = 0
        for row in _read_json("ingredients.json"):
            category = IngredientCategory.objects.get(slug=row["category_slug"])
            name = row.get("name_en") or row.get("name_it") or row["slug"]
            defaults = {
                "name": name,
                "category": category,
                "fodmap": row.get("fodmap") or "unknown",
            }
            for field in NUTRITION_FIELDS:
                if field == "glycemic_index":
                    defaults[field] = int(row.get(field) or 0)
                elif field == "price":
                    defaults[field] = _dec(row.get(field)) or Decimal("0")
                else:
                    defaults[field] = _dec(row.get(field))
            obj, was_created = Ingredient.objects.update_or_create(
                slug=row["slug"],
                defaults=defaults,
            )
            _apply_translations(obj, row, ("name", "slug"))
            if hasattr(obj, "slug_it"):
                obj.slug_it = row["slug"]
            if hasattr(obj, "slug_en"):
                obj.slug_en = row["slug"]
            obj.save()
            created += int(was_created)
            updated += int(not was_created)
        return f"{created}/{updated}"

    def _load_presence(self):
        created = updated = 0
        for row in _read_json("presence.json"):
            ingredient = Ingredient.objects.get(slug=row["ingredient_slug"])
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
