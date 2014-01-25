import itertools as it

import json
import requests
import pandas as pd
import numpy as np


def get_players(m):
    """
    m : match
    """
    try:
        return list(set([x['account_id'] for x in m['players']]))
    except:
        return [np.nan]


def flatten(iterable):
    return it.chain.from_iterable(iterable)


def get_history(steam_id):
    r = requests.get(HISTORY_URL.format(key=KEY, steam_id=steam_id))
    return r.json()['result']

# MYSTEAMID = "76561198025007092"
# LAST_MATCH_ID = "478948089"
#-----------------------------------------------------------------------------

class API:
    """
    The network side of things.


    Parameters
    ----------
    key: value API key

    Returns
    -------
    api: API

    Notes
    -----
    Call specific keyword args should go into their respective functions.
    """
    HISTORY_URL = "https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/V001/"
    MATCH_URL = "https://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/V001/"

    def __init__(self, key):
        self.key = key

    def get_match_history(self, **kwargs):
        kwargs['key'] = self.key
        r = requests.get(self.HISTORY_URL, params=kwargs)
        return r.json()['result']

    def get_match_details(self, match_id, **kwargs):
        kwargs['key'] = self.key
        kwargs['match_id'] = match_id
        r = requests.get(self.MATCH_URL, params=kwargs)
        return r.json()['result']

    def get_heros(self):
        url = "https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v0001/"
        r = requests.get(url, params={'key': self.key})
        return r.json()['result']

    def get_player_summaries(self):
        pass

    def get_full_history(self, account_id):
        pass

class Response:
    """
    The local side.
    """
    pass


class HistoryResponse(Response):

    def __init__(self, resp):

        self.status = resp['status']
        self.results_remaining = resp['results_remaining']
        self.num_results = resp['num_results']
        self.total_results = resp['total_results']
        self.matches = resp['matches']

        self.match_ids = [match['match_id'] for match in self.matches]

class DetailsResponse(Response):

    def __init__(self, resp):

        self.resp = resp
        self.match_id = resp['match_id']
        self.player_ids = [player['account_id'] for player in resp['players']]
        self.hero_id_to_names = self.get_hero_names()

    def get_by_player(self, key):
        """
        valid keys: {'kills', 'hero_id', 'player_slot', 'gold', 'gold_per_min',
                     'last_hits', 'ability_upgrades', 'level', 'hero_healing',
                     'deaths', 'leaver_status', 'additional_units',
                     'gold_spent', 'xp_per_min', 'assists', 'tower_damage',
                     'denies', 'hero_damage', 'item_4', 'item_5', 'item_2',
                     'item_3', 'item_0', 'item_1', 'account_id'}

        """
        # account id isn't nesc unique.
        return {player['hero_id']: player[key]
                for player in self.resp['players']}

    def get_match_report(self):
        keys = ['kills', 'deaths', 'assists',
                'last_hits', 'denies', 'gold']
        df = pd.concat([pd.Series(self.get_by_player(key))
                        for key in keys], axis=1, keys=keys)
        df = df.rename(index=lambda x: self.hero_id_to_names[str(x)])
        return df

    def get_hero_names(self):
        with open('../hero_names.json') as f:
            names = json.load(f)

        return names

    def get_team(self):
        pass


if __name__ == "__main__":
    with open('/Users/admin/Dropbox/bin/api-keys.txt', 'r') as f:
        api_keys = json.load(f)

    KEY = api_keys['steam']

    HISTORY_URL = ("https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/"
                   "V001/?key={key}&account_id={account_id}")
    MATCH_URL = ("https://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/"
                 "V001/?match_id={match_id}&key={key}")

    r = requests.get(HISTORY_URL.format(key=KEY, player_name='Auggie'))
    r = requests.get(MATCH_URL.format(key=KEY, match_id="478948089"))
    j = r.json()

    all_players = []
    for m in j['result']['matches']:
        all_players.append(get_players(m))

    df = pd.Series(list(flatten(all_players)))
