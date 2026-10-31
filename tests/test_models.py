"""Model and catalog loader tests for django-ingredients."""

from __future__ import annotations

from django.core.management import call_command
from django.db import connection
from django.test import TestCase

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

    def test_presence_fk_points_at_allergens(self):
        call_command("load_ingredient_catalog")
        row = IngredientAllergenPresence.objects.select_related(
            "allergen", "ingredient"
        ).first()
        self.assertIsNotNone(row)
        self.assertEqual(row.allergen._meta.app_label, "allergens")
        self.assertTrue(row.allergen.slug)

    def test_no_legacy_recipes_tables(self):
        with connection.cursor() as cursor:
            tables = connection.introspection.table_names(cursor)
        self.assertIn("ingredients_ingredient", tables)
        self.assertNotIn("recipes_ingredient", tables)
