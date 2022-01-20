# Mixed utilities
#
# Author: F. Mertens

import itertools
import astropy.time as at


def alphanum(s):
    return "".join(filter(str.isalnum, s))


def all_same(l):
    return not l or l.count(l[0]) == len(l)


def all_in_other(l, other):
    return all(elem in other for elem in l)


def get_lst(obs_mjd, longitude=6.57):
    return at.Time(obs_mjd, scale='utc', format='mjd').sidereal_time('mean', longitude=longitude).value


def is_in_lst_bin(lst, lst_s, lst_e):
    if lst_s == lst_e:
        return False
    if lst_e > lst_s:
        return (lst >= lst_s) and (lst < lst_e)
    return (lst >= lst_s) or (lst < lst_e)


def pairwise(iterable):
    '''s -> (s0,s1), (s1,s2), (s2, s3), ...'''
    a, b = itertools.tee(iterable)
    next(b, None)
    return list(zip(a, b))
