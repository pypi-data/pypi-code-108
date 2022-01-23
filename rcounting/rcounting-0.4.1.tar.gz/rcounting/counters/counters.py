import os
from pathlib import Path

module_dir = os.path.dirname(__file__)

with open(module_dir / Path("aliases.txt"), "r", encoding="utf8") as f:
    alias_list = f.readlines()
alias_list = [x.strip().split(",") for x in alias_list]
alias_dict = {}
for aliases in alias_list:
    for alias in aliases:
        alias_dict[alias] = aliases[0]


def apply_alias(username):
    return alias_dict[username] if username in alias_dict else username


mods = [
    "Z3F",
    "949paintball",
    "zhige",
    "atomicimploder",
    "ekjp",
    "TheNitromeFan",
    "davidjl123",
    "rschaosid",
    "KingCaspianX",
    "Urbul",
    "Zaajdaeon",
]


def is_mod(username):
    return username in mods


ignored_counters = ["LuckyNumber-Bot", "CountingStatsBot", "CountingHelper", "WikiSummarizerBot"]
ignored_counters = [x.lower() for x in ignored_counters]
banned_counters = ["[deleted]", "Franciscouzo"]


def is_ignored_counter(username):
    return username.lower() in ignored_counters


def is_banned_counter(username):
    return username in banned_counters
