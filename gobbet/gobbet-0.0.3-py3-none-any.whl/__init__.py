from gobbet.wordlist import Wordlist
from gobbet.downloader import news_dir, get_articles_json
from gobbet.parser import parse_dump
import pickle
import os
from youseedee import parse_file_ranges
from collections import defaultdict


unicode_ranges = defaultdict(list)
for s, e, c in parse_file_ranges("Scripts.txt"):
    unicode_ranges[c].append(range(s, e + 1))


def filter_length(items, threshold=3):
    return [x for x in items if len(x) >= threshold]


def filter_unicodes(items, codepoint_ranges):
    def _included_letter(l):
        return any(ord(l) in r for r in codepoint_ranges)

    def _included(word):
        return all(_included_letter(l) for l in word)

    return [x for x in items if _included(x)]


def get_news(lang="en", force=False):
    return get_source(lang, force, which="wikinews")

def get_source(lang="en", force=False, which="wikinews"):
    source_path = os.path.join(news_dir(), f"{lang}.pickle")
    if os.path.isfile(source_path) and not force:
        with open(source_path, "rb") as pickle_file:
            news = pickle.load(pickle_file)
        return news["words"], news["headlines"], news["paragraphs"]

    news = parse_dump(get_articles_json(lang, force=force, which=which))

    with open(source_path, "wb") as pickle_file:
        pickle.dump(news, pickle_file)
    return news["words"], news["headlines"], news["paragraphs"]
