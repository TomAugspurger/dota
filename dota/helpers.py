# -*- coding: utf-8 -*-
import re
import pathlib
try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO

import pandas as pd


def cached_games(directory, regex=r"[\w\/]*?(\d+)\.json"):
    """
    Return the match ids of all games.

    Parameters
    ----------
    directory : str or pathlib.Path
    regex : str. Alternative regex. Used to match games

    Returns
    -------

    match_ids : iterable of Paths

    """
    if not isinstance(directory, (pathlib.Path, pathlib.PosixPath,
                                  pathlib.WindowsPath)):
        directory = pathlib.Path(directory)

    regex = re.compile(regex)
    match_ids = filter(lambda x: regex.match(str(x)), directory.iterdir())
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


def pb_team_id(df, order=0):
    return df.team_id_f.iloc[order]


def pb_opponent_id(df, order=0):
    """
    Get the opponent id from a pick / ban Frame.

    Parameters
    ----------
    df : DataFrame
        formatted like a pick / ban frame
    order : int
        pick / ban order (1 .. 19)

    Returns
    -------
    opponent_id : int
    """
    x = df['team_id_f'].unique()
    other_team = {x[0]: x[1], x[1]: x[0]}
    return df.team_id_f.map(other_team).iloc[order]


def pb_previous_pbs(df, order=0):
    """
    Get the hero id's for all prior picks and bans.

    Parameters
    ----------
    df : DataFrame
        formatted like a pick / ban frame
    order : int
        pick / ban order (1 .. 19)

    Returns
    -------
    prior_pbs : Series
        index labels are pick0, b0 ... or just order?
        values are hero_id_f
    """
    pbs = pd.DataFrame(df.hero_id_f.iloc[:order],
                       index=df.order.iloc[:order].values).T
    pbs = pbs.rename(columns=lambda x: 'pb_' + str(x))
    return pbs


def pb_only_complete_drafts(df):
    """
    Remove any matches where at least one team_id is NaN.
    """
    good_ids = (~pd.isnull(df['team_id'])).groupby(df['match_id']).all()
    good_ids = good_ids[good_ids].index
    return df.query('match_id in @good_ids')
