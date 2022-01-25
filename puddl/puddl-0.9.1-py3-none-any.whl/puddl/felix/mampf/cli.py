import datetime
import logging
import re

import click
from flask import Flask, request, make_response
from sqlalchemy.exc import SQLAlchemyError

from puddl import get_config
from puddl.db.alchemy import get_engine
from .models import Base, schema, Thing

log = logging.getLogger()


@click.group()
def main():
    pass


@main.command()
def run():
    conf = get_config(app='mampf')
    schema.bind(get_engine(conf))
    Base.metadata.create_all(schema.engine)

    app = Flask(__name__)

    @app.route('/')
    def index():
        response = make_response(f'POST stuff to {request.base_url}<scope>\n')
        response.headers['Content-Type'] = 'text/plain'
        return response

    @app.route('/<scope>', methods=['POST'])
    def mjam(scope):
        session = schema.Session()
        t = Thing(
            scope=scope,
            x=dict(request.form),
        )
        try:
            session.add(t)
            session.commit()
            response = make_response()  # no news is good news
            response.headers['Content-Type'] = 'text/plain'
            return response
        except SQLAlchemyError:
            session.rollback()
            response = make_response('NOK\n', 500)
            response.headers['Content-Type'] = 'text/plain'
            return response

    app.run()


def _parse_since(x):
    RE_SINCE = re.compile(
        r'((?P<days>\d+?)d)?'
        r'((?P<hours>\d+?)h)?'
        r'((?P<minutes>\d+?)m)?'
        r'((?P<seconds>\d+?)s)?')
    m = RE_SINCE.match(x)
    td_kw = {}
    for k, v in m.groupdict().items():
        if v is None:
            continue
        else:
            td_kw[k] = float(v)
    return datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(**td_kw)


@main.command()
@click.option('--limit', default=100)
@click.option(
    '--since',
    help="Only return logs newer than a relative duration like 5s, 2m, or 3h."
)
def ls(limit, since):
    conf = get_config(app='mampf')
    schema.bind(get_engine(conf))
    session = schema.Session()
    things = session.query(Thing) \
        .order_by(Thing.dt.desc())
    # time filter
    if since is not None:
        then = _parse_since(since)
        things = things.filter(Thing.dt > then)
    # limit
    things = things.limit(limit)
    for thing in reversed(things.all()):
        print(thing)
