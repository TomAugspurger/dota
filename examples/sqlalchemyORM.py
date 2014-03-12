import os
import json


import pandas as pd
from sqlalchemy import (Boolean, Column, Integer, String, create_engine,
                        Sequence, Table, ForeignKey)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref

from dota import api

Base = declarative_base()

# association_table = Table('association', Base.metadata,
#                           Column('match_id', Integer, ForeignKey('games.match_id')),
#                           Column('player_id', Integer, ForeignKey('players.account_id'))
#                           )

class PlayerGame(Base):

    __tablename__ = 'playergames'

    match_id = Column(Integer, ForeignKey('games.match_id'), primary_key=True)
    account_id = Column(Integer, ForeignKey('players.account_id'), primary_key=True)

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

    player = relationship("Player", backref="playergames")

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

    players = relationship("PlayerGame", backref="games")

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

    def __repr__(self):
        return "<Game {}>".format(self.match_id)


class Player(Base):

    __tablename__ = 'players'

    account_id = Column(Integer, primary_key=True)
    handle = Column(String)


def main():
    games = ['detail392159753.json', 'detail430298310.json', 'detail462344226.json',
             'detail510935923.json', 'detail550014092.json', 'detail431670975.json']

    engine = create_engine('sqlite:///:memory:', echo=True)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    gs = []
    for g in games:

        with open(os.path.expanduser('~/sandbox/dota/data/' + g)) as f:
            d = api.DetailsResponse(json.load(f))

        game = Game(d.resp)
        gs.append(game)
        pgs = []
        pls = []
        for player in d.resp['players']:
            pg = PlayerGame(d.match_id, player)
            if pd.isnull(pg.account_id):
                continue

            pl = Player(account_id=pg.account_id)
            existing_player = session.query(Player).filter(
                Player.account_id == pl.account_id).first()
            if existing_player is None:
                session.add(pl)

            # pls.append(pl)
            pgs.append(pg)

        session.add_all(pgs)
        session.add_all(pls)
    session.add_all(gs)
    session.commit()
    return engine, session

if __name__ == '__main__':

    main()
