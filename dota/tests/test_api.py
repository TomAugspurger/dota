# -*- coding: utf-8 -*-
import os
import json
import unittest

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO

from numpy import nan
import pandas as pd
import pandas.util.testing as tm
from pandas.util.testing import network

from dota.api import API, HistoryResponse, DetailsResponse


class TestAPI(unittest.TestCase):
    """
    All network tests are here. Assumes the existence of a JSON
    file call .key.json in the local tests/ directory with the format
    {
        "steam": KEY
    }
    """
    def setUp(self):
        with open('.key.json') as f:
            key = json.load(f)['steam']
        self.h = API(key)

    @network
    def test_get_match_history(self):
        hist = self.h.get_match_history(account_id=76561198025007092,
                                        start_at_match_id=547519680,
                                        matches_requested=1)
        self.assertEqual(len(hist.matches), 1)
        self.assertEqual(hist.match_ids, [547519680])

    @network
    def test_get_match_details(self):
        MATCH_ID = 547519680
        d = self.h.get_match_details(match_id=MATCH_ID)
        self.assertEqual(d.match_id, MATCH_ID)
        self.assertEqual(d.winner, 'Radiant')


class TestHistoryResponse(unittest.TestCase):

    def setUp(self):
        with open('history_response.json') as f:
            self.hr = HistoryResponse(json.load(f))

    def test_partner_counts(self):
        pass

    def test_add(self):
        result = self.hr + self.hr
        self.assertEqual(len(result.match_ids), 2 * len(self.hr.match_ids))
        self.assertEqual(result.total_results, self.hr.total_results)
        self.assertEqual(result.status, self.hr.status)

    def test_len(self):
        self.assertEqual(len(self.hr), len(self.hr.match_ids))

    # def test_to_json(self):

    #     d = {1234: DetailsResponse({'radiant_win': True,
    #                                 'match_id': 1234,
    #                                 'players': []})}
    #     self.hr.update_details(d)
    #     self.hr.to_json('test_to_json.json')
    #     with open('test_to_json.json', 'r') as f:
    #         result = json.load(f)
    #     expected = {'history': self.hr.resp,
    #                 'details': d}
    #     self.assertEqual(result, expected)
    #     os.remove(test_to_json.json)


