#!/usr/bin/env python
from __future__ import print_function
import logging, os

# complete -C /uscms/home/klijnsma/packages/toscript/completion.py to

import sys, seutils
logger = seutils.logger
logger.setLevel(logging.ERROR)
seutils.cli_detect_fnal()

DO_LOGGING = False

def completion_hook(cmd, prev_word, curr_word, line):
    log('\ncmd="{}" prev_word="{}" curr_word="{}" line="{}"'.format(cmd, prev_word, curr_word, line))
    hook = cmd_to_hook.get(cmd, None)
    if not hook:
        print('Not recognizing command {}'.format(cmd))
        return
    hook(cmd, prev_word, curr_word, line)

def cannot_expand():
    logger.error(
        'Cannot expand: Start paths with the full mgm (root://...) or set the %s environment variable',
        seutils.MGM_ENV_KEY
        )

def log(*args, **kwargs):
    if DO_LOGGING:
        logger.error(*args, **kwargs)

def complete_ls(cmd, prev_word, curr_word, line):
    if line.strip() == 'seu-ls':
        # Only the plain command is being expanded
        if seutils.DEFAULT_MGM is None:
            cannot_expand()
        else:
            print(seutils.cli_flexible_format('').strip())
        return
    elif line.endswith(' '):
        log('Already expanded')
        # Already expanded
        return
    else:
        # Get the thing to expand
        raw_lfn = line.split()[-1].strip()

    log('Raw lfn %s', raw_lfn)
    # Do some formatting
    if seutils.is_ssh(raw_lfn):
        lfn = raw_lfn
    elif not seutils.has_protocol(raw_lfn):
        if seutils.DEFAULT_MGM is None:
            cannot_expand()
            return
        lfn = seutils.cli_flexible_format(raw_lfn)
    else:
        lfn = raw_lfn
    log('Using lfn %s', lfn)

    # Do expansion
    if lfn.endswith('/'):
        contents = seutils.listdir(lfn)
    else:
        contents = seutils.ls_wildcard(lfn + ('' if lfn.endswith('*') else '*'))

    # Print carefully
    if len(contents) == 0:
        log('No contents to expand')
        return

    elif len(contents) > 1:
        log('Multiple contents')

        expand_to = find_longest_matching_start(contents)
        log('Maximum expand string: %s', expand_to)

        if expand_to.strip() == lfn.strip():
            log('lfn %s already maximally expanded, printing contents', lfn)
            print(' ' + '\n'.join(contents))
        else:
            log('Only printing expansion %s', expand_to)
            if ':' in raw_lfn:
                print(expand_to.split(':')[-1].strip())
            else:
                print(expand_to.strip())
    else:
        log('Single content')
        c = contents[0]
        if seutils.isdir(c): c += '/'
        # The ':' counts as a splitting in `complete`... Only print whatever comes after the ':'
        if ':' in raw_lfn:
            print(c.split(':')[-1])
        else:
            print(c)


def find_longest_matching_start(lines):
    """
    Finds longest expansionable string
    """
    max_len = max(map(len, lines))
    try:
        break_now = False
        for i in range(max_len):
            char = lines[0][i]
            for line in lines:
                if line[i] != char:
                    # Matching breaks at character index i
                    break_now = True
                    break
            if break_now: break
    except IndexError:
        pass
    return lines[0][:i]

cmd_to_hook = {
    'seu-ls' : complete_ls,
    }

def main():
    args = sys.argv
    cmd = args[1]
    prev_word = args[3]
    curr_word = args[2]
    line = os.environ['COMP_LINE']
    completion_hook(cmd, prev_word, curr_word, line)

if __name__ == "__main__":
    main()