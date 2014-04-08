# -*- coding: utf-8 -*-

import pathlib
from pathlib import Path
import unittest
import io

from dota.helpers import cached_games, open_or_stringIO


class TestHelpers(unittest.TestCase):

    def setUp(self):
        pathlib.Path('details12345678.json').touch()
        pathlib.Path('1234.json').touch()

    def test_cached_games(self):

        p = pathlib.Path('.')
        result = sorted(cached_games(p))
        expected = [Path('1234.json'), Path('details12345678.json')]
        self.assertEqual(result, expected)

        result = sorted(cached_games(p, full_path=False))
        expected = [1234, 12345678]
        self.assertEqual(result, expected)

    def tearDown(self):
        pathlib.Path('details12345678.json').unlink()
        pathlib.Path('1234.json').unlink()

    def test_open_or_stringIO(self):
        fileobj = open_or_stringIO('1234.json')
        self.assertIsInstance(fileobj, io.TextIOWrapper)

        stringobj = open_or_stringIO("fakefile")
        self.assertIsInstance(stringobj, io.StringIO)

        stringobj = open_or_stringIO("1234.json", as_string=True)
        self.assertIsInstance(stringobj, io.StringIO)
