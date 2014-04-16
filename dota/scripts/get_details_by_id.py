# -*- coding: utf-8 -*-
import json
import pathlib
import argparse

from dota import api
from dota.helpers import cached_games

parser = argparse.ArgumentParser("Get new matches by account ID.")
parser.add_argument("id", type=int, help="Steam ID. e.g.: 76561198102796812 "
                                         "or 76561198025007092.")
parser.add_argument("--key_path", type=str, help="Path to JSON file with steam"
                    " key.", default='~/Dropbox/bin/api-keys.txt')
parser.add_argument("--data_dir", type=str, help='Path to data directory.',
                    default='~/sandbox/dota/data/')


def argparser(args):
    steam_id = args.id
    key_path = pathlib.Path(pathlib.os.path.expanduser(args.key_path))
    data_dir = pathlib.Path(pathlib.os.path.expanduser(args.data_dir))
    return steam_id, key_path, data_dir


def get_details(steam_id, key, data_dir):
    """
    Take a steam_id and check for new games. Download details of any
    new games to data_dir. Primarily called from the command line.
    """
    cached = cached_games(data_dir)

    h = api.API(key)
    hr = h.get_match_history(account_id=steam_id)
    new_ids = set(hr.match_ids) - set((int(x.stem.strip('details')) for x in cached))

    if len(new_ids) == 0:
        print("No new matches for {}".format(steam_id))

    print("Fetching details on {} games".format(len(new_ids)))

    for id_ in new_ids:
        dr = h.get_match_details(id_)
        with (data_dir / (str(dr.match_id) + '.json')).open('w') as f:
            json.dump(dr.resp, f)
        print("Added {}.".format(id_))

if __name__ == '__main__':
    args = parser.parse_args()
    steam_id, key_path, data_dir = argparser(args)

    with key_path.open() as f:
        key = json.load(f)['steam']

    get_details(steam_id, key, data_dir)
