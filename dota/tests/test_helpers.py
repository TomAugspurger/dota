# -*- coding: utf-8 -*-

import pathlib
import unittest
import io

import requests
from pandas.util.testing import network

from dota import helpers as h
from dota.helpers import cached_games, open_or_stringIO


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

    def test_open_or_stringIO(self):
        fileobj = open_or_stringIO('1234.json')
        self.assertIsInstance(fileobj, io.TextIOWrapper)

        stringobj = open_or_stringIO("fakefile")
        self.assertIsInstance(stringobj, io.StringIO)

        stringobj = open_or_stringIO("1234.json", as_string=True)
        self.assertIsInstance(stringobj, io.StringIO)


class TestResources(unittest.TestCase):

    def test_format_resource_name(self):
        result = h._format_resource_name('kunkka', 'hero', 'lg')
        expected = 'kunkka_lg.png'
        self.assertEqual(result, expected)

        result = h._format_resource_name('kunkka', 'hero', 'full')
        expected = 'kunkka_full.jpg'
        self.assertEqual(result, expected)

        result = h._format_resource_name('blink', 'item', 'lg')
        expected = 'blink_lg.png'
        self.assertEqual(result, expected)

    @network
    def test_fetch_resource(self):
        url = "http://cdn.dota2.com/apps/dota2/images/heroes/kunkka_lg.png"
        self.assertTrue(requests.get(url, stream=True).ok)

        url = "http://cdn.dota2.com/apps/dota2/images/heroes/FAKE.png"
        self.assertFalse(requests.get(url, stream=True).ok)
