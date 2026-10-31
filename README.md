# django-ingredients

[![CI](https://github.com/DLRSP/django-ingredients/actions/workflows/ci.yaml/badge.svg)](https://github.com/DLRSP/django-ingredients/actions/workflows/ci.yaml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Food ingredient catalog for Django: types, categories, nutrition fields,
allergen presence (via `django-allergens`), Filer images, and an idempotent
seed loader.

## Requirements

- Python 3.10+
- Django 4.2+
- django-allergens
- django-filer
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
    "allergens",
    "ingredients",
]
```

```shell
python manage.py migrate
python manage.py load_ingredient_catalog
```

`load_ingredient_catalog` loads allergens first, then types, categories,
ingredients and presence rows (idempotent by slug).

## License

MIT