class TestDetailsResponse(unittest.TestCase):

    def setUp(self):
        with open('details_response.json') as f:
            self.dr = DetailsResponse(json.load(f))

    def test_match_report(self):
        result = self.dr.match_report().iloc[:2]
        d = {'gold': {(547519680, 'Dire', 'bounty_hunter'): 16, (547519680, 'Dire', 'crystal_maiden'): 1626},
             'item_0': {(547519680, 'Dire', 'bounty_hunter'): 36, (547519680, 'Dire', 'crystal_maiden'): 36},
             'item_2': {(547519680, 'Dire', 'bounty_hunter'): 168, (547519680, 'Dire', 'crystal_maiden'): 37},
             'player_slot': {(547519680, 'Dire', 'bounty_hunter'): 128, (547519680, 'Dire', 'crystal_maiden'): 131},
             'item_4': {(547519680, 'Dire', 'bounty_hunter'): 67, (547519680, 'Dire', 'crystal_maiden'): 102},
             'hero_damage': {(547519680, 'Dire', 'bounty_hunter'): 6141, (547519680, 'Dire', 'crystal_maiden'): 8204},
             'last_hits': {(547519680, 'Dire', 'bounty_hunter'): 56, (547519680, 'Dire', 'crystal_maiden'): 64},
             'item_1': {(547519680, 'Dire', 'bounty_hunter'): 50, (547519680, 'Dire', 'crystal_maiden'): 42},
             'kills': {(547519680, 'Dire', 'bounty_hunter'): 4, (547519680, 'Dire', 'crystal_maiden'): 6},
             'denies': {(547519680, 'Dire', 'bounty_hunter'): 1, (547519680, 'Dire', 'crystal_maiden'): 6},
             'hero_healing': {(547519680, 'Dire', 'bounty_hunter'): 0, (547519680, 'Dire', 'crystal_maiden'): 0},
             'level': {(547519680, 'Dire', 'bounty_hunter'): 16, (547519680, 'Dire', 'crystal_maiden'): 17},
             'item_3': {(547519680, 'Dire', 'bounty_hunter'): 185, (547519680, 'Dire', 'crystal_maiden'): 214},
             'win': {(547519680, 'Dire', 'bounty_hunter'): False, (547519680, 'Dire', 'crystal_maiden'): False},
             'deaths': {(547519680, 'Dire', 'bounty_hunter'): 10, (547519680, 'Dire', 'crystal_maiden'): 10},
             'gold_spent': {(547519680, 'Dire', 'bounty_hunter'): 12185, (547519680, 'Dire', 'crystal_maiden'): 8505},
             'account_id': {(547519680, 'Dire', 'bounty_hunter'): 82787032.0, (547519680, 'Dire', 'crystal_maiden'): nan},
             'assists': {(547519680, 'Dire', 'bounty_hunter'): 5, (547519680, 'Dire', 'crystal_maiden'): 7},
             'item_5': {(547519680, 'Dire', 'bounty_hunter'): 46, (547519680, 'Dire', 'crystal_maiden'): 0}}
        expected = pd.DataFrame(d)
        expected.index = pd.MultiIndex.from_tuples(expected.index)
        expected = expected.sort_index()
        expected = result.reindex_axis(result.columns, axis=1)
        tm.assert_frame_equal(result, expected)

    def test_format_df(self):
        data = [{'hero_damage': 26610,
                 'denies': 20,
                 'player_slot': 128,
                 'last_hits': 342,
                 'item_3': 63,
                 'item_2': 0,
                 'item_1': 123,
                 'item_0': 135,
                 'account_id': 26316691,
                 'item_5': 141,
                 'hero_healing': 0,
                 'hero_id': 63,
                 'deaths': 4,
                 'item_4': 168,
                 'level': 23,
                 'kills': 16,
                 'gold_spent': 27186,
                 'assists': 6,
                 'gold': 3663},
                {'hero_damage': 5382,
                 'denies': 2,
                 'player_slot': 132,
                 'last_hits': 72,
                 'item_3': 30,
                 'item_2': 100,
                 'item_1': 34,
                 'item_0': 214,
                 'account_id': 36547811,
                 'item_5': 0,
                 'hero_healing': 7899,
                 'hero_id': 102,
                 'deaths': 2,
                 'item_4': 102,
                 'level': 19,
                 'kills': 1,
                 'gold_spent': 8535,
                 'assists': 11,
                 'gold': 5096}]
        df = pd.DataFrame(data)
        result = DetailsResponse.format_df(df, 'Dire', 1)
        expected = pd.DataFrame({'hero_damage': {(1, 'Dire', '102'): 5382, (1, 'Dire', 'weaver'): 26610},
                                 'denies': {(1, 'Dire', '102'): 2, (1, 'Dire', 'weaver'): 20},
                                 'item_5': {(1, 'Dire', '102'): 0, (1, 'Dire', 'weaver'): 141},
                                 'item_4': {(1, 'Dire', '102'): 102, (1, 'Dire', 'weaver'): 168},
                                 'item_3': {(1, 'Dire', '102'): 30, (1, 'Dire', 'weaver'): 63},
                                 'item_2': {(1, 'Dire', '102'): 100, (1, 'Dire', 'weaver'): 0},
                                 'item_1': {(1, 'Dire', '102'): 34, (1, 'Dire', 'weaver'): 123},
                                 'item_0': {(1, 'Dire', '102'): 214, (1, 'Dire', 'weaver'): 135},
                                 'account_id': {(1, 'Dire', '102'): 36547811, (1, 'Dire', 'weaver'): 26316691},
                                 'win': {(1, 'Dire', '102'): True, (1, 'Dire', 'weaver'): True},
                                 'player_slot': {(1, 'Dire', '102'): 132, (1, 'Dire', 'weaver'): 128},
                                 'hero_healing': {(1, 'Dire', '102'): 7899, (1, 'Dire', 'weaver'): 0},
                                 'deaths': {(1, 'Dire', '102'): 2, (1, 'Dire', 'weaver'): 4},
                                 'last_hits': {(1, 'Dire', '102'): 72, (1, 'Dire', 'weaver'): 342},
                                 'level': {(1, 'Dire', '102'): 19, (1, 'Dire', 'weaver'): 23},
                                 'kills': {(1, 'Dire', '102'): 1, (1, 'Dire', 'weaver'): 16},
                                 'gold_spent': {(1, 'Dire', '102'): 8535, (1, 'Dire', 'weaver'): 27186},
                                 'assists': {(1, 'Dire', '102'): 11, (1, 'Dire', 'weaver'): 6},
                                 'gold': {(1, 'Dire', '102'): 5096, (1, 'Dire', 'weaver'): 3663}})
        expected.index = pd.MultiIndex.from_tuples(expected.index,
                                                   names=['match_id', 'team',
                                                          'hero'])
        expected = expected.sort_index()
        tm.assert_frame_equal(result, expected)


def _get_test_files():
    """
    Used to generate the details_response.json file.
    """
    with open('.key.json') as f:
        key = json.load(f)['steam']
    h = API(key)

    hist = h.get_match_history(account_id=76561198025007092)
    with open('history_response.json', 'w') as f:
        json.dump(hist.resp, f)

    dr = h.get_match_details(547519680)
    with open('details_response.json', 'w') as f:
        json.dump(dr.resp, f)
