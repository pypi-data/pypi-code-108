# -*- encoding: utf-8 -*-

import click
import datetime
import re
import traceback
import pandas

from clspy import ConfigUnique
from clspy import Logger
from notion_client import Client

clslog = Logger().log

from .clslq_notion_wreport import WeekReport
from .clslq_notion_mreport import MonthReport


def cli_week(client, clsconfig, excel, remove, force, send):
    """Generate work report every week

    Args:
        client (object): Notion client instance
        clsconfig (dict): Config instance of .clslq.json
        excel (bool): Support dump excel or not
        remove (bool): Remove dumped files or not
        force (bool): Force generate or not
        send (bool): Send email or not
    """
    for i in client.search()['results']:
        if i['object'] == 'database':
            try:

                database = client.databases.query(i['id'])
                title = i['title']

                for t in title:
                    plain_text = t['plain_text'].strip().replace(' → ', '~')
                    plain_text_head = t['plain_text'][0:3]
                    value = re.compile(r'^[0-9]+[0-9]$')
                    # Handle valid report database only
                    if plain_text_head == 'WRT':
                        break
                    if value.match(plain_text_head) == None:
                        break
                    enddate = datetime.datetime.fromisoformat(
                        t['mention']['date']['end'])
                    startdate = datetime.datetime.fromisoformat(
                        t['mention']['date']['start'])

                    wrp = WeekReport(plain_text)

                    # Use BT-Panel timer task to trigger
                    if not force:
                        if wrp.now.weekday() != 5:  # 0~6 means Monday~Sunday
                            clslog.warning("Today is not Saturday")
                            break
                    if not wrp.week_belongs(startdate, enddate):
                        click.secho(
                            "[{}~{}] today:{}[weekday:{}] gap:{}days Week report expired"
                            .format(startdate.strftime("%Y-%m-%d"),
                                    enddate.strftime("%Y-%m-%d"),
                                    wrp.now.strftime("%Y-%m-%d"),
                                    wrp.now.weekday(),
                                    abs(startdate - wrp.now).days),
                            fg='green')
                        break
                    wtitle = "{}({})".format(clsconfig.get('wr_title_prefix'),
                                             plain_text)

                    if excel:
                        wrp.excel_worksheet_dump(plain_text, database)
                        df = pandas.read_excel(plain_text + '.xlsx',
                                               sheet_name='WR',
                                               header=1)
                    else:
                        df = wrp.pandas_df_fill(database)
                    pandas.set_option('colheader_justify', 'center')
                    df.style.hide_index()  # Hide index col

                    # with open("debug.json", "w") as file:
                    #     file.write(json.dumps(i))

                    wrp.render_html(clsconfig, wtitle, database)
                    if send:
                        wrp.send_email(clsconfig, wtitle)
                    if remove:
                        wrp.remove_files()

            except Exception as e:
                clslog.error(e)
                traceback.print_exc(e)


def cli_month(client, clsconfig, remove, force, send):
    """Generate work report every month

    Args:
        client (object): Notion client instance
        clsconfig (dict): Config instance of .clslq.json
        remove (bool): Remove dumped files or not
        force (bool): Force generate or not
        send (bool): Send email or not
    """
    mrp = MonthReport(clsconfig.get('mr_title_prefix'))
    mrp.init(clsconfig.get('mr_title_prefix'), clsconfig.get('user'),
             clsconfig.get('department'), force)
    # Use BT-Panel timer task to trigger
    if not force:
        if not (mrp.now.day >= 1 and mrp.now.day <= 5):
            clslog.warning(
                "Month report email only sent when mday [1~5] or in force mode"
            )
            return
    """Get week tasks, dump them into month table

    Search all pages and child pages that are shared with the integration.

    The results may include databases. The query parameter matches against the page titles. If the query parameter is not provided, the response will contain all pages (and child pages) in the results.

    The filter parameter can be used to query specifically for only pages or only databases.

    """
    searchAll = client.search()

    for i in searchAll['results']:
        # Itor all database
        if i['object'] == 'database':
            try:
                database = client.databases.query(i['id'])
                title = i['title']
                mrp.render_itor_database(client, i['id'], title, database,
                                         force)

            except Exception as e:
                clslog.error(e)
                traceback.print_exc(e)
        elif i['object'] == 'page':
            try:
                if i['id'] == '61c48036-8c46-4c72-aea2-4d02927c01e3':
                    pass
            except Exception as e:
                clslog.error(e)

    try:
        mrp.render_html(mrp.mtitle)
        if force:
            study_title = "C(oncept)T(each)R(eview)S(implify)({}{:02})".format(
                mrp.now.year, mrp.now.month)
        else:
            study_title = "C(oncept)T(each)R(eview)S(implify)({}{:02})".format(
                mrp.now.year, mrp.now.month - 1)
        study_email = mrp.render_study_html(study_title)

        if send:
            mrp.send_email(clsconfig, mrp.mtitle)
            mrp.send_study_email(clsconfig, study_title, study_email)
        if remove:
            mrp.remove_files()
    except Exception as e:
        clslog.error(e)
        traceback.print_exc(e)


@click.option('--rtype',
              '-t',
              required=True,
              default='week',
              type=click.Choice(['week', 'month', 'all']),
              help='Choose a type to generate report')
@click.option('--excel',
              '-e',
              flag_value='GenerateExcel',
              default=False,
              help='Generate xlsx excel file or not')
@click.option('--remove',
              '-r',
              flag_value='RemoveFiles',
              help='Remove files or not')
@click.option(
    '--force',
    '-f',
    flag_value='force',
    default=False,
    help='Force generate right now, otherwise limited by valid datetime')
@click.option('--send',
              '-s',
              flag_value='send',
              default=False,
              help='Send email or not')
@click.option('--config',
              '-c',
              type=click.Path(exists=True),
              default='.clslq.json',
              help='CLSLQ config use {} as default.'.format('.clslq.json'))
@click.command(context_settings=dict(
    allow_extra_args=True,
    ignore_unknown_options=True,
),
               help="Notion Report Generator.")
def notion(rtype, config, excel, remove, force, send):

    clsconfig = ConfigUnique(file=config)
    if clsconfig.get('secrets_from') is None:
        click.secho("Make sure notion secret code is valid in .clslq.json",
                    fg='red')
        return

    client = Client(auth=clsconfig.get('secrets_from'),
                    notion_version="2021-08-16")

    click.secho("Report type: {} Notion Accounts:".format(rtype), fg='yellow')
    for u in client.users.list()['results']:
        click.secho("{:8s} {}".format(u['name'], u['id']), fg='green')
    if 'week' == rtype:
        click.secho("Week report generator", fg='green')
        cli_week(client, clsconfig, excel, remove, force, send)
    elif 'month' == rtype:
        click.secho("Month report generator", fg='green')
        cli_month(client, clsconfig, remove, force, send)
    else:
        click.secho("All reports generator", fg='green')
        cli_week(client, clsconfig, excel, remove, force, send)
        cli_month(client, clsconfig, remove, force, send)
