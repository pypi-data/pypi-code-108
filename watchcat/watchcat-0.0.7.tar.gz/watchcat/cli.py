import argparse

from . import info


def build_parser():
    parser = argparse.ArgumentParser(f"{info.name}")
    parser.add_argument("--version", "-V", action="version")
    parser.add_argument("--config", "-c", required=True, help="config yaml file")
    parser.add_argument("--db", "-d", default="watchcat.db")
    return parser
