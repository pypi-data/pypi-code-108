#!/usr/bin/env python
import json

from puddl.pg import DB

app = DB('exif')

data = []
rows = app.engine.execute('SELECT id, lat, lng, alt, thumb, url, dt, since_start FROM markers ORDER BY dt ASC')

for row in rows:
    d = dict(zip(rows.keys(), row))
    data.append(d)

jsdata = json.dumps(data)

tmin = app.engine.execute('SELECT min(dt) FROM markers').scalar()
tmax = app.engine.execute('SELECT max(dt) FROM markers').scalar()
print(f"window.tmin = '{tmin}'")
print(f"window.tmax = '{tmax}'")
print(f"window.exif_data = {jsdata}")
