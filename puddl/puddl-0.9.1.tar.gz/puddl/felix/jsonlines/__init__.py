import json
import logging

import click

from puddl.db.alchemy import App

log = logging.getLogger()


@click.group()
def main():
    pass


def _iter_lines2dicts(lines):
    for line in lines:
        data = json.loads(line)
        yield data


@main.command()
@click.argument('schema')
@click.argument('table')
def load(schema, table):
    import pandas as pd

    app = App(schema)
    df = pd.DataFrame(_iter_lines2dicts(click.get_text_stream('stdin')))
    app.df_dump(df, table, index=False)
    log.info(f'SELECT * FROM {table}')
