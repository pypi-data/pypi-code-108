"""reads pluralization formulae from the .po files
and prints out list of languages for each formula"""

import sys
import os.path
import collections

def find_formula(item):
    return item.startswith('"Plural-Forms:')

lang_codes = collections.defaultdict(set)

for filename in sys.argv:
    if not filename.endswith('.po'):
        continue
    lines = open(filename).readlines()
    formula = list(filter(find_formula, lines))[0]
    lang = os.path.dirname(os.path.dirname(filename))
    lang_codes[formula].add(lang.split('/')[-1])

for formula in lang_codes:
    print(lang_codes[formula])
    print(formula)
