"""
Indexes a CodiMD remote given as os environment variable CODIMD_NAME.

Can be run standalone like this::

    CODIMD_NAME=foo python index.py
"""
import logging
import os

import pandas as pd
import requests

from puddl import get_config
from puddl.db import get_alchemy_session
from puddl.db.alchemy import Upserter
from puddl.felix.codimd import CodiMDError
from puddl.felix.codimd.models import Remote, Note, History

log = logging.getLogger(__name__)
conf = get_config(app='codimd')

remote_name = os.environ['CODIMD_NAME']

db_session = get_alchemy_session(conf)
s = requests.session()

# I'd like to use "?" here, but providing create_engine with paramstyle='qmark'
# does not work. :(
# https://docs.sqlalchemy.org/en/13/core/engines.html#sqlalchemy.create_engine.params.paramstyle
remote = db_session.query(Remote) \
    .filter(Remote.name == remote_name) \
    .one()


def raise_on_alert_in_dom(response: requests.Response):
    """
    CodiMD seems not to know how to return non-200 HTTP status codes.
    So we look for "alert" in the DOM. *sigh*
    Could use beautiful soup or lxml for that, but meh.
    """
    o = response.text.find('alert')
    if o >= 0:
        raise CodiMDError(response.text[o:o + 200])


s.post(f'{remote.url}/login',
       data={'email': remote.email, 'password': remote.password})

r = s.get(f'{remote.url}/history')
raise_on_alert_in_dom(r)
records = r.json()['history']
# [{'id': 'pycharm', 'text': 'pycharm', 'time': 1582037284079, 'tags': []}, ...]
log.debug(records)
df = pd.DataFrame(records)
# db.bind.execute('DELETE FROM codimd.history')
db_session.bind.execute('TRUNCATE codimd.history RESTART IDENTITY CASCADE')
df.to_sql(
    'history', db_session.bind,
    schema='codimd', if_exists='append', index=False,
    dtype={k: v.type for k, v in History.__table__.columns.items()}
)
# want to get this in a notebook?
# df = pd.read_sql('SELECT * FROM codimd.history', engine, index_col='index')

ups = Upserter(db_session, Note)

for note_id in df['id']:
    log.info(f'fetching {note_id}')
    r = s.get(f'{remote.url}/{note_id}/download')

    ups.upsert(
        remote_id=remote.id,
        note_id=note_id,
        text=r.text,
    )
db_session.commit()
