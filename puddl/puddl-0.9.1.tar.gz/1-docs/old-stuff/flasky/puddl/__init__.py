from .datum import Datum


def dump(source, path):
    d = Datum(source=source, path=path)
    return d.to_json()


def get_db():
    from .db import DB

    return DB()


def index(source, path):
    db = get_db()
    d = Datum(source=source, path=path)
    db.stream_datum(source, d)
    return d
