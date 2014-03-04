import json
import unittest

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


class TestDetailsResponse(unittest.TestCase):

    def setUp(self):
        with open('details_response.json') as f:
            self.dr = DetailsResponse(json.load(f))

    def test_match_report(self):
        self.dr.match_report()  # works


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
