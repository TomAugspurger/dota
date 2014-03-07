import re

_start_hero_pattern = '\t"npc_dota_hero_'
_start_item_pattern = '\t"item_'
# ability has 1 false positive `\t"Version"`
_start_ability_pattern = '\t"'

def parse_heros(f):
    hero_blocks = []
    for line in f:
        if line.startswith(_start_hero_pattern):
            hero_block = get_hero_block(f, line)
            hero_blocks.append(hero_block)
    return hero_blocks


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

    item_name = line.split(_start_item_pattern)[1].rstrip('"\t\n')
    f.readline()
    n_open = 1
    pass

def parse_abilities(f):
    blocks = []
    for line in f:
        if (line.startswith(_start_ability_pattern) and
                not line.startswith('\t"Version"')):
            block = get_ability_block(f, line)
            blocks.append(block)
    ability_d = {}

    for ability in blocks:
        ability_d[ability[0][1]] = dict(ability[1:])

    return ability_d

def get_ability_block(f, line):

    results = get_block(f, line, kind='ability')

    return results

def get_block(f, line, kind):
    if kind == 'hero':
        name = line.split(_start_hero_pattern)[1].rstrip('"\t\n')
    elif kind == 'ability':
        name = line.strip().strip('"')
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

def main(infile):
    """
    infile should be npc_heros.txt
    """
    with open(infile, 'r') as f:
        parse_heros(f)
