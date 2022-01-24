# Copyright 2020 Splunk Inc. All rights reserved.

"""
A naive bias language scanner.
It flags any words contained in bias_wordlist.txt, optionally with prefixes and suffixes "_ . /".
"""

import os
import re

from splunk_appinspect.offense import get_mime_type

exceptions = [""]
prefixes = ["", "_", ".", "/"]
suffixes = ["", "_", ".", "/"]

with open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "bias_wordlist.txt")
) as _file:
    words_array = []
    for _line in _file:
        bias_word = _line.strip().lower()
        for prefix in prefixes:
            words_array.append((prefix + bias_word, bias_word))
        for suffix in suffixes:
            words_array.append((bias_word + suffix, bias_word))
    words = dict(words_array)


def word_is_bias(word):
    """
    Match a single word against the bias_wordlist
    """
    lc_word = word.lower()
    if lc_word in exceptions:
        return None
    if lc_word in words:
        return word, words[lc_word]

    return None


def scan_file_for_bias(filename):
    """
    Tokenize into single words, and match each against the bias word list.
    Notice: The get_mime_type method should only be used in Unix environment.
    """
    results = set()
    if get_mime_type(filename).find("text") == -1:
        # Skip binary files
        return results

    file = open(filename, "r", errors="ignore")
    line_nunmber = 0
    for line in file:
        line_nunmber += 1
        for word in re.split(r"\W+", line):
            match = word_is_bias(word)
            if match:
                results.add((line_nunmber, line.strip(), match[0], match[1]))
    file.close()
    return results
