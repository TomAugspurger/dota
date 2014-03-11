import os
import re
import json

import dota
from dota import api

with open(os.path.expanduser('~/Dropbox/bin/api-keys.txt')) as f:
    key = json.load(f)['steam']

h = api.API(key=key)

p = os.path.join(os.path.dirname(dota.__file__),
                 'pro_match_ids.txt')
with open(p) as f:
    match_ids = [x.strip() for x in f.readlines()]

matches = filter(None, map(lambda x: re.match(r'.*(\d{9}).json$', x),
                           os.listdir('../data/pro/')))
matches = [x.groups()[0] for x in matches]
new_matches = [x for x in match_ids if x not in matches]
new_matches

details = {mid: h.get_match_details(mid) for mid in new_matches}
details = {}
there = '../data/pro/'

try:
    os.makedirs(there)
except FileExistsError:
    pass

for k in details:
    with open(there + k + '.json', 'w') as f:
        json.dump(details[k].resp, f)
