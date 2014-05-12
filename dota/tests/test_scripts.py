# -*- coding: utf-8 -*-
import pathlib
import unittest
from unittest.mock import patch
from os.path import expanduser

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO

import requests
from pandas.util.testing import network

from numpy import nan
import pandas as pd
from pandas import Timestamp
import pandas.util.testing as tm

from dota.api import API, HistoryResponse, DetailsResponse
from dota.scripts import get_details_by_id
import dota.scripts.parsers as p
import dota.scripts.json2hdf5 as h5



class TestGetByID(unittest.TestCase):

    def setUp(self):
        # Make some fake cached games
        pathlib.Path('details12345678.json').touch()
        pathlib.Path('1234.json').touch()

    def test_argparser(self):
        args = ['1234']
        args = get_details_by_id.parser.parse_args(args)
        steam_id, key_path, data_dir = get_details_by_id.argparser(args)
        self.assertEqual(steam_id, 1234)
        self.assertEqual(key_path,
                         pathlib.Path(expanduser('~/Dropbox/bin/api-keys.txt')))
        self.assertEqual(data_dir,
                         pathlib.Path(expanduser('~/sandbox/dota/data/')))

    def test_get_details(self):
        # make fake new game 12345
        # TODO: mock out HR / DR construction as well?
        hr = HistoryResponse({'status': 1,
                              'results_remaining': 0,
                              'num_results': 1,
                              'total_results': 1,
                              'matches': [{'match_id': 12345}]})
        dr = DetailsResponse({'radiant_win': 1,
                              'match_id': 12345,
                              'players': [],
                              'negative_votes': 1,
                              'positive_votes': 1,
                              'lobby_type': 1,
                              'duration': 1,
                              'first_blood_time': 1,
                              'leagueid': 1,
                              'start_time': 1,
                              'dire_name': 1,
                              'radiant_name': 1,
                              'dire_team_id': 1,
                              'radiant_team_id': 1})

        with patch.object(API, 'get_match_history', return_value=hr):
            with patch.object(API, 'get_match_details', return_value=dr):
                get_details_by_id.get_details(steam_id=1, key='fake',
                                              data_dir=pathlib.Path('.'))

        new = pathlib.Path('12345.json')
        self.assertTrue(new.exists())

    def tearDown(self):
        pathlib.Path('details12345678.json').unlink()
        pathlib.Path('1234.json').unlink()
        try:
            pathlib.Path('12345.json').unlink()
        except FileNotFoundError:
            pass


# class TestGetProMatches(unittest.TestCase):

#     # def test_fetch_new_match_ids(match_ids_path):
#     #     # mocked


