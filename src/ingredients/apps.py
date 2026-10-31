from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class IngredientsConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "ingredients"
    verbose_name = _("Ingredients")
