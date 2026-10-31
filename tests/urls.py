"""Test URLConf for django-ingredients (i18n_patterns + package urls)."""

from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += i18n_patterns(
    path(
        "jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"
    ),
    path("", include("ingredients.urls")),
)
