import traceback


def stripped_traceback(
    nostrip=0,
    formatted_exc=None,
    zope_match='Zope',
    zope_match2='zope',
    monkey_match='in monkey_exec',
    logging_exec_match='logging_exec',
):
    """ remove internals from a traceback.format_exc() structure
    Default is to remove Zope internals.
    """
    formatted_exc = formatted_exc or traceback.format_exc()
    tbr = formatted_exc.splitlines()
    if nostrip:
        return tbr
    tb = []
    i = -1
    while i < len(tbr) - 1:
        i += 1
        line = tbr[i]
        if line.endswith(monkey_match):
            i += 3
            continue

        if zope_match in line or zope_match2 in line or logging_exec_match in line:
            if tb[-1] != '    internal...':
                tb.append('    internal...')
            i += 1
            continue

        # good one append it:
        tb.append(line)
    # strip the v1 error handler itself from the traceback:
    if len(tb) > 3 and tb[-2].endswith('in err'):
        tbr = tb[:-3]
    else:
        tbr = tb
    return tbr
