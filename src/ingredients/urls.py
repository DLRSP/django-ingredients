"""URL patterns for django-ingredients (translated path prefixes)."""

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import path
from django.utils.translation import gettext_lazy as _

from ingredients.models import Ingredient, IngredientCategory, IngredientType


def ingredient_list(request):
    names = ", ".join(
        Ingredient.objects.order_by("name").values_list("name", flat=True)[:50]
    )
    return HttpResponse(names or "ingredients")


def type_detail(request, slug_type):
    obj = get_object_or_404(IngredientType, slug=slug_type)
    return HttpResponse(obj.name)


def category_detail(request, slug_type, slug_cat):
    obj = get_object_or_404(
        IngredientCategory, slug=slug_cat, type__slug=slug_type
    )
    return HttpResponse(obj.name)


def ingredient_detail(request, slug_type, slug_cat, slug):
    obj = get_object_or_404(
        Ingredient,
        slug=slug,
        category__slug=slug_cat,
        category__type__slug=slug_type,
    )
    return HttpResponse(obj.name)


urlpatterns = [
    path(_("ingredients/"), ingredient_list, name="ingredients"),
    path(
        _("ingredients/<slug:slug_type>/"),
        type_detail,
        name="ingredients-type-detail",
    ),
    path(
        _("ingredients/<slug:slug_type>/<slug:slug_cat>/"),
        category_detail,
        name="ingredients-category-detail",
    ),
    path(
        _("ingredients/<slug:slug_type>/<slug:slug_cat>/<slug:slug>/"),
        ingredient_detail,
        name="ingredient-detail",
    ),
]
