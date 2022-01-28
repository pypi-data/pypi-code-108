#!/usr/bin/env python
#
#
# Author: Thamme Gowda
# Created: 10/17/21
import collections as coll
import sys
import argparse

from mtdata import __version__, log
from mtdata.index import get_entries, bcp47, is_compatible

exclusions = [
    'jw300-1-',  # we have newer version
    'qed-2.0a-'  # for research purpose only
]


def parse_version(txt):
    # noinspection PyBroadException
    try:
        return float(txt), ''
    except:
        return 1, txt


def filter_english_entries():
    entries = get_entries()
    log.info(f"Found {len(entries):,} sets in my index")
    eng = bcp47('eng')
    entries = [e for e in entries
               if is_compatible(eng, e.did.langs[0]) or is_compatible(eng, e.did.langs[1])]
    log.info(f"Found {len(entries):,} sets have English on either source or target side")
    entries = [e for e in entries if not any(x in str(e.did) for x in exclusions)]
    log.info(f"Found {len(entries):,} after removing exclusions : {exclusions}")
    # versioned entries
    """
    ver_entries = coll.defaultdict(set)
    for e in entries:
        did = e.did
        xxx = did.langs[1].lang if is_compatible(eng, did.langs[0].lang) else did.langs[0].lang
        key = (xxx, did.group, did.name)
        ver_entries[key].add((did.version, e))
    log.info(f"Excluding older versions: {len(ver_entries):,} ")
    lang_entries = coll.defaultdict(set)
    for (xxx, group, name), sets in ver_entries.items():
        # reverse sort (version, entry) items
        sorter_set = sorted(sets, reverse=True, key=lambda x: parse_version(x[0]))
        recent_version = list(sorter_set)[0][1]  # the top 1
        lang_entries[xxx].add(recent_version)
    n_selected_entries = sum(len(v) for v in lang_entries.values())
    """
    lang_entries = coll.defaultdict(set)
    for e in entries:
        did = e.did
        xxx = did.langs[1].lang if is_compatible(eng, did.langs[0].lang) else did.langs[0].lang
        lang_entries[xxx].add(e)
    n_selected_entries = sum(len(v) for v in lang_entries.values())
    log.info(f"Total languages={len(lang_entries):,} || total datasets selected={n_selected_entries:,}")
    # sort based on descending order of number of entries
    lang_entries = list(sorted(lang_entries.items(), key=lambda x: len(x[1]), reverse=True))
    sep = '\t'
    print('Lang', '#sets', 'Trains', 'Devs', 'Tests', sep=sep)
    for i, (xxx, sets) in enumerate(lang_entries, start=1):
        devs = []
        tests = []
        trains = []
        for s in sets:
            name = s.did.name
            did = str(s.did)
            if 'test' in name:
                tests.append(did)
            elif 'dev' in name:
                devs.append(did)
            else:
                trains.append(did)
        trains, devs, tests = [x and ', '.join(sorted(x)) or '' for x in [trains, devs, tests]]
        print(xxx, len(sets), trains, devs, tests, sep=sep)


def main(**kwargs):
    filter_english_entries()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-vv', '--verbose', action='store_true', help='verbose mode')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')

    parser.add_argument("-i", "--inp", type=argparse.FileType('r', encoding='utf-8'), default=sys.stdin,
                        help="Input file. Default: STDIN")
    parser.add_argument("-o", "--out", type=argparse.FileType('w', encoding='utf-8'), default=sys.stdin,
                        help="Input file. Default: STDOUT")
    args = parser.parse_args()
    if args.inp is sys.stdin or args.out is sys.stdout:
        assert sys.getdefaultencoding().lower() in ('utf-8', 'utf8'), \
            f'Please set PYTHONIOENCODING=utf-8; Current encoding: {sys.getdefaultencoding()}'
    return args


if __name__ == '__main__':
    main()
