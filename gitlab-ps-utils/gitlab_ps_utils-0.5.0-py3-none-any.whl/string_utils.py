from base64 import b64decode, b64encode
import getpass
import sys
from re import sub


def strip_numbers(s):
    """
        Strip out any numbers from a string

        :param s: (str) the string containing numbers
        :return: (str) string without numbers
    """
    return sub(r"[0-9]+", '', s)


def convert_to_underscores(s):
    """
        Converts ' ', '/', '.', ':' to underscores

        :param s: (str) the string containing spaces, slashes, periods, or colons
        :return: (str) string without those characters
    """
    return sub(r" |\/|\.|\:", "_", s)


def clean_split(s, *args, **kwargs):
    """
        Returns split string without any empty string elements

        :param: s: (str) the string to split
        :param: *args, **kwargs: any arguments you need to pass to the split function

        example usage:

        s = "hello/world"
        clean_split(s, "/")
        ['hello', 'world']
    """
    return list(filter(None, s.split(*args, **kwargs)))


def obfuscate(prompt):
    return b64encode(getpass.getpass(prompt).encode("ascii")).decode("ascii")


def deobfuscate(secret):
    try:
        return b64decode(secret.encode("ascii")).decode("ascii")
    except Exception as e:
        print(f"Invalid token - {e}")
        sys.exit()
