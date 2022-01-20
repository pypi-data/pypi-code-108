import json

from tasq_cli import settings
from tasq_cli.server import make_request

logger = None


def list_projects():
    global logger
    logger = settings.get_logger()
    url = f'/projects/?sort=-id&page[size]=100'
    r = make_request(url)
    data = r.json()['data']
    for j in data:
        del(j['relationships'])
    print(json.dumps(data))
    return
