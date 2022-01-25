from pathlib import Path

from flask import Flask, send_from_directory

from puddl.pg import DB

app = Flask(__name__)
pdl = DB('exif')
root = Path('.').absolute()


@app.route('/')
def index():
    return send_from_directory(root, 'index.html')


@app.route('/<path:path>')
def _home(path):
    print(path)
    return send_from_directory(root, path)


@app.route("/space")
def space():
    data = []
    rows = pdl.engine.execute('SELECT id, lat, lng, alt, thumb, url, dt, since_start FROM markers ORDER BY dt ASC')

    for row in rows:
        d = dict(zip(rows.keys(), row))
        data.append(d)
    return {'rows': data}


@app.route("/time")
def time():
    return {
        'tmin': pdl.engine.execute('SELECT min(dt) FROM markers').scalar(),
        'tmax': pdl.engine.execute('SELECT max(dt) FROM markers').scalar(),
    }
