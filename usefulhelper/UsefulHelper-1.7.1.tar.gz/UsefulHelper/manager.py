# -*- coding: UTF-8 -*-
"""
The temple of manage
"""
import os
import re

import click
import shutil

from UsefulHelper.Tools import Setup
from UsefulHelper.Tools.tree import Tree
from UsefulHelper.Project.App import path

from UNKnownDB.DB.LightDB import Data


key_list = ['prepare', 'build', 'create']
manage_list = ['setup', 'pack', 'clean']


@click.command()
@click.option(
    '--get', prompt='manage>>'
)
def main(get):
    split = get.split(' ')
    first = split[0]
    if first in manage_list:
        info = eval(first)(split[1:])
        print(info)
        get = None
        main(get)
    elif first in key_list:
        eval(first)()
        get = None
        main(get)
    elif first == 'stop':
        exit(0)
    else:
        print(get + " isn't support")
        get = None
        main(get)


def setup(get):
    task = Setup(path=get)
    task.setup()
    return 'Down'


def pack(get):
    task = Setup(path=get)
    task.pack()
    return 'Down'


def clean(get):
    if not get:
        shutil.rmtree('./')
    else:
        shutil.rmtree(get[0])


def prepare():
    # Describe
    make_dir('./Describe')
    open('./Describe/grammar.usg', 'w').close()
    open('./Describe/setting.uss', 'w').close()
    open('./Describe/function.py', 'w').close()
    # Build
    make_dir('Build')
    print('Down')


def make_dir(name):
    os.mkdir(name)
    open('./' + name + '/__init__.py', 'w').close()


def build():
    """
    build
    """
    with open('./Build/grammar.usb', 'w') as out:
        tree = Tree('./Describe/grammar.usg')
        tree.dict()
        print(tree.Describe)
        out.write(str(tree.value()))
    print('Down')


def create():
    with open('./Describe/function.py') as func:
        settings = func.read()
    with open(path) as temple:
        data = temple.read()
        write = re.sub("'<def>'", settings, data)
    with open('./Build/app.py', 'w') as final:
        final.write(write)


def db(get):
    with Data('info.unl') as data:
        print(data.path)
        data[get[0]] = get[1]
