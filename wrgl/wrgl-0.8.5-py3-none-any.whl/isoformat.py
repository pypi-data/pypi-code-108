import datetime


# Helpers for parsing the result of isoformat()
def _parse_isoformat_date(dtstr):
    # It is assumed that this function will only be called with a
    # string of length exactly 10, and (though this is not used) ASCII-only
    year = int(dtstr[0:4])
    if dtstr[4] != '-':
        raise ValueError('Invalid date separator: %s' % dtstr[4])

    month = int(dtstr[5:7])

    if dtstr[7] != '-':
        raise ValueError('Invalid date separator')

    day = int(dtstr[8:10])

    return [year, month, day]


def _parse_hh_mm_ss_ff(tstr):
    # Parses things of the form HH[:MM[:SS[.fff[fff]]]]
    len_str = len(tstr)

    time_comps = [0, 0, 0, 0]
    pos = 0
    for comp in range(0, 3):
        if (len_str - pos) < 2:
            raise ValueError('Incomplete time component')

        time_comps[comp] = int(tstr[pos:pos+2])

        pos += 2
        next_char = tstr[pos:pos+1]

        if not next_char or comp >= 2:
            break

        if next_char != ':':
            raise ValueError('Invalid time separator: %c' % next_char)

        pos += 1

    if pos < len_str:
        if tstr[pos] != '.':
            raise ValueError('Invalid microsecond component')
        else:
            pos += 1

            len_remainder = len_str - pos
            if len_remainder not in (3, 6):
                raise ValueError('Invalid microsecond component')

            time_comps[3] = int(tstr[pos:])
            if len_remainder == 3:
                time_comps[3] *= 1000

    return time_comps


def _parse_isoformat_time(tstr):
    # Format supported is HH[:MM[:SS[.fff[fff]]]][+HH:MM[:SS[.ffffff]]]
    len_str = len(tstr)
    if len_str < 2:
        raise ValueError('Isoformat time too short')

    # This is equivalent to re.search('[+-]', tstr), but faster
    tz_pos = max(tstr.find('-'), tstr.find('+'), tstr.find('Z'))
    timestr = tstr[:tz_pos] if tz_pos > 0 else tstr

    time_comps = _parse_hh_mm_ss_ff(timestr)

    tzi = None
    if tz_pos > 0:
        tzstr = tstr[tz_pos:]

        # Valid time zone strings are:
        # Z                     len: 1
        # [+-]HH:MM             len: 6
        # [+-]HH:MM:SS          len: 9
        # [+-]HH:MM:SS.ffffff   len: 16

        if len(tzstr) not in (1, 6, 9, 16):
            raise ValueError('Malformed time zone string')

        if tzstr == 'Z':
            tzi = datetime.timezone.utc
        else:
            tz_comps = _parse_hh_mm_ss_ff(tzstr[1:])
            if all(x == 0 for x in tz_comps):
                tzi = datetime.timezone.utc
            else:
                tzsign = -1 if tstr[tz_pos] == '-' else 1

                td = datetime.timedelta(hours=tz_comps[0], minutes=tz_comps[1],
                                        seconds=tz_comps[2], microseconds=tz_comps[3])

                tzi = datetime.timezone(tzsign * td)

    time_comps.append(tzi)

    return time_comps


def fromisoformat(date_string):
    """Construct a datetime from the output of datetime.isoformat()."""
    if not isinstance(date_string, str):
        raise TypeError('fromisoformat: argument must be str')

    # Split this at the separator
    dstr = date_string[0:10]
    tstr = date_string[11:]

    try:
        date_components = _parse_isoformat_date(dstr)
    except ValueError:
        raise ValueError(f'Invalid isoformat string: {date_string!r}')

    if tstr:
        try:
            time_components = _parse_isoformat_time(tstr)
        except ValueError:
            raise ValueError(f'Invalid isoformat string: {date_string!r}')
    else:
        time_components = [0, 0, 0, 0, None]

    return datetime.datetime(*(date_components + time_components))
