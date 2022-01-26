"""
Defines a Graph-Easy extension that overrides code block rendering if the
language type is 'grapheasy', 'dot', 'vcg', or 'gdl'.
"""


import urwid
import subprocess


from lookatme.exceptions import IgnoredByContrib


def user_warnings():
    return [
        'Requires graph-easy and graphviz be installed and in your path',
        'See https://github.com/codybuell/lookatme.contrib.grapheasy for more info'
    ]


def render_code(token, body, stack, loop):
    lang = token["lang"] or ""
    if lang not in ['grapheasy', 'dot', 'vcg', 'gdl']:
        raise IgnoredByContrib()

    # deal with any double quotes in the code block
    code_block = token['text'].replace('"', '\\"')

    # build and run our command
    command = 'echo "' + code_block + '" | graph-easy --as=boxart'
    cmd_out = subprocess.check_output(command, shell=True, encoding='utf-8')

    return urwid.Text(cmd_out)
