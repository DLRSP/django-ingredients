# Install

```shell
pip install django-ingredients
```

Until the sibling package is on PyPI, CI/install may use the GitHub source for
`django-allergens` (see `pyproject.toml`).

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