class TestParsers(unittest.TestCase):
    # the tabbing and newlining is important

    def setUp(self):
        self.ex_hero = """"npc_dota_hero_antimage"
        {
            // General
            //-------------------------------------------------------------------------------------------------------------
            "HeroID"                    "1"                                                     // unique ID number for this hero.  Do not change this once established or it will invalidate collected stats.
            "Ability4"                  "antimage_mana_void"                    // Ability 4
            "ItemSlots"
            {
                "0"
                {
                    "SlotIndex" "0"
                    "SlotName"  "weapon"
                    "SlotText"  "#LoadoutSlot_Weapon"
                    "TextureWidth"      "128"
                    "TextureHeight"     "256"
                    "MaxPolygonsLOD0"   "400"
                    "MaxPolygonsLOD1"   "350"
                }

            "Bot"
            {
                "HeroType"          "DOTA_BOT_HARD_CARRY"
                "LaningInfo"
                {
                    "SoloDesire"            "1"
                }
            }
        }
        """
        self.ex_item = """\t"item_blink"
    {
        // General
        //-------------------------------------------------------------------------------------------------------------
        "ID"                            "1"                                                     // unique ID number for this item.  Do not change this once established or it will invalidate collected stats.
        "AbilityName"                   "item_blink"
        "AbilitySpecial"
        {
            "01"
            {
                "var_type"              "FIELD_INTEGER"
                "blink_range"           "1200"
            }
        }
    }"""
        self.ex_ability = """\t"antimage_blink"
    {
        // General
        //-------------------------------------------------------------------------------------------------------------
        "ID"                    "5004"                                                      // unique ID number for this ability.  Do not change this once established or it will invalidate collected stats.
        "AbilityName"                   "antimage_blink"
        {
            "01"
            {
                "var_type"              "FIELD_INTEGER"
                "blink_range"           "1000 1075 1150 1150"
            }

        }
    }"""

    def test_parse_hero(self):
        f = StringIO(self.ex_hero)
        line = f.readline()
        result = p.get_ability_block(f, line)
        expected = [('name', 'npc_dota_hero_antimage'),
                    ('HeroID', '1'),
                    ('Ability4', 'antimage_mana_void'),
                    ('SlotIndex', '0'),
                    ('SlotName', 'weapon'),
                    ('SlotText', '#LoadoutSlot_Weapon'),
                    ('TextureWidth', '128'),
                    ('TextureHeight', '256'),
                    ('MaxPolygonsLOD0', '400'),
                    ('MaxPolygonsLOD1', '350'),
                    ('HeroType', 'DOTA_BOT_HARD_CARRY'),
                    ('SoloDesire', '1')]
        self.assertEqual(result, expected)
        f.close()

    def test_parse_item(self):
        f = StringIO(self.ex_item)
        line = f.readline()
        result = p.get_item_block(f, line)
        expected = [('name', 'blink'),
                    ('ID', '1'),
                    ('AbilityName', 'item_blink'),
                    ('var_type', 'FIELD_INTEGER'),
                    ('blink_range', '1200')]
        self.assertEqual(result, expected)
        f.close()

    def test_parse_ability(self):
        f = StringIO(self.ex_ability)
        line = f.readline()
        result = p.get_ability_block(f, line)
        expected = [('name', 'antimage_blink'),
                    ('ID', '5004'),
                    ('AbilityName', 'antimage_blink'),
                    ('var_type', 'FIELD_INTEGER'),
                    ('blink_range', '1000 1075 1150 1150')]

        self.assertEqual(result, expected)
        f.close()


class TestHDF5(unittest.TestCase):

    def setUp(self):
        self.dr = DetailsResponse.from_json('details_response.json')

    def test_add_by_side(self):
        # just a smoke test
        _data = {'duration': {0: 2857, 5: 2857},
                 'game_mod': {0: 1, 5: 1},
                 'team': {0: 1, 5: 0},
                 'item_2': {0: 168, 5: 79},
                 'hero_healing': {0: 0, 5: 1721},
                 'kills': {0: 4, 5: 7},
                 'dire_team_id': {0: None, 5: None},
                 'hero_damage': {0: 6141, 5: 9766},
                 'match_id': {0: 547519680, 5: 547519680},
                 'deaths': {0: 10, 5: 4},
                 'assists': {0: 5, 5: 14},
                 'radiant_team_id': {0: None, 5: None},
                 'gold_spent': {0: 12185, 5: 11910},
                 'tower_status': {0: nan, 5: nan},
                 'level': {0: 16, 5: 20},
                 'start_time': {0: Timestamp('2014-03-04 03:43:14'),
                                5: Timestamp('2014-03-04 03:43:14')},
                 'hero': {0: 62, 5: 102},
                 'player_slot': {0: 128, 5: 2},
                 'win': {0: False, 5: True},
                 'item_5': {0: 46, 5: 46},
                 'item_4': {0: 67, 5: 61},
                 'account_id': {0: 82787032.0, 5: nan},
                 'item_1': {0: 50, 5: 90},
                 'item_0': {0: 36, 5: 180},
                 'item_3': {0: 185, 5: 0},
                 'last_hits': {0: 56, 5: 67},
                 'denies': {0: 1, 5: 7},
                 'barracks_status': {0: nan, 5: nan},
                 'gold': {0: 16, 5: 3527}}

        expected = pd.DataFrame(_data).sort_index(axis=1)
        result = h5.format_df(self.dr).sort_index(axis=1).loc[[0, 5]]
        tm.assert_frame_equal(result, expected)
