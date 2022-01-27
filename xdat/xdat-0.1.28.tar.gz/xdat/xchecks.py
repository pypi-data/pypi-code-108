import numpy as np


def check_equals(a1, a2, sort=False):
    """
    checks that two arrays are the same

    :param sort: if True, sorts the arrays first
    """

    assert len(a1) == len(a2)
    assert a1.shape == a2.shape

    if sort:
        a1.sort()
        a2.sort()

    assert (a1 == a2).sum() == a1.size


def check_same_sets(sa1, sa2):
    """
    checks that two arrays contain the same items, irregardless of sort & repeats
    """
    a1 = np.unique(sa1)
    a2 = np.unique(sa2)

    check_equals(a1, a2, sort=True)


def check_no_dups(sa):
    """
    checks that array does not contain duplicates
    """
    assert len(sa) == len(np.unique(sa))

