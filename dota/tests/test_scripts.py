# -*- coding: utf-8 -*-
import pathlib
import unittest
from unittest.mock import patch
from os.path import expanduser

from dota.api import API, HistoryResponse, DetailsResponse
from dota.scripts import get_details_by_id


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
