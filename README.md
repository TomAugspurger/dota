DOTA Stats
==========

A library for fetching, processing, and analysis DOTA 2 statistics.

Installation
============

Via [`pip`](https://pypi.python.org/pypi/dota/0.2.0) with `pip install dota` or clone the source and `python setup.py install`.

Dependencies
------------

- numpy
- pandas
- arrow
- requests
- lxml
- sqlalchemy

Finally, you'll need a [Steam API key](http://steamcommunity.com/dev). See the [dev forums](http://dev.dota2.com/forumdisplay.php?f=411) for documentation on the DOTA 2 web API.

Example:

```python

>>> from dota import api

>>> steam_id = "76561198025007092"
>>> with open('.key') as f:
        key = f.readline().rstrip()

>>> con = api.API(key)
>>> history = con.get_match_history(steam_id=steam_id)
```
