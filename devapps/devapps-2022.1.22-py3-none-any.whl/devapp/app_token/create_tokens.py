#!/usr/bin/env python
# TODO: make this a real program, currently just a hack to get tokens
"""
for now just run this with a >> to your tokens store file

"""
import os
import sys
import time

import jwt


def run():
    here = os.path.abspath(os.path.dirname(__file__))
    sys.argv.append('')
    sys.argv.append('')

    secret_file = sys.argv[1]

    why = sys.argv[2]
    if not why:
        print('add why as sys.argv[2]')
        sys.exit(1)
    realms = sys.argv[3]
    if not realms:
        print('add realms as sys.argv[3]')
        sys.exit(1)

    now = int(time.time())
    now5y = now + 86400 * 360 * 5
    message = {
        'iss': 'https://axwifi.com/',
        'sub': 'ax.wifi',
        # 'roles': 'publ_*',
        'roles': sys.argv[4],
        'realms': realms,
        'why': why,
        'iat': now,
        'exp': now5y,
        'max_rate': 10,  # per sec
    }

    # print('\n========== NEW TOKEN==%s==%s====\n' % (time.ctime(), why))
    [print(k, v, file=sys.stderr) for k, v in list(message.items())]
    print(
        str(
            jwt.encode(
                message, open(secret_file).read().strip(), algorithm='HS256'
            ).decode('utf-8')
        )
    )
