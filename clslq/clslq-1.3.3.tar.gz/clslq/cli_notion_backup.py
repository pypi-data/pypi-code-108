# -*- encoding: utf-8 -*-
'''clslq_notion_backup

Notion client in python, notion-py is required

Usage: clslq notion_backup [OPTIONS]


'''

import click

from clspy.config import ConfigUnique
from clspy.log import Logger
from notion_client import Client
from .clslq_notion_export import exporter

clslog = Logger().log


@click.option('--config',
              '-c',
              type=click.Path(exists=True),
              default='.clslq.json',
              help='CLSLQ config use {} as default.'.format('.clslq.json'))
@click.command(context_settings=dict(
    allow_extra_args=True,
    ignore_unknown_options=True,
),
               help="Notion backup tool, use secert in clslq config.")
def notion_backup(config):

    clsconfig = ConfigUnique(file=config)
    if clsconfig.get('secrets_from') is None:
        click.secho("Make sure notion secret code is valid in .clslq.json",
                    fg='red')
        return

    client = Client(auth=clsconfig.get('secrets_from'),
                    notion_version="2021-08-16")

    click.secho("Notion Accounts:", fg='yellow')
    for u in client.users.list()['results']:
        click.secho("{:8s} {}".format(u['name'], u['id']), fg='green')

    exporter(client, clsconfig)
