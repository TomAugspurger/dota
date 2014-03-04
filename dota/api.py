from __future__ import division

import itertools as it

import json
import requests
from requests.exceptions import HTTPError
import pandas as pd
import numpy as np

from os.path import dirname, abspath

with open(dirname(abspath(__file__)) + "/hero_names.json") as f:
    _HERO_NAMES = json.load(f)


_PRIVATE = 4294967295  # privacy option in client

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
        # inpsect query so you can finish out the results.
        self.query = kwargs
        kwargs['key'] = self.key
        r = requests.get(self.HISTORY_URL, params=kwargs)
        hist = HistoryResponse(r.json()['result'], helper=self)
        # at time of implementation the date_min/max kwargs are browken
        # using start_at_match_id as a workaround
        while hist.results_remaining > 0:
            new_kwargs = kwargs.copy()
            new_start_match_id = min([m['match_id'] for m in hist.matches]) - 1
            new_kwargs['start_at_match_id'] = new_start_match_id
            r = requests.get(self.HISTORY_URL, params=new_kwargs)
            hist += HistoryResponse(r.json()['result'], helper=self)
        return hist

    def get_match_details(self, match_id, **kwargs):
        kwargs['key'] = self.key
        kwargs['match_id'] = match_id
        r = requests.get(self.MATCH_URL, params=kwargs)
        if r.status_code == 503:
            raise HTTPError
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

    def __add__(self, other):
        """
        Parameters
        ----------

        other : HistoryResponse

        Returns
        -------

        resp : HistoryResponse

        If ``other`` is an exhaustion of self then the total results and
        results remaing attributes are propogated to the retuern HistoryResponse.
        That's determined by the total results equaling (which is not
        foolproof).

        """
        resp1 = self.resp
        resp2 = other.resp

        resp = {}
        resp['num_results'] = len(self) + len(other)
        try:
            assert resp1['total_results'] == resp2['total_results']
            resp['results_remaining'] = min(resp1['results_remaining'],
                                            resp2['results_remaining'])
            resp['total_results'] = resp1['total_results']
        except AssertionError:
            resp['results_remaining'] = np.nan
            resp['total_results'] = np.nan
        resp['matches'] = resp1['matches'] + resp2['matches']
        resp['status'] = max(resp1['status'], resp2['status'])

        helper = self.helper or other.helper
        return HistoryResponse(resp, helper=helper)

    def __len__(self):
        return len(self.match_ids)

    def get_all_match_details(self, helper=None):

        import time
        details = {}
        N = len(self.match_ids)

        helper = helper or self.helper
        self._check_helper(helper=helper)

        for i, match in enumerate(self.match_ids):
            try:
                details[match] = helper.get_match_details(match)
            except HTTPError:
                import warnings
                warnings.warn("HTTPError on {}".format(match))
            time.sleep(.25)  # rate limiting
            # TODO: progress bar
            if round((i / N) * 100) % 10 == 0:
                print("\rAdded {} ({}%)".format(match, 100 * i / N))

        responses = {k: DetailsResponse(v) for k, v in details.items()}
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
        for p in resp['players']:
            if p.get('account_id') == _PRIVATE:
                p['account_id'] = np.nan
        self.player_ids = [player.get('account_id', np.nan) for player in resp['players']]
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
        return {player['hero_id']: player.get(key)
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

        return df

    def get_team(self):
        pass

