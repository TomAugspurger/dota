import os
import json

from sqlalchemy import Boolean, Column, Integer, String, create_engine, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dota import api

Base = declarative_base()


class Game(Base):

    __tablename__ = 'games'

    match_id = Column(Integer, primary_key=True)
    start_time = Column(Integer)
    match_seq_num = Column(Integer)
    leagueid = Column(String)
    lobby_type = Column(Integer)
    game_mode = Column(Integer)
    positive_votes = Column(Integer)
    negative_votes = Column(Integer)

    radiant_win = Column(Boolean)
    duration = Column(Integer)
    first_blood_time = Column(Integer)
    tower_status_dire = Column(Integer)
    tower_status_radiant = Column(Integer)
    barracks_status_radiant = Column(Integer)
    barracks_status_dire = Column(Integer)
    human_players = Column(Integer)
    # player0 = Column(Integer)
    # player1 = Column(Integer)
    # player2 = Column(Integer)
    # player3 = Column(Integer)
    # player4 = Column(Integer)
    # player5 = Column(Integer)
    # player6 = Column(Integer)
    # player7 = Column(Integer)
    # player8 = Column(Integer)
    # player9 = Column(Integer)

    def __init__(self, resp):
        self.match_id = resp['match_id']
        self.start_time = resp['start_time']
        self.match_seq_num = resp['match_seq_num']
        self.leagueid = resp['leagueid']
        self.lobby_type = resp['lobby_type']
        self.game_mode = resp['game_mode']
        self.positive_votes = resp['positive_votes']
        self.negative_votes = resp['negative_votes']
        self.radiant_win = resp['radiant_win']
        self.duration = resp['duration']
        self.first_blood_time = resp['first_blood_time']
        self.tower_status_dire = resp['tower_status_dire']
        self.tower_status_radiant = resp['tower_status_radiant']
        self.barracks_status_radiant = resp['barracks_status_radiant']
        self.barracks_status_dire = resp['barracks_status_dire']
        self.human_players = resp['human_players']
        # player0 = Column(Integer)
        # player1 = Column(Integer)
        # player2 = Column(Integer)
        # player3 = Column(Integer)
        # player4 = Column(Integer)
        # player5 = Column(Integer)
        # player6 = Column(Integer)
        # player7 = Column(Integer)
        # player8 = Column(Integer)
        # player9 = Column(Integer)

    def __repr__(self):
        return "<Game {}>".format(self.match_id)


class Player(Base):

    __tablename__ = 'players'

    # player_match_id = Column(Integer,
    #                          Sequence('player_match_id_sq'), primary_key=True)
    match_id = Column(Integer)
    account_id = Column(Integer, primary_key=True)
    hero_id = Column(Integer)
    level = Column(Integer)
    denies = Column(Integer)
    gold = Column(Integer)
    item_5 = Column(Integer)
    item_4 = Column(Integer)
    item_1 = Column(Integer)
    item_0 = Column(Integer)
    item_3 = Column(Integer)
    item_2 = Column(Integer)
    gold_spent = Column(Integer)
    deaths = Column(Integer)
    hero_damage = Column(Integer)
    assists = Column(Integer)
    gold_per_min = Column(Integer)
    hero_healing = Column(Integer)
    player_slot = Column(Integer)
    last_hits = Column(Integer)
    xp_per_min = Column(Integer)
    tower_damage = Column(Integer)
    kills = Column(Integer)
    leaver_status = Column(Integer)
    # ability_upgrades = Column(Integer)

    def __init__(self, match_id, resp):

        self.match_id = match_id
        self.account_id = resp['account_id']
        self.hero_id = resp['hero_id']
        self.level = resp['level']
        self.denies = resp['denies']
        self.gold = resp['gold']
        self.item_5 = resp['item_5']
        self.item_4 = resp['item_4']
        self.item_1 = resp['item_1']
        self.item_0 = resp['item_0']
        self.item_3 = resp['item_3']
        self.item_2 = resp['item_2']
        self.gold_spent = resp['gold_spent']
        self.deaths = resp['deaths']
        self.hero_damage = resp['hero_damage']
        self.assists = resp['assists']
        self.gold_per_min = resp['gold_per_min']
        self.hero_healing = resp['hero_healing']
        self.player_slot = resp['player_slot']
        self.last_hits = resp['last_hits']
        self.xp_per_min = resp['xp_per_min']
        self.tower_damage = resp['tower_damage']
        self.kills = resp['kills']
        self.leaver_status = resp['leaver_status']


def make_players(DR):
    players = []
    for player in DR.resp['players']:
        players.append(Player(d.match_id, player))

    return players

games = ['detail392159753.json', 'detail430298310.json', 'detail462344226.json',
         'detail510935923.json', 'detail550014092.json', 'detail431670975.json']

engine = create_engine('sqlite:///tst.db', echo=True)


Session = sessionmaker(bind=engine)
session = Session()

for g in games:

    with open(os.path.expanduser('~/sandbox/dota/data/' + g)) as f:
        d = api.DetailsResponse(json.load(f))

    game = Game(d.resp)
    game.metadata.create_all(engine)
    session.add(game)

session.commit()
