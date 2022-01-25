import traceback
from clspy.log import Logger
from notion_client import Client
from .notion.databases import database

clslog = Logger().log


def exporter(client, clsconfig):
    """Get week tasks, dump them into month table

    Search all pages and child pages that are shared with the integration.

    The results may include databases. The query parameter matches against the page titles. If the query parameter is not provided, the response will contain all pages (and child pages) in the results.

    The filter parameter can be used to query specifically for only pages or only databases.

    """
    searchAll = client.search()

    for i in searchAll['results']:
        # Itor all database
        clslog.info(i['object'])
        if i['object'] == 'database':
            try:
                database = client.databases.query(i['id'])
                title = i['title']

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
        pass
        # render html
    except Exception as e:
        clslog.error(e)
        traceback.print_exc(e)
