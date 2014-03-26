# -*- coding: utf-8 -*-
import pathlib
import unittest
from unittest.mock import patch
from os.path import expanduser

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO


from dota.api import API, HistoryResponse, DetailsResponse
from dota.scripts import get_details_by_id
import dota.scripts.parsers as p

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
