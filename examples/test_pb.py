# -*- coding: utf-8 -*-
import unittest

import numpy as np
import pandas as pd
import pandas.util.testing as tm

import dota.helpers as h


class TestExtraction(unittest.TestCase):

    def setUp(self):
        pbs = ([False] * 4 + [True] * 4 + [False] * 4
               + [True] * 4 + [False] * 2 + [True] * 2)
        team = np.array([0, 1, 0, 1, 0, 1, 1, 0, 0, 1,
                         0, 1, 1, 0, 1, 0, 1, 0, 1, 0])
        self.df = pd.DataFrame({'hero_id': range(20),
                                'is_pick': pbs,
                                'order': range(20),
                                'team': team,
                                'team_id': team,
                                'team_name': team,
                                'match_id': np.ones(20),
                                'team_id_f': team,
                                'hero_id_f': range(20)
                                })

    def test_opponent(self):
        expected = np.abs(self.df['team_id_f'] - 1)

        for order in range(20):
            result = h.pb_opponent_id(self.df, order=order)
            self.assertEqual(result, expected.iloc[order])

    def test_previous_pbs(self):

        for i in range(1, 20):
            d = {'pb_{}'.format(j): j for j in range(i)}
            expected = pd.DataFrame(d, index=['hero_id_f'])
            expected = expected[sorted(d.keys(),
                                       key=lambda x: int(x.split('_')[-1]))]
            result = h.pb_previous_pbs(self.df, i)
            tm.assert_frame_equal(result, expected)

    def test_only_complete(self):

        result = h.pb_only_complete_drafts(self.df)
        tm.assert_frame_equal(result, self.df)

        bad = self.df.copy()
        bad.loc[0, 'team_id'] = np.nan
        bad['match_id'] = bad['match_id'] + 1
        bad = pd.concat([bad, self.df])

        result = h.pb_only_complete_drafts(bad)
        tm.assert_frame_equal(result, self.df, check_dtype=False)
