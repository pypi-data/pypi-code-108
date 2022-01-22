"""Utility file containg helper functions"""
import argparse


def convert_to_string(bits):
    """
    Converts bits to string
    Parametes:
        Binary bits 1's and 0's
    Returns:
        String (sentences, words)
    """
    string = ""
    for i in range(0, len(bits), 8):
        char_bin = bits[i:i+8]
        char_int = int(char_bin, 2)
        char = chr(char_int)
        string += char
    return string


def convert_to_bits(string):
    """
    Converts string to bits
    Parameters:
        String (sentences, words)

    Returns:
        Binary bits 1's and 0's
    """

    bits = ""
    for char in string:
        # convert char to int
        char_int = ord(char)
        # convert int to binary
        char_bin = bin(char_int)[2:]
        # add 0's to binary to make it 8 bits
        char_bin = char_bin.zfill(8)
        bits += char_bin
    return bits


def banner():
    """ Prints banner """

    banner_string = """
**DDNA - DNA Encoder/Decoder**

O       o O       o O       o
A O   o | A O   o | | O   o G
| G O | C 1 | O G | T | O | 1
1 o   O | T o   O A | o   O C
o       O o       O o       O

               aayushp.com.np
"""
    print(banner_string)


def arguments():
    """
    Parses arguments from terminal
    """
    parser = argparse.ArgumentParser(
        description="DDNA - DNA Encoder/Decoder")
    parser.add_argument(
        "-e", "--encode", help="Encode String to DNA", type=str)
    parser.add_argument(
        "-d", "--decode", help="Decode DNA to String", type=str)
    args = parser.parse_args()
    return args
