import datetime
import io
import json
import logging
import pathlib
import random
import sys

import appdirs
import diskcache
import humanfriendly
import requests

cache_path = pathlib.Path(appdirs.user_cache_dir(appname="clinepunk"))
url = (
    "https://raw.githubusercontent.com/dwyl/english-words/master/words_dictionary.json"
)


def refresh_cache():
    r = requests.get(url)

    if r.status_code == 200:
        dct = r.json()
        js = json.dumps(dct, indent=2).encode("utf-8")
        return js
    return ""


def get_words(count=1):
    js = ""
    with diskcache.Cache(cache_path) as reference:
        result = reference.get("clinepunk.words")
        if not result:
            logging.debug("setting cache")
            js = refresh_cache()
            reference.set(
                "clinepunk.words",
                io.BytesIO(js),
                expire=datetime.timedelta(days=365 * 2).total_seconds(),
            )
        else:
            logging.debug("cache is still fresh, using it")
            reader = result
            js = reader.read().decode()

    words = json.loads(js)
    words = words.keys()
    words = list(filter(lambda x: len(x) <= 5, words))

    logging.debug(f"cache path is {cache_path}")
    logging.debug(f"cache has {len(words):,d} words")
    logging.debug(
        f"cache has size {humanfriendly.format_size(cache_path.stat().st_size, binary=True)}"
    )

    sample = random.sample(words, count)
    logging.debug(f"sample words is {sample}")

    return sample


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="{%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(f"{pathlib.Path(__file__).stem}.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    words = get_words(count=2)
    out = "".join(words)
    print(out)


if __name__ == "__main__":
    main()
