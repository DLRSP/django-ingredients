from modeltranslation.translator import TranslationOptions, register

from ingredients.models import Ingredient, IngredientCategory, IngredientType


@register(IngredientType)
class IngredientTypeTranslationOptions(TranslationOptions):
    fields = ("name", "slug")


@register(IngredientCategory)
class IngredientCategoryTranslationOptions(TranslationOptions):
    fields = ("name", "slug", "description")


@register(Ingredient)
class IngredientTranslationOptions(TranslationOptions):
    fields = ("name", "slug")
