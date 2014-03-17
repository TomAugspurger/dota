# -*- coding: utf-8 -*-

import pathlib
import unittest

from dota.helpers import cached_games


class TestHelpers(unittest.TestCase):

    def setUp(self):
        pathlib.Path('details12345678.json').touch()
        pathlib.Path('1234.json').touch()

    def test_cached_games(self):

        p = pathlib.Path('.')
        result = sorted(cached_games(p))
        expected = [1234, 12345678]
        self.assertEqual(result, expected)

        result = sorted(cached_games(p))
        self.assertEqual(result, expected)

    def tearDown(self):
        pathlib.Path('details12345678.json').unlink()
        pathlib.Path('1234.json').unlink()
