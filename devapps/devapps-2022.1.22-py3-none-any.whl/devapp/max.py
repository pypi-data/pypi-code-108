import os
import sys

from mdvl import to_md_list


def explain_parse_options():
    """max_explain docstrings can do that passing the file as sys.argv[1]
    In the file we parse the matching occurrance of a switch case statement like
    the one in the max_function file.
    Debug this by printing out - will result in the docstring shown.
    """
    match = sys.argv[1]

    fn = sys.argv[2]
    if not os.path.exists(fn):
        print('Options parser: not found file given by docstring (%s)' % fn)
        return
    with open(fn) as fd:
        s = fd.read()
    block = []
    have = False
    is_match = False
    for line in s.splitlines():
        line = line.strip()
        if match in line:
            is_match = True
        if line == 'esac':
            if is_match:
                have = True
                break
        else:
            if is_match:
                block.append(line)
    if not have or not block:
        print('No case declaration found in', fn)
    # options now like:
    # -d|deactivate)
    # deactivate
    # return $?
    # ;;
    # -w|--welcome)
    keys = []
    shorts = []
    funcs = []
    while len(block) > 1:
        line = block.pop(0)
        if line == '*)':
            continue

        if line.endswith(')'):
            if not '|' in line:
                line = '|' + line
            l = line.split('|', 1)
            shorts.append(l[0].strip())
            keys.append(l[1].split(')', 1)[0].strip())
            while block and 'shift' in block[0]:
                block.pop(0)
            if block:
                funcs.append(block.pop(0))

    out = to_md_list(shorts, keys, funcs)
    print(out)
