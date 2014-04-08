# -*- coding: utf-8 -*-
import re
import pathlib
try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO


def cached_games(directory, regex=r"[\w\/]*?(\d+)\.json",
                 full_path=True):
    """
    Return the match ids of all games.

    Parameters
    ----------
    directory : str or pathlib.Path
    regex : str. Alternative regex. Used to match games

    Returns
    -------

    list of strs

    """
    if not isinstance(directory, (pathlib.Path, pathlib.PosixPath,
                                  pathlib.WindowsPath)):
        directory = pathlib.Path(directory)

    regex = re.compile(regex)
    match_ids = filter(lambda x: regex.match(str(x)), directory.iterdir())
    if not full_path:
        match_ids = (int(regex.match(str(x)).groups()[0]) for x in match_ids)
    return match_ids


def open_or_stringIO(f, as_string=False):
    """
    Useful for testing, but not sure how good it actually is.
    """
    try:
        p = pathlib.Path(f)
        if p.exists() and not as_string:
            return open(f)
        else:
            return StringIO(f)
    except OSError:
        return StringIO(f)
