#!/usr/bin/env python

import setuptools

setuptools.setup(
    name="wordlebot",
    install_requires=["more_itertools"],
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    entry_points={
        "botfights.wordle.guesser": [
            "max_entropy = wordlebot.guessing:MaxEntropyGuesser",
            "maximin_surprise = wordlebot.guessing:MaximinSurpriseGuesser",
            "cheap_heuristic = wordlebot.guessing:CheapHeuristicGuesser",
            "simple = wordlebot.guessing:SimpleGuesser",
        ],
    },
)
