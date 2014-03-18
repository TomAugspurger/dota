import argparse
import re
import os
import json
import pathlib

from lxml import html

from dota import api

_start_hero_pattern = '\t"npc_dota_hero_'
_start_item_pattern = '\t"item_'
# ability has 1 false positive `\t"Version"`
_start_ability_pattern = '\t"'


#-----------------------------------------------------------------------------
# Three main parsers: abilities, items, heros
# each parser writes its results to dota/*_parsed.json

def parse_abilities():
    with open('dota/npc_abilities.txt') as f:
        blocks = []
        for line in f:
            if (line.startswith(_start_ability_pattern) and
                    not line.startswith('\t"Version"')):
                block = get_ability_block(f, line)
                blocks.append(block)

    ability_d = _construct_json(blocks)

    with open("dota/abilities_parsed.json", 'w') as f:
        json.dump(ability_d, f)
        print("Parsed Abilities.")


def parse_heroes():
    with open('dota/npc_heroes.txt') as f:
        hero_blocks = []
        for line in f:
            if line.startswith(_start_hero_pattern):
                hero_block = get_hero_block(f, line)
                hero_blocks.append(hero_block)

    hero_d = _construct_json(hero_blocks)

    with open("dota/heroes_parsed.json", 'w') as f:
        json.dump(hero_d, f)
        print("Parsed Heros.")


def parse_items():
    with open('dota/items.txt') as f:

        blocks = []
        for line in f:
            if (line.startswith(_start_item_pattern)):
                block = get_item_block(f, line)
                blocks.append(block)

    item_d = _construct_json(blocks)
    with open("dota/items_parsed.json", 'w') as f:
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


def get_pro_matches():
    # Find new match ids
    url = "http://www.datdota.com/matches.php"
    r = html.parse(url).getroot()

    reg = re.compile(r'match.*(\d{9})$')
    links = filter(lambda x: reg.match(x[2]), r.iterlinks())

    here = os.path.dirname(__file__)
    match_ids_path = os.path.join(here, 'data', 'pro', 'pro_match_ids.txt')

    with open(match_ids_path, 'r') as f:
        old_ids = f.readlines()

    ids = (x[2].split('?q=')[-1] + '\n' for x in links)
    new_ids = [x for x in ids if x not in old_ids]

    with open(match_ids_path,  'a+') as f:
        f.writelines(new_ids)

    #--------------------------------------------------------------------------
    # Get Match Details for new matches
    with open(os.path.expanduser('~/') + 'Dropbox/bin/api-keys.txt') as f:
        key = json.load(f)['steam']

    h = api.API(key=key)

    with open(match_ids_path, 'a+') as f:
        match_ids = [x.strip() for x in f.readlines()]

    f = pathlib.Path(__file__).absolute()
    data_path = f.parent.joinpath(pathlib.Path('data/pro'))

    matches = filter(None, map(lambda x: re.match(r'.*(\d{9}).json$', x),
                               os.listdir(str(data_path))))
    matches = [x.groups()[0] for x in matches]
    new_matches = [x for x in match_ids if x not in matches]
    details = {mid: h.get_match_details(mid) for mid in new_matches}

    if not data_path.exists():
        data_path.mkdir()

    for k in details:
        with (data_path / (str(k) + '.json')).open('w') as f:
            json.dump(details[k].resp, f)

    #--------------------------------------------------------------------------
    # Insert into pro.db
    from examples.sqlalchemyORM import update_db

    update_db(data_path)

    print("Added {}".format(new_ids))


parser = argparse.ArgumentParser()
parser.add_argument('kind', choices=['items', 'heroes', 'abilities',
                                     'pro_matches'])


if __name__ == '__main__':
    args = parser.parse_args()
    kind = args.kind

    dispatch = {'items': parse_items,
                'heroes': parse_heroes,
                'abilities': parse_abilities,
                'pro_matches': get_pro_matches
                }
    dispatch[kind]()
