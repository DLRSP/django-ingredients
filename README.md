# django-ingredients

[![CI](https://github.com/DLRSP/django-ingredients/actions/workflows/ci.yaml/badge.svg)](https://github.com/DLRSP/django-ingredients/actions/workflows/ci.yaml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docs](https://img.shields.io/badge/docs-github.io-blue)](https://dlrsp.github.io/django-ingredients/)

Reusable food **ingredient catalog** for Django sites: types, categories,
nutrition fields, allergen presence links, and catalog images.

## Why use it

- Ship a ready catalog of ingredients with English + Italian names and slugs
- Attach nutrition values and allergen presence without building your own taxonomy
- Seed Filer images and data with one management command
- Keep public routes multilingual via modeltranslation and translated URL prefixes

## Requirements

- Python 3.10+
- Django 4.2+
- django-allergens
- django-filer (+ mptt, easy-thumbnails, polymorphic)
- django-modeltranslation

## Install

```shell
pip install django-ingredients
```

```python
INSTALLED_APPS = [
    "modeltranslation",
    # ...
    "easy_thumbnails",
    "filer",
    "mptt",
    "polymorphic",
    "allergens",
    "ingredients",
]
```

```shell
python manage.py migrate
python manage.py load_ingredient_catalog
```

Include `ingredients.urls` inside `i18n_patterns` for translated path prefixes
(for example `ingredienti/` in Italian).

## License

MIT
