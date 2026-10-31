from django.core.validators import MinValueValidator
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.translation import get_language, gettext_lazy as _
from filer.fields.image import FilerImageField

from ingredients.constants import ALLERGEN_QUANTITY, INGREDIENT_FODMAP

not_negative = MinValueValidator(0)


def _active_slug(obj, field="slug"):
    lang = (get_language() or "en").split("-")[0]
    value = getattr(obj, f"{field}_{lang}", None)
    return value or getattr(obj, field)


class IngredientType(models.Model):
    name = models.CharField(_("Name"), max_length=200)
    slug = models.SlugField(_("Slug"), unique=True)
    image = FilerImageField(
        verbose_name=_("Image"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ingredient_type_images",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = _("Ingredient type")
        verbose_name_plural = _("Ingredient types")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "ingredients-type-detail",
            kwargs={"slug_type": _active_slug(self)},
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class IngredientCategory(models.Model):
    name = models.CharField(_("Name"), max_length=200)
    slug = models.SlugField(_("Slug"), unique=True)
    description = models.CharField(_("Description"), max_length=200, blank=True)
    type = models.ForeignKey(
        IngredientType,
        verbose_name=_("Type"),
        on_delete=models.CASCADE,
        related_name="categories",
    )
    image = FilerImageField(
        verbose_name=_("Image"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ingredient_category_images",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = _("Ingredient category")
        verbose_name_plural = _("Ingredient categories")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "ingredients-category-detail",
            kwargs={
                "slug_type": _active_slug(self.type),
                "slug_cat": _active_slug(self),
            },
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class Ingredient(models.Model):
    name = models.CharField(_("Name"), max_length=200)
    slug = models.SlugField(_("Slug"), unique=True)
    category = models.ForeignKey(
        IngredientCategory,
        verbose_name=_("Category"),
        on_delete=models.CASCADE,
        related_name="ingredients",
    )
    allergens = models.ManyToManyField(
        "allergens.Allergen",
        blank=True,
        through="IngredientAllergenPresence",
        related_name="ingredients",
        verbose_name=_("Allergens"),
    )
    price = models.DecimalField(
        _("Price €/Kg"),
        max_digits=6,
        decimal_places=2,
        blank=True,
        default=0,
    )
    image = FilerImageField(
        verbose_name=_("Image"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ingredient_images",
    )
    glycemic_index = models.IntegerField(
        _("Glycemic index"), blank=True, default=0
    )
    fodmap = models.CharField(
        _("FODMAP"),
        choices=INGREDIENT_FODMAP,
        max_length=15,
        default="unknown",
        blank=True,
    )

    # Nutrition values are stored per kg (not per 100 g).
    calories = models.DecimalField(
        _("Calories"),
        blank=True,
        null=True,
        decimal_places=1,
        max_digits=6,
        validators=[not_negative],
    )
    carbohydrate = models.DecimalField(
        _("Carbohydrate"),
        blank=True,
        null=True,
        decimal_places=3,
        max_digits=6,
        validators=[not_negative],
    )
    sugar = models.DecimalField(
        _("Sugar"),
        blank=True,
        null=True,
        decimal_places=3,
        max_digits=6,
        validators=[not_negative],
    )
    protein = models.DecimalField(
        _("Protein"),
        blank=True,
        null=True,
        decimal_places=3,
        max_digits=6,
        validators=[not_negative],
    )
    fat = models.DecimalField(
        _("Fat"),
        blank=True,
        null=True,
        decimal_places=3,
        max_digits=6,
        validators=[not_negative],
    )
    saturatedfat = models.DecimalField(
        _("Saturated fat"),
        blank=True,
        null=True,
        decimal_places=3,
        max_digits=6,
        validators=[not_negative],
    )
    fiber = models.DecimalField(
        _("Fiber"),
        blank=True,
        null=True,
        decimal_places=3,
        max_digits=6,
        validators=[not_negative],
    )
    cholesterol = models.DecimalField(
        _("Cholesterol"),
        blank=True,
        null=True,
        decimal_places=0,
        max_digits=6,
        validators=[not_negative],
    )
    sodium = models.DecimalField(
        _("Sodium (Na)"),
        blank=True,
        null=True,
        decimal_places=0,
        max_digits=6,
        validators=[not_negative],
    )
    potassium = models.DecimalField(
        _("Potassium (K)"),
        blank=True,
        null=True,
        decimal_places=0,
        max_digits=6,
        validators=[not_negative],
    )
    zinco = models.DecimalField(
        _("Zinc (Zn)"),
        blank=True,
        null=True,
        decimal_places=0,
        max_digits=6,
        validators=[not_negative],
    )
    calcium = models.DecimalField(
        _("Calcium (Ca)"),
        blank=True,
        null=True,
        decimal_places=0,
        max_digits=6,
        validators=[not_negative],
    )
    ferrum = models.DecimalField(
        _("Iron (Fe)"),
        blank=True,
        null=True,
        decimal_places=0,
        max_digits=6,
        validators=[not_negative],
    )
    phosphorus = models.DecimalField(
        _("Phosphorus (P)"),
        blank=True,
        null=True,
        decimal_places=0,
        max_digits=6,
        validators=[not_negative],
    )
    vit_a = models.DecimalField(
        _("Vitamin A (retinol)"),
        blank=True,
        null=True,
        decimal_places=0,
        max_digits=6,
        validators=[not_negative],
    )
    vit_a_eq = models.DecimalField(
        _("Retinol equivalents"),
        blank=True,
        null=True,
        decimal_places=0,
        max_digits=6,
        validators=[not_negative],
    )
    vit_a_beta = models.DecimalField(
        _("Beta-carotene"),
        blank=True,
        null=True,
        decimal_places=0,
        max_digits=6,
        validators=[not_negative],
    )
    vit_b1 = models.DecimalField(
        _("Vitamin B1 (thiamine)"),
        blank=True,
        null=True,
        decimal_places=0,
        max_digits=6,
        validators=[not_negative],
    )
    vit_b2 = models.DecimalField(
        _("Vitamin B2 (riboflavin)"),
        blank=True,
        null=True,
        decimal_places=0,
        max_digits=6,
        validators=[not_negative],
    )
    vit_b3 = models.DecimalField(
        _("Vitamin B3 (niacin)"),
        blank=True,
        null=True,
        decimal_places=0,
        max_digits=6,
        validators=[not_negative],
    )
    vit_b6 = models.DecimalField(
        _("Vitamin B6 (pyridoxine)"),
        blank=True,
        null=True,
        decimal_places=0,
        max_digits=6,
        validators=[not_negative],
    )
    vit_b9 = models.DecimalField(
        _("Vitamin B9 (folic acid)"),
        blank=True,
        null=True,
        decimal_places=0,
        max_digits=6,
        validators=[not_negative],
    )
    vit_c = models.DecimalField(
        _("Vitamin C (ascorbic acid)"),
        blank=True,
        null=True,
        decimal_places=0,
        max_digits=6,
        validators=[not_negative],
    )
    vit_d = models.DecimalField(
        _("Vitamin D (cholecalciferol)"),
        blank=True,
        null=True,
        decimal_places=0,
        max_digits=6,
        validators=[not_negative],
    )
    vit_e = models.DecimalField(
        _("Vitamin E (tocopherol)"),
        blank=True,
        null=True,
        decimal_places=0,
        max_digits=6,
        validators=[not_negative],
    )

    class Meta:
        ordering = ["name"]
        verbose_name = _("Ingredient")
        verbose_name_plural = _("Ingredients")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "ingredient-detail",
            kwargs={
                "slug_type": _active_slug(self.category.type),
                "slug_cat": _active_slug(self.category),
                "slug": _active_slug(self),
            },
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class IngredientAllergenPresence(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name=_("Ingredient"),
        on_delete=models.CASCADE,
        related_name="allergen_presence",
    )
    allergen = models.ForeignKey(
        "allergens.Allergen",
        verbose_name=_("Allergen"),
        on_delete=models.CASCADE,
        related_name="ingredient_presence",
    )
    present = models.BooleanField(_("Present"), default=False)
    may_be_present = models.BooleanField(_("May be present"), default=False)
    quantity = models.CharField(
        _("Quantity level"),
        choices=ALLERGEN_QUANTITY,
        max_length=6,
        default="free",
        blank=True,
    )

    class Meta:
        verbose_name = _("Ingredient allergen presence")
        verbose_name_plural = _("Ingredient allergen presence")
        unique_together = [("ingredient", "allergen")]

    def __str__(self):
        return f"{self.ingredient} / {self.allergen}"
