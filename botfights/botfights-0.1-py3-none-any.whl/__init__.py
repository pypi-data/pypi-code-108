import importlib.util
import logging
import os
import pathlib
from typing import Optional

import fire
import pkg_resources

from botfights.wordle.wordle import get_random, load_wordlist, play_botfights, play_bots


def _gen_implementations():
    for entry_point in pkg_resources.iter_entry_points("botfights.wordle.guesser"):
        factory_func = entry_point.load()
        yield entry_point.name, factory_func


def get_implementations():
    return dict(_gen_implementations())


def wordle(
    guesser: str,
    seed: str = "",
    num: int = 0,
    event: Optional[str] = None,
    wordlist: str = "bot",
    fraction: float = 1.0,
):
    get_random().seed(seed)

    wordlist = load_wordlist(wordlist, fraction)
    if "::" in guesser:
        path, cls_name = guesser.split("::")
        path = pathlib.Path(path)
        spec = importlib.util.spec_from_file_location(path.stem, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        cls = getattr(mod, cls_name)
        bot_name = f"{mod.__name__}.{cls.__name__}"
    else:
        bot_name = guesser
        cls = get_implementations()[bot_name]

    bot = cls(wordlist)

    if event is None:
        return play_bots({bot_name: bot}, wordlist, num)
    else:
        return play_botfights(
            bot, os.environ["BOTFIGHTS_USER"], os.environ["BOTFIGHTS_PASS"], event
        )


def main():
    logging.basicConfig(level=logging.INFO)
    fire.Fire({func.__name__: func for func in [wordle]})
