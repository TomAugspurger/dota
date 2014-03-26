# -*- coding: utf-8 -*-

import os
import re
import json
import pathlib

from lxml import html

from dota import api
from dota.helpers import cached_games


def fetch_new_match_ids(match_ids_path):
    """
    Get new match ids from datdota.

    Parameters
    ----------

    id_store : path to text file with matches already cached.

    Returns
    -------

    new_ids : [str]

    Notes
    -----

    id_store should be like '578918710\n'
    """
    url = "http://www.datdota.com/matches.php"
    r = html.parse(url).getroot()

    reg = re.compile(r'match.*(\d{9})$')
    links = filter(lambda x: reg.match(x[2]), r.iterlinks())

    with match_ids_path.open() as f:
        old_ids = f.readlines()

    ids = (x[2].split('?q=')[-1] + '\n' for x in links)
    new_ids = [x for x in ids if x not in old_ids]
    ids = 1
    return new_ids


def get_new_details(match_ids, data_path):

    with open(os.path.expanduser('~/') + 'Dropbox/bin/api-keys.txt') as f:
        key = json.load(f)['steam']

    h = api.API(key=key)

    cached = cached_games(data_path)
    new_matches = [x for x in match_ids if int(x) not in cached]
    details = {mid: h.get_match_details(mid) for mid in new_matches}
    return details


def write_new_details(details, data_path):

    if not data_path.exists():
        data_path.mkdir()

    for k in details:
        with (data_path / (str(k) + '.json')).open('w') as f:
            json.dump(details[k].resp, f)


def get_pro_matches(id_store='pro_match_ids.txt',
                    data_path='~/sandbox/dota/data/pro/'):
    """
    Find new match ids

    Parameters
    ----------

    id_store : str
    data_path : str
    """
    id_store = pathlib.Path(id_store)
    data_path = pathlib.Path(os.path.expanduser(data_path))
    match_ids_path = data_path / id_store

    new_ids = fetch_new_match_ids(match_ids_path)

    print("New matches found: {}".format(new_ids))
    #--------------------------------------------------------------------------
    # Write new ids and update match_ids by reading
    with match_ids_path.open('a+') as f:
        f.writelines(new_ids)

    with match_ids_path.open() as f:
        match_ids = [x.strip() for x in f.readlines()]

    #--------------------------------------------------------------------------
    # Get Match Details for new matches
    details = get_new_details(match_ids, data_path)
    write_new_details(details, data_path)

    #--------------------------------------------------------------------------
    # Insert into pro.db
    from examples.sqlalchemyORM import update_db

    update_db(data_path)

    print("Added {}".format(new_ids))


if __name__ == '__main__':
    # TODO: add argparser for id_store and data_path
    get_pro_matches()
