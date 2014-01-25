dota
====

DOTA 2 stats stuff.

Example:

```python

>>> from dota import api

>>> steam_id = "76561198025007092"
>>> with open('.key') as f:
        key = f.readline().rstrip()

>>> con = api.API(key)
>>> history = con.get_match_history(steam_id=steam_id)
```
