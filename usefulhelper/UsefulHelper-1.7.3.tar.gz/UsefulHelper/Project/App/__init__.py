"""
DSL APP
"""
import click
from UsefulHelper.Tools.search import Search

name = ''
path = __file__


'<def>'


@click.command()
@click.option(
    '--get', prompt=name + '>>'
)
def main(get: str):
    search = Search('./grammar.usb')
    exec(search.find(things=get.split(' ')))
    main()


if __name__ == '__main__':
    main()
else:
    print(__name__)
