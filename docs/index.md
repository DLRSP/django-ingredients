# django-ingredients

Template repository for a **reusable Django app** published on PyPI. After you clone and rename, replace the placeholder import package `ingredients` and the distribution name `django-ingredients` across the tree (see the checklist in `README.md`).

---

## Requirements

- Python 3.10+
- Django 3.2+ (see `pyproject.toml` for declared compatibility)

---

## Installation

```shell
pip install django-ingredients
```

Add the app to `INSTALLED_APPS` using your real module name (after renaming from `ingredients`):

```python
INSTALLED_APPS = [
    # ...
    "ingredients",
    # ...
]
```

---

## Documentation

Full docs are built with [MkDocs](https://www.mkdocs.org/) (Material theme). From the repo root:

```shell
pip install -e ".[docs]"
mkdocs serve
```
