# -*- coding: utf-8 -*-
import re
from os.path import dirname
from pathlib import Path, PosixPath, WindowsPath
try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO

import requests

import dota.api


def cached_games(directory, regex=r"[\w\/]*?(\d+)\.json"):
    """
    Return the match ids of all games.

    Parameters
    ----------
    directory : str or Path
    regex : str. Alternative regex. Used to match games

    Returns
    -------

    list of strs

    """
    if not isinstance(directory, (Path, PosixPath, WindowsPath)):
        directory = Path(directory)

    regex = re.compile(regex)
    match_ids = filter(lambda x: regex.match(str(x)), directory.iterdir())
    match_ids = [int(regex.match(str(x)).groups()[0]) for x in match_ids]
    return match_ids


def open_or_stringIO(f, as_string=False):
    """
    Useful for testing, but not sure how good it actually is.
    """
    try:
        p = Path(f)
        if p.exists() and not as_string:
            return open(f)
        else:
            return StringIO(f)
    except OSError:
        return StringIO(f)


def load_resource(name, kind, size='lg'):
    """
    Check /resources/kind/name for an image. If it exists return that image.
    Use with IPython.display.Image()

    Parameters:
    name : str or int
    kind : str
        one of {'hero', 'item'}

    Returns:

    handel : _io.TextIOWrapper
        handle to file
    """
    # construct path
    name_ = _format_resource_name(name, kind, size)
    resource_dir = Path(dirname(dota.__file__) + '/resources')
    cachefile = resource_dir / Path(kind + '/' + name_)

    if not cachefile.parent.exists():
        cachefile.parent.mkdir(parents=True)

    # optionally fetch and store
    if not cachefile.exists():
        r = _fetch_resource(name_, kind)

        if r.ok:
            with cachefile.open('wb') as f:
                for chunk in r.iter_content():
                    f.write(chunk)
        else:
            msg = "{} is not cached and could not fetch from Valve".format(name)
            raise ValueError(msg)

    return cachefile.open('rb')


def _format_resource_name(name, kind, size):
    if isinstance(name, int):
        name_ = getattr(dota.api, '_' + kind + '_id_to_name')[name].strip(kind)
    else:
        name_ = name

    if not name_ in getattr(dota.api, '_' + kind + '_name_to_id').keys():
        raise KeyError("Unrecognized name {}".format(name))

    if size == 'full':
        ext = 'jpg'
    else:
        ext = 'png'

    name_ = "{}_{}.{}".format(name_, size, ext)

    return name_


def _fetch_resource(name_, kind):
    url = "http://cdn.dota2.com/apps/dota2/images/{}s/{}".format(kind, name_)
    r = requests.get(url, stream=True)
    return r
