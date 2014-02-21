from __future__ import division

import itertools as it

import json
import requests
import pandas as pd
import numpy as np

from os.path import dirname, abspath

with open(dirname(abspath(__file__)) + "/hero_names.json") as f:
    _HERO_NAMES = json.load(f)


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


def id_64(id_32):
    return id_32 + 76561197960265728


def id_32(id_64):
    return id_64 - 76561197960265728


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
        """

        Parameters
        -----------------
        player_name: str
            Search matches with a player name, exact match only
        hero_id: str
            Search for matches with a specific hero being played (hero ID, not name, see HEROES below)
        game_mode: int
            Search for matches of a given mode (see below)
        skill: int
            0 for any, 1 for normal, 2 for high, 3 for very high skill (default is 0)
        date_min: int UTC
            date in UTC seconds since Jan 1, 1970 (unix time format)
        date_max: int UTC
            date in UTC seconds since Jan 1, 1970 (unix time format)
        min_players: int
            the minimum number of players required in the match
        account_id: int
            Search for all matches for the given user (32-bit or 64-bit steam ID)
        league_id: int
            matches for a particular league
        start_at_match_id: int
            Start the search at the indicated match id, descending
        matches_requested: int
            Maximum is 25 matches (default is 25)
        tournament_games_only:
            set to only show tournament games

        Examples
        --------

        import arrow
        now = arrow.utcnow()
        yest = now.replace(days=-1)

        h = api.API(key)
        history = h.get_match_history(date_min=yest.strftime('%s'),
                                      date_max=now.strftime('%s'))

        """
        kwargs['key'] = self.key
        r = requests.get(self.HISTORY_URL, params=kwargs)
        return HistoryResponse(r.json()['result'], helper=self)

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

    def parse_match_history(self, history):
        return [self.parse_match(match) for match in history['matches']]

    @staticmethod
    def parse_match(match):
        pass

    @staticmethod
    def player_counts(history):
        ids = []
        for match in history['matches']:
            for player in match['players']:
                ids.append(player['account_id'])
        s = pd.Series(ids)
        s = s.replace(4294967295, np.nan)  # private profiles.
        return pd.value_counts(s)

    # @staticmethod
    # def match_ids(history):
    #     return [match['match_id'] for match in history['matches']]


class Response:
    """
    The local side.
    """
    pass


class HistoryResponse(Response):

    def __init__(self, resp, helper=None):

        self.status = resp['status']
        self.results_remaining = resp['results_remaining']
        self.num_results = resp['num_results']
        self.total_results = resp['total_results']
        self.matches = resp['matches']

        self.match_ids = [match['match_id'] for match in self.matches]
        self.helper = helper
        self.resp = resp

    def get_all_match_details(self, helper=None):

        import time
        details = {}
        N = len(self.match_ids)

        helper = helper or self.helper
        self._check_helper(helper=helper)

        for i, match in enumerate(self.match_ids):
            details[match] = helper.get_match_details(match)
            time.sleep(.9)  # rate limiting
            # TODO: progress bar
            if round((i / N) * 100) % 10 == 0:
                print("Added {} ({}%)".format(match, 10 * i / N))

        responses = {k: DetailsResponse(v) for k, v in details.iteritems()}
        return responses

    def _check_helper(self, helper=None):
        if helper is None and self.helper is None:
            raise ValueError("Need to start an API object")

    def get_partners(self):
        cts = []
        for match in self.matches:
            for player in match['players']:
                cts.append(player['account_id'])
        cts = pd.Series(cts)
        cts = cts.replace(4294967295, np.nan)
        return cts.value_counts()


class DetailsResponse(Response):

    def __init__(self, resp):

        self.resp = resp
        if resp['radiant_win']:
            self.winner = 'Radiant'
        else:
            self.winner = 'Dire'
        self.match_id = resp['match_id']
        self.player_ids = [player['account_id'] for player in resp['players']]
        self.hero_id_to_names = _HERO_NAMES

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
        # TODO: ability upgrades
        keys = ['level', 'kills', 'deaths', 'assists',
                'last_hits', 'denies', 'gold', 'gold_spent', 'player_slot',
                'account_id', 'item_0', 'item_1', 'item_2', 'item_3', 'item_4',
                'item_5']
        df = pd.concat([pd.Series(self.get_by_player(key))
                        for key in keys], axis=1, keys=keys)
        df['match_id'] = self.match_id
        df = df.rename(index=lambda x: self.hero_id_to_names.get(str(x), str(x)))
        df.index.set_names(['hero'], inplace=True)

        def rep_team(x):
            if x < 5:
                return 'Radiant'
            else:
                return 'Dire'

        df['team'] = df['player_slot'].apply(rep_team)
        df['win'] = df['team'] == self.winner
        df = df.sort('team', ascending=False)

        df = df.reset_index().set_index(['match_id', 'team', 'hero'])
        df = df.rename(columns={'player_slot': 'team'})

        return df

    def get_hero_names(self):
        with open('hero_names.json') as f:
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
