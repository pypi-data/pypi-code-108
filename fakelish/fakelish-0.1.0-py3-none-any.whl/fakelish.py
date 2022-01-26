from __future__ import annotations

import importlib.resources
import json
import random

WORD_PROBABILITY_FILENAME = "word-probability.json"

WORD_PROBABILITY = None


def generate_fake_word_with_unexpected_length():
    global WORD_PROBABILITY

    if WORD_PROBABILITY is None:
        with importlib.resources.open_text(
            "fakelish", WORD_PROBABILITY_FILENAME
        ) as read_file:
            WORD_PROBABILITY = json.load(read_file)

    max_seq = 2
    ch = "^"
    fake_word = ""
    chrs = []
    while ch != "END":
        chrs.append(ch)
        if len(chrs) > max_seq:
            chrs = chrs[1:]

        next_accumed_probs = []
        n = 0
        while True:
            string = "".join(chrs[n:])
            next_accumed_probs = WORD_PROBABILITY.get(string)
            n += 1
            if not (next_accumed_probs is None and n < len(chrs)):
                break

        next_ch = ""
        r = random.random()
        for x in next_accumed_probs:
            x_ch, x_prob = x
            candidate_next_ch = x_ch

            if r <= x_prob:
                next_ch = candidate_next_ch
                break

        if next_ch != "END":
            fake_word += next_ch

        ch = next_ch

    return fake_word


def generate_fake_word_by_length(length):
    fake_word = ""
    while len(fake_word) != length:
        fake_word = generate_fake_word_with_unexpected_length()
    return fake_word


def generate_fake_word(minLength, maxLength):
    fake_word = ""
    while not (minLength <= len(fake_word) and len(fake_word) <= maxLength):
        fake_word = generate_fake_word_with_unexpected_length()
    return fake_word
