import json
import pathlib
import argparse

from dota import api
from dota.helpers import cached_games

parser = argparse.ArgumentParser("Get new matches by account ID.")
parser.add_argument("id", type=int, help="Steam ID")
parser.add_argument("--key_path", type=str, help="Path to JSON file with steam"
                    " key.", default='~/Dropbox/bin/api-keys.txt')
parser.add_argument("--data_dir", type=str, help='Path to data directory.',
                    default='~/sandbox/dota/data/')


if __name__ == '__main__':
    args = parser.parse_args()
    steam_id = args.id
    key_path = pathlib.Path(pathlib.os.path.expanduser(args.key_path))
    data_dir = pathlib.Path(pathlib.os.path.expanduser(args.data_dir))

    with key_path.open() as f:
        key = json.load(f)['steam']

    cached = cached_games(data_dir)

    h = api.API(key)
    hr = h.get_match_history(account_id=steam_id)
    new_ids = set(hr.match_ids) - set(cached)

    for id_ in new_ids:
        dr = h.get_match_details(id_)
        with (data_dir / (str(dr.match_id) + '.json')).open('w') as f:
            json.dump(dr.resp, f)
        print("Added {}.".format(id_))