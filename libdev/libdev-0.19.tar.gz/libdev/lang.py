"""
Natural language processing functionality
"""

def get_form(count, variations):
    """ Get form of a noun with a number """

    count = abs(count)

    if count % 10 == 1 and count % 100 != 11:
        return variations[0]

    if count % 10 in (2, 3, 4) and count % 100 not in (12, 13, 14):
        return variations[1]

    return variations[2]
