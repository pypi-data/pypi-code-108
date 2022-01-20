import sys
import unicodedata


def get_unicode_space_characters():
    """ Returns all unicode characters in the "seperator, space" category (Zs)"""
    # Based on https://stackoverflow.com/questions/14245053/how-can-i-get-all-whitespaces-in-utf-8-in-python
    spaces = []
    for i in range(sys.maxunicode + 1):
        if unicodedata.category(chr(i)) == 'Zs':
            spaces.append(chr(i))
    return spaces
