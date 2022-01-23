#!/usr/bin/python3.9 cli.py
# -*- coding: UTF-8 -*-
import os

import click
from UNKnownDB.DB import LightDB

key_list = ['start']


def start(get):
    if not get:
        get = ''
    try:
        os.mkdir('./' + get)
    except FileExistsError:
        pass
    open('./' + get + '/__init__.py', 'w').close()
    with open('./' + get + '/manage.py', 'w') as manage:
        manage.write(
            """
from UsefulHelper.manager import *


if __name__ == '__main__':
    print('Developing')
    main()
else:
    main()
        """
        )
    with LightDB.Data(path='./' + get + '/info', name=get) as db:
        print(db)
    return 'Done'


def stop():
    exit()


@click.command()
@click.option(
    "--things", prompt="UsefulHelper>>",
    help="NONE."
)
def main(things):
    split = things.split(' ')
    first = split[0]
    if first in key_list:
        info = eval(first)(split[1])
        print(info)
        things = None
        main(things)
    elif first == 'stop':
        stop()
    else:
        print(things + " isn't support")
        things = None
        main(things)


if __name__ == '__main__':
    print('Welcome to UsefulHelper')
    print('Seeing https://github.com/')
    main()
else:
    main()
