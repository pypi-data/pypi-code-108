# main
from os import path
from . import algorithms
import json
import os
from . import argparser
import sys
from .ioutil import savedDict
from .subcommands import subcommands


def run(args=None):
    if(args is None):
        args = sys.argv
    argdict = argparser.parse_args(args[1:])
    subcommand = 'help'
    if(not argdict):
        subcommand = 'help'
    elif(argdict.get('positional')):
        _args = argdict['positional']
        subcmd = _args[0]
        if(subcmd in ["edit", "add", "app", "awesome"]):
            subcommand = subcmd
        else:
            subcommand = "search"

    else:
        subcommand = 'help'
    subcommands[subcommand](argdict)


if(__name__ == '__main__'):
    run()
