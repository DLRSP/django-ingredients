# Usage

```python
from ingredients.models import Ingredient

item = Ingredient.objects.get(slug="alchermes")
print(item.name_en, item.name_it)
```

URL path prefixes translate via gettext:

- English: `/en/ingredients/...`
- Italian: `/it/ingredienti/...`
