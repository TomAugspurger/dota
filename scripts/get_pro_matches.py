# -*- coding: utf-8 -*-

import os
import re
import json
import pathlib

from lxml import html

from dota import api
from dota.helpers import cached_games

def get_pro_matches():
    # Find new match ids
    url = "http://www.datdota.com/matches.php"
    r = html.parse(url).getroot()

    reg = re.compile(r'match.*(\d{9})$')
    links = filter(lambda x: reg.match(x[2]), r.iterlinks())

    here = pathlib.Path(__file__).parent.absolute()
    match_ids_path = here.parent / 'data/pro/pro_match_ids.txt'

    with match_ids_path.open() as f:
        old_ids = f.readlines()

    ids = (x[2].split('?q=')[-1] + '\n' for x in links)
    new_ids = [x for x in ids if x not in old_ids]

    with match_ids_path.open('a+') as f:
        f.writelines(new_ids)

    #--------------------------------------------------------------------------
    # Get Match Details for new matches
    with open(os.path.expanduser('~/') + 'Dropbox/bin/api-keys.txt') as f:
        key = json.load(f)['steam']

    h = api.API(key=key)

    with match_ids_path.open() as f:
        match_ids = [x.strip() for x in f.readlines()]

    f = pathlib.Path(__file__).absolute()
    data_path = f.parent.joinpath(pathlib.Path('data/pro'))

    matches = filter(None, map(lambda x: re.match(r'.*(\d{9}).json$', x),
                               os.listdir(str(data_path))))
    matches = [x.groups()[0] for x in matches]
    new_matches = [x for x in match_ids if x not in matches]
    details = {mid: h.get_match_details(mid) for mid in new_matches}

    if not data_path.exists():
        data_path.mkdir()

    for k in details:
        with (data_path / (str(k) + '.json')).open('w') as f:
            json.dump(details[k].resp, f)

    #--------------------------------------------------------------------------
    # Insert into pro.db
    from examples.sqlalchemyORM import update_db

    update_db(data_path)

    print("Added {}".format(new_ids))


if __name__ == '__main__':
    get_pro_matches()
