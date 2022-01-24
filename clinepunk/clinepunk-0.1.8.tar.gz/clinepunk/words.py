import bisect
import io
import logging
import pathlib
import pickle
import random
import sys
import typing

import appdirs
import requests

from clinepunk import cache as cachemod
from clinepunk import model

url = "https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english-no-swears.txt"


def refresh_cache() -> typing.List[model.Word]:
    logging.debug(f"fetching {url}")
    response = requests.get(url)
    logging.debug(f"{response.status_code=}")
    if response.status_code != 200:
        logging.warning(f"couldn't fetch {url}")

    text = response.text

    words = []
    for word in text.splitlines():
        bisect.insort(words, model.Word(length=len(word), word=word))

    col = model.WordCollection(words)
    buffer = io.BytesIO()
    pickle.dump(col, buffer)

    return buffer


def find_filter(words, min_length=3, max_length=7):
    return filter(lambda s: s.length > min_length and s.length <= max_length, words)


def get_words(count=2):
    cache_path = pathlib.Path(appdirs.user_cache_dir(appname="clinepunk"))
    buffer = cachemod.cache(cache_path, refresh_cache, "clinepunk.words2")
    print(type(buffer))
    col = pickle.loads(buffer.getbuffer())
    logging.debug(f"word collection has {len(col.words)} words")
    print(type(col))
    words = list(find_filter(col.words))
    logging.debug(f"{len(words)} match query")

    sample = random.sample(words, count)

    return [x.word for x in sample]


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="{%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(f"{pathlib.Path(__file__).stem}.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    lst = get_words(count=2)
    out = "".join(lst)
    logging.debug(out)
    return out


if __name__ == "__main__":
    main()
