"""
Hilites serializable structers in the terminal.

json, yml for now

"""
# TODO: perf improvement for python objects: the serialization / parsing in again
# by pygments can be avoided by tokenizing directly based on the nature of the
# objects.
# But: This is anyway mainly for foreground, i.e. debugging...

from json import dumps

from ax.utils.six import StringIO
from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers import JsonLexer, YamlLexer
from yaml import dump, safe_dump

ysl = ytermf = jsl = termf = ''


def coljhighlight(s):
    global jsl, termf
    if not jsl:
        jsl = JsonLexer()
        termf = TerminalFormatter(bg='dark')
    io = StringIO()
    if not isinstance(s, basestring):
        s = dumps(s, indent=4, sort_keys=1, default=str)
    highlight(s, jsl, termf, io)
    res = io.getvalue()
    io.close()
    return res.replace('\\n', '\n')


def colyhighlight(s):
    global ysl, ytermf
    if not ysl:
        ysl = YamlLexer()
        ytermf = TerminalFormatter(bg='dark')
    io = StringIO()
    if not isinstance(s, basestring):
        try:
            s = safe_dump(s)
        except:
            s = dump(s, default_flow_style=False)
    highlight(s, ysl, ytermf, io)
    res = io.getvalue()
    io.close()
    return res
