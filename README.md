# django-ingredients

[![CI](https://github.com/DLRSP/django-ingredients/actions/workflows/ci.yaml/badge.svg)](https://github.com/DLRSP/django-ingredients/actions/workflows/ci.yaml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docs](https://img.shields.io/badge/docs-github.io-blue)](https://dlrsp.github.io/django-ingredients/)

Food ingredient catalog for Django: types, categories, nutrition fields,
allergen presence (via `django-allergens`), Filer images, and an idempotent
seed loader.

Default language is **English**. Italian names come from the historical catalog;
`name_en` uses known English labels where available, otherwise a Title-Case of
the ASCII slug (provisional English — refine over time).

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

`load_ingredient_catalog` loads allergens first, then types, categories,
ingredients, and allergen presence. Include `ingredients.urls` inside
`i18n_patterns` for translated prefixes (`ingredienti/` in Italian).

## License

MIT
