"""
DSL APP
"""
import click
from UsefulHelper.Tools.search import Search

name = ''
path = __file__


name = 'BUI'


class MainWindow:
    def __init__(self):
        pass


class Widget:
    def __init__(self):
        pass


class Text:
    def __init__(self):
        pass


class EnterBox:
    def __init__(self):
        pass


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
