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

    def test_add(self):
        result = self.hr + self.hr
        self.assertEqual(len(result.match_ids), 2 * len(self.hr.match_ids))
        self.assertEqual(result.total_results, self.hr.total_results)
        self.assertEqual(result.status, self.hr.status)

    def test_len(self):
        self.assertEqual(len(self.hr), len(self.hr.match_ids))


class TestDetailsResponse(unittest.TestCase):

    def setUp(self):
        with open('details_response.json') as f:
            self.dr = DetailsResponse(json.load(f))
