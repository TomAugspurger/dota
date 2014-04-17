# -*- coding: utf-8 -*-
import argparse
import re
import json
from functools import partial

import requests

from dota.helpers import open_or_stringIO

_start_hero_pattern = '\t"npc_dota_hero_'
_start_item_pattern = '\t"item_'
# ability has 1 false positive `\t"Version"`
_start_ability_pattern = '\t"'


#-----------------------------------------------------------------------------
# Three main parsers: abilities, items, heros
# each parser writes its results to dota/*_parsed.json


def parse_abilities(ability_file='../npc_abilities.txt'):

    with open_or_stringIO(ability_file) as f:
        blocks = []
        for line in f:
            if (line.startswith(_start_ability_pattern) and
                    not line.startswith('\t"Version"')):
                block = get_ability_block(f, line)
                blocks.append(block)

    ability_d = _construct_json(blocks)

    with open("../abilities_parsed.json", 'w') as f:
        json.dump(ability_d, f)
        print("Parsed Abilities.")


def parse_heroes(hero_file='../npc_heroes.txt'):
    with open_or_stringIO(hero_file) as f:
        hero_blocks = []
        for line in f:
            if line.startswith(_start_hero_pattern):
                hero_block = get_hero_block(f, line)
                hero_blocks.append(hero_block)

    hero_d = _construct_json(hero_blocks)

    with open("../heroes_parsed.json", 'w') as f:
        json.dump(hero_d, f)
        print("Parsed Heros.")


def parse_items(item_file='../items.txt'):
    with open_or_stringIO(item_file) as f:

        blocks = []
        for line in f:
            if (line.startswith(_start_item_pattern)):
                block = get_item_block(f, line)
                blocks.append(block)

    item_d = _construct_json(blocks)
    with open("../items_parsed.json", 'w') as f:
        json.dump(item_d, f)
        print("Parsed Items.")


def _construct_json(blocks):
    d = {}
    for block in blocks:
        d[block[0][1]] = dict(block[1:])

    return d


def get_hero_block(f, line):
    results = get_block(f, line, kind='hero')
    return results  # results isn't unique cause nesting


def get_hero_names(heros):
    ids = {}
    for hero in heros:
        d = dict(hero)
        name = d['name']
        hero_id = d.get('HeroID', 0)
        ids[int(hero_id)] = name
    return ids


def get_item_block(f, line):

    results = get_block(f, line, kind='item')
    return results


def get_ability_block(f, line):

    results = get_block(f, line, kind='ability')
    return results


def get_block(f, line, kind):
    if kind == 'hero':
        name = line.split(_start_hero_pattern)[1].rstrip('"\t\n')
    elif kind == 'ability':
        name = line.strip().strip('"')
    elif kind == 'item':
        name = line.split(_start_item_pattern)[1].rstrip('"\t\n')

    f.readline()  # {
    n_open = 1

    pair = re.compile(r'\t*\"(.+)\"\s*\"(.+)\"')

    results = []
    results.append(('name', name))
    for line in f:
        if re.search(r'\t+{', line):
            n_open += 1
        elif re.search(r'\t+}', line):
            n_open -= 1
            if n_open == 0:
                break
        elif re.search(pair, line):
            results.append(re.search(pair, line).groups())

    return results

#-----------------------------------------------------------------------------
# update raw files


def update_files(kind):

    urls = {'abilities': ("https://raw.githubusercontent.com/dotadelight/"
                          "dota2-database/master/sources/npc_abilities.txt"),
            'heroes': ("https://raw.githubusercontent.com/dotadelight/"
                       "dota2-database/master/sources/npc_heroes.txt")}
    r = requests.get(urls[kind])

    with open('../npc_{}.txt'.format(kind), 'w') as f:
        f.write(r.text)
    print("Updated {}".format(kind))

#-----------------------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument('kind', choices=['items', 'heroes', 'abilities',
                                     'update_abilities', 'update_heroes'])

if __name__ == '__main__':
    args = parser.parse_args()
    kind = args.kind

    dispatch = {'items': parse_items,
                'heroes': parse_heroes,
                'abilities': parse_abilities,
                'update_abilities': partial(update_files, 'abilities'),
                'update_heroes': partial(update_files, 'heroes')
                }
    dispatch[kind]()
