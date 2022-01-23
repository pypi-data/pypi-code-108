#!/usr/bin/env python3
# coding: utf-8
import argparse
import re
import shlex


def extract_case(path, title='subcmd'):
    text = open(path).read()
    regex = re.compile(
        r'case\s+(.*?)\s+in(.*?)\besac\b',
        re.DOTALL | re.MULTILINE,
    )
    for mat in regex.finditer(text):
        if mat and title in mat.group():
            return mat


def quotation_closed(s):
    try:
        return shlex.split(s)
    except ValueError:
        pass


def extract_pat_from_entry(entry):
    cnt = entry.count(')')
    while True:
        idx = entry.find(')')
        if idx == -1:
            break
        pat = entry[:idx]
        if not pat or pat[-1] == '\\':
            break
        if quotation_closed(pat):
            return pat


def extract_pats(text):
    for entry in text.split(';;'):
        pat = extract_pat_from_entry(entry)
        if pat:
            yield pat


def run(prog, args):
    desc = 'extract patterns of a case construct from a shell script'
    pr = argparse.ArgumentParser(prog=prog, description=desc)
    aa = pr.add_argument
    aa('path', metavar='PATH', help='path to a shell script')
    aa('title', default='subcmd', nargs='?')
    ns = pr.parse_args(args)
    mat = extract_case(ns.path, ns.title)
    if not mat:
        return
    pats = []
    for pat in extract_pats(mat.group(2)):
        pat = ' '.join(shlex.split(pat, comments=True))
        pats.append(pat)
    if pats:
        print(ns.title + ':')
        for pat in pats:
            print('-', pat)
