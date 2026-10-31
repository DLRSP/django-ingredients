from django.utils.translation import gettext_lazy as _

ALLERGEN_QUANTITY = (
    ("free", _("Free")),
    ("low", _("Low")),
    ("medium", _("Medium")),
    ("high", _("High")),
)

INGREDIENT_FODMAP = (
    ("unknown", _("Unknown")),
    ("suggested", _("Suggested")),
    ("moderate", _("Moderate")),
    ("not-suggested", _("Not suggested")),
)
