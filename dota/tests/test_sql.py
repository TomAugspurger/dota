# -*- coding: utf-8 -*-
import unittest

from sqlalchemy.orm import sessionmaker

from dota.sql.orm import Game, Player, PlayerGame, Team
from dota.sql import orm


class TestORM(unittest.TestCase):

    def setUp(self):
        """
        Create in memory engine. Populate with a few items.
        """

        engine = orm.make_engine("sqlite:///:memory:")
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(fake_game())
        session.add(fake_playergame())
        session.add(Player(account_id=1, name='name'))
        session.add(fake_team())
        session.commit()
        self.session = session

    def test_filter_by_patch(self):
        # just after 6.8
        game = fake_game(match_id=2, start_time=1390975201)
        self.session.add(game)
        self.assertIs(orm.filter_by_patch(self.session).first(), game)
        self.assertEqual(len(orm.filter_by_patch(self.session).all()), 1)

    def test_filter_by_patch_679_on(self):
        game1 = fake_game(match_id=2, start_time=1390975100)
        game2 = fake_game(match_id=3, start_time=1390975201)
        self.session.add_all([game1, game2])
        result = orm.filter_by_patch(self.session, start='6.79').all()
        self.assertEqual(len(result), 2)

    def test_filter_by_patch_679_only(self):
        game1 = fake_game(match_id=2, start_time=1390975100)
        game2 = fake_game(match_id=3, start_time=1390975201)
        self.session.add_all([game1, game2])
        result = orm.filter_by_patch(self.session, start='6.79',
                                     stop='6.80').all()
        self.assertEqual(len(result), 1)

    def tearDown(self):
        self.session.close()


def fake_playergame(**kwargs):
    d = {'match_id': 1,
         'account_id': 1,
         'hero_id': 1,
         'level': 25,
         'denies': 1,
         'gold': 1,
         'item_5': 1,
         'item_4': 1,
         'item_1': 1,
         'item_0': 1,
         'item_3': 1,
         'item_2': 1,
         'gold_spent': 1,
         'deaths': 1,
         'hero_damage': 1,
         'assists': 1,
         'gold_per_min': 1,
         'hero_healing': 1,
         'player_slot': 1,
         'last_hits': 1,
         'xp_per_min': 1,
         'tower_damage': 1,
         'kills': 1,
         'leaver_status': 1}
    d.update(kwargs)
    return PlayerGame(1, d)


def fake_game(**kwargs):
    d = {'match_id': 1,
         'dire_team_id': 1,
         'radiant_team_id': 1,
         'start_time': 1,
         'match_seq_num': 1,
         'leagueid': 1,
         'lobby_type': 1,
         'game_mode': 1,
         'positive_votes': 1,
         'negative_votes': 1,
         'radiant_win': 1,
         'duration': 1,
         'first_blood_time': 1,
         'tower_status_dire': 1,
         'tower_status_radiant': 1,
         'barracks_status_radiant': 1,
         'barracks_status_dire': 1,
         'human_players': 1}
    d.update(kwargs)
    return Game(d)


def fake_team(**kwargs):
    d = {'dire_team_id': 1,
         'dire_name': 'NaVi'}
    d.update(kwargs)
    return Team(d)
