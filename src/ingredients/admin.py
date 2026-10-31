from django.contrib import admin

from ingredients.models import (
    Ingredient,
    IngredientAllergenPresence,
    IngredientCategory,
    IngredientType,
)


class IngredientAllergenPresenceInline(admin.TabularInline):
    model = IngredientAllergenPresence
    extra = 0


@admin.register(IngredientType)
class IngredientTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug")


@admin.register(IngredientCategory)
class IngredientCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "type")
    list_filter = ("type",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "category", "fodmap", "price")
    list_filter = ("category__type", "fodmap")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug")
    inlines = [IngredientAllergenPresenceInline]


@admin.register(IngredientAllergenPresence)
class IngredientAllergenPresenceAdmin(admin.ModelAdmin):
    list_display = (
        "ingredient",
        "allergen",
        "present",
        "may_be_present",
        "quantity",
    )
    list_filter = ("present", "may_be_present", "quantity", "allergen")
    search_fields = ("ingredient__name", "allergen__name")
