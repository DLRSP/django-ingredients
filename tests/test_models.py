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
        eggs = IngredientType.objects.get(slug="eggs")
        self.assertEqual(eggs.name_it, "Uova")
        self.assertEqual(eggs.name_en, "Eggs")
        self.assertEqual(eggs.slug_en, "eggs")
        self.assertEqual(eggs.slug_it, "uova")
        red = IngredientCategory.objects.get(slug="red-meats")
        self.assertEqual(red.name_en, "Red meats")
        self.assertEqual(red.name_it, "Carni rosse")
        self.assertEqual(red.slug_it, "carni-rosse")
        sample = Ingredient.objects.get(slug_it="uova")
        self.assertEqual(sample.slug_en, "eggs")
        self.assertEqual(sample.name_en, "Eggs")
        self.assertTrue(sample.name_it)
        self.assertTrue(eggs.image_id)
        self.assertTrue(red.image_id)
        self.assertTrue(sample.image_id)

    def test_catalog_english_slugs_are_canonical(self):
        call_command("load_ingredient_catalog")
        for itype in IngredientType.objects.all():
            self.assertEqual(itype.slug, itype.slug_en)
        for cat in IngredientCategory.objects.all():
            self.assertEqual(cat.slug, cat.slug_en)
            self.assertEqual(cat.type.slug, cat.type.slug_en)
        for ing in Ingredient.objects.all()[:50]:
            self.assertEqual(ing.slug, ing.slug_en)
            self.assertEqual(ing.category.slug, ing.category.slug_en)

    def test_reverse_en_and_it_path_prefixes(self):
        call_command("load_ingredient_catalog")
        itype = IngredientType.objects.get(slug="eggs")
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

    def test_presence_uses_english_catalog_keys(self):
        call_command("load_ingredient_catalog")
        row = IngredientAllergenPresence.objects.select_related(
            "allergen", "ingredient"
        ).get(ingredient__slug="eggs", allergen__slug="egg")
        self.assertEqual(row.allergen._meta.app_label, "allergens")
        self.assertEqual(row.ingredient.slug_en, "eggs")
        self.assertEqual(row.allergen.slug_en, "egg")

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
