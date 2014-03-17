# -*- coding: utf-8 -*-

import re
import pathlib


def cached_games(directory, regex=r"[a-z/]*(\d*)\.json"):
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
    match_ids = [regex.match(str(x)).groups()[0] for x in match_ids]
    return match_ids
