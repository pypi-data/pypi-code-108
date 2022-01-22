
from argparse import ArgumentParser
from pathlib import Path

parser = ArgumentParser()
#optional positional arguments


parser.add_argument("config", type=Path, default=Path("default"), nargs='?', metavar="CONFIG")
parser.add_argument("-x", default=None, dest="T")
parser.add_argument("-i", dest="I", action="store_true")

