"""Model and catalog loader tests for django-ingredients."""

from __future__ import annotations

from django.core.management import call_command
from django.db import connection
from django.test import TestCase
from django.urls import clear_url_caches, reverse, set_urlconf
from django.utils import translation

from ingredients.models import (
    Ingredient,
    IngredientAllergenPresence,
    IngredientCategory,
    IngredientType,
)


class IngredientModelTests(TestCase):
    def test_default_table_names(self):
        self.assertEqual(IngredientType._meta.db_table, "ingredients_ingredienttype")
        self.assertEqual(
            IngredientCategory._meta.db_table, "ingredients_ingredientcategory"
        )
        self.assertEqual(Ingredient._meta.db_table, "ingredients_ingredient")
        self.assertEqual(
            IngredientAllergenPresence._meta.db_table,
            "ingredients_ingredientallergenpresence",
        )

    def test_load_ingredient_catalog_idempotent(self):
        call_command("load_ingredient_catalog")
        types = IngredientType.objects.count()
        cats = IngredientCategory.objects.count()
        ings = Ingredient.objects.count()
        presence = IngredientAllergenPresence.objects.count()
        self.assertEqual(types, 8)
        self.assertEqual(cats, 31)
        self.assertEqual(ings, 505)
        self.assertEqual(presence, 185)

        call_command("load_ingredient_catalog")
        self.assertEqual(IngredientType.objects.count(), types)
        self.assertEqual(IngredientCategory.objects.count(), cats)
        self.assertEqual(Ingredient.objects.count(), ings)
        self.assertEqual(IngredientAllergenPresence.objects.count(), presence)

    def test_catalog_fills_en_and_it_fields(self):
        call_command("load_ingredient_catalog")
        eggs = IngredientType.objects.get(slug="uova")
        self.assertEqual(eggs.name_it, "Uova")
        self.assertEqual(eggs.name_en, "Eggs")
        self.assertTrue(eggs.slug_en)
        self.assertEqual(eggs.slug_it, "uova")
        sample = Ingredient.objects.first()
        self.assertTrue(sample.name_en)
        self.assertTrue(sample.name_it)
        self.assertTrue(sample.slug_en)
        self.assertTrue(sample.slug_it)

    def test_reverse_en_and_it_path_prefixes(self):
        call_command("load_ingredient_catalog")
        itype = IngredientType.objects.get(slug="uova")
        clear_url_caches()
        set_urlconf("tests.urls")
        with translation.override("en"):
            url_en = reverse(
                "ingredients-type-detail",
                kwargs={"slug_type": itype.slug_en},
            )
        with translation.override("it"):
            url_it = reverse(
                "ingredients-type-detail",
                kwargs={"slug_type": itype.slug_it},
            )
        self.assertIn("/ingredients/", url_en)
        self.assertIn("/ingredienti/", url_it)

    def test_presence_fk_points_at_allergens(self):
        call_command("load_ingredient_catalog")
        row = IngredientAllergenPresence.objects.select_related(
            "allergen", "ingredient"
        ).first()
        self.assertIsNotNone(row)
        self.assertEqual(row.allergen._meta.app_label, "allergens")
        self.assertTrue(row.allergen.slug)

    def test_filer_stack_importable(self):
        import easy_thumbnails  # noqa: F401
        import filer  # noqa: F401
        import mptt  # noqa: F401
        import polymorphic  # noqa: F401

        self.assertTrue(True)

    def test_no_legacy_recipes_tables(self):
        with connection.cursor() as cursor:
            tables = connection.introspection.table_names(cursor)
        self.assertIn("ingredients_ingredient", tables)
        self.assertNotIn("recipes_ingredient", tables)
