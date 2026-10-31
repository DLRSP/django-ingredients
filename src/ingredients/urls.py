"""URL patterns for django-ingredients."""

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import path

from ingredients.models import Ingredient, IngredientCategory, IngredientType


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
    path(
        "ingredients/<slug:slug_type>/",
        type_detail,
        name="ingredients-type-detail",
    ),
    path(
        "ingredients/<slug:slug_type>/<slug:slug_cat>/",
        category_detail,
        name="ingredients-category-detail",
    ),
    path(
        "ingredients/<slug:slug_type>/<slug:slug_cat>/<slug:slug>/",
        ingredient_detail,
        name="ingredient-detail",
    ),
]
