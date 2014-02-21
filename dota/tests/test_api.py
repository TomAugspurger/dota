import json
import unittest

from dota.api import HistoryResponse, DetailsResponse


class TestAPI(unittest.TestCase):

    pass


class TestHistoryResponse(unittest.TestCase):

    def setUp(self):
        with open('history_response.json') as f:
            self.hr = HistoryResponse(json.load(f))

    def test_player_counts(self):
        pass


class TestDetailsResponse(unittest.TestCase):

    def setUp(self):
        with open('details_response.json') as f:
            self.dr = DetailsResponse(json.load(f))
