from __future__ import absolute_import, division, print_function

from .term import I, L, M, R

"""Some Terminal Messages used repeatedly"""


def DeprecationMessage(msg, ticket=None, alternatives=(), eol=None):
    s = ', '.join([M(a) for a in alternatives])
    if s:
        s = 'Alternatives: ' + s
    if eol:
        s = 'End of live: %s' % I(eol)
    if ticket:
        s += ' ' + L('[%s]' % ticket)
    return '\n'.join([R('%s' % msg.upper()), '', s])
