import re

from theming.unicode_chars import UCs


class BPFormat(object):
    """ bpython (curses?) format strings.
    Note: if it turns out they are curses complient then subclass.

    \x01 represents a colour marker, which
    can be proceded by one or two of
    the following letters:
    k, r, g, y, b, m, c, w, d
    Which represent:
    blacK, Red, Green, Yellow, Blue, Magenta,
    Cyan, White, Default
    e.g. \x01y for yellow,
         \x01G   Bold green
         \x01gb for green on blue background
         \x01gI  Inverse

    \x03 represents the start of the actual
        text that is output (in this case it's
        a %s for substitution)

    \x04 represents the end of the string; this is
        necessary because the strings are all joined
        together at the end so the parser needs them
        as delimeters
    """

    csi = '\x03'
    reset = '\x04'
    # K comes out as green strong on my term. have to investigate:
    color_map = {
        'green_strong': 'G',
        'black': 'k',
        'red': 'r',
        'green': 'g',
        'yellow': 'y',
        'blue': 'b',
        'magenta': 'm',
        'cyan': 'c',
        'white': 'w',
    }

    @staticmethod
    def format(s, col, bg=None, bold=False, inverse=False, reset=True):
        """ format('foo', 'green')"""
        r = BPFormat.reset
        if not reset:
            r = ''
        if len(col) == 2:
            # gI
            col, bg = col
        if col == col.upper():
            # GREEN
            col = col.lower()
            bold = 1
        elif not len(col) == 1:
            # green
            col = BPFormat.color_map[col]
        if bold:
            col = col.upper()
        if bg:
            if len(bg) != 1:
                col += BPFormat.color_map[bg]
            else:
                col += bg
        else:
            if inverse:
                col += 'I'
        res = '\x04\x01%s\x03%s%s' % (col, s, r)
        return res

    # --------------------------- any process can overwrite these to his liking:
    # debug, info, important, warn, alarm:
    cols = ['b', 'c', 'G', 'GI', 'RI']

    @staticmethod
    def fmt_debug(s):
        return BPFormat.format(s, BPFormat.cols[0])

    @staticmethod
    def fmt_info(s):
        return BPFormat.format(s, BPFormat.cols[1])

    @staticmethod
    def fmt_important(s):
        return BPFormat.format(s, BPFormat.cols[2])

    @staticmethod
    def fmt_warn(s):
        return BPFormat.format(s, BPFormat.cols[3])

    @staticmethod
    def fmt_alarm(s):
        return BPFormat.format(s, BPFormat.cols[4])

    # can be set by processes, like config mgmt for [D]...[S]... matches:
    #  {re.compile(r'(\[D\]\w*)'): 'info'} -> show all "foo [D]bar baz" in info color
    rules = {}
    # if order is wanted:
    rules_list = []
    for table_char in UCs.VU, UCs.JUNC, UCs.H, UCs.GOOD:
        rules_list.append([re.compile(r'(%s)' % table_char), 'g'])
    rules_list.append([re.compile(r'(%s)' % UCs.BAD), 'R'])

    @staticmethod
    def fmt(s):
        # first the list, order here, map rules than won't match:
        F = BPFormat
        l = [F.rules_list, F.rules.items()]
        for p in l:
            for match, rule in p:
                func = getattr(F, 'fmt_%s' % rule, 0)
                if func:
                    # rule is like 'info'
                    s = match.sub(func('\\1'), s)
                else:
                    # rule is a color:
                    s = match.sub(F.format('\\1', rule), s)
        return s


if __name__ == '__main__':
    # run this in bpython to see, normal shell should show unchanges output:
    BPFormat.rules = {re.compile(r'(\[D\]\w*)'): 'info'}
    print(BPFormat.fmt('foo [D]daemonname[S]other\nbar [D]daemon2'))
