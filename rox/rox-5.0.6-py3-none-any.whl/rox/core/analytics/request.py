from datetime import date, datetime
from dateutil.tz import tzutc
import json
from gzip import GzipFile
from requests.auth import HTTPBasicAuth
from requests import sessions
from io import BytesIO

from rox.core.analytics.version import VERSION
from rox.core.analytics.utils import remove_trailing_slash
from rox.core.consts.environment import Environment
from rox.core.logging.logging import Logging

_session = sessions.Session()


def post(device_properties, write_key, host=None, gzip=False, batch=None, **kwargs):
    """Post the `batch` to the API"""
    body = batch
    if device_properties.rox_options.is_self_managed():
        analytics_base_url = device_properties.rox_options.analytics_url
    else:
        analytics_base_url = Environment.ANALYTICS_PATH
    url = remove_trailing_slash(analytics_base_url) + '/impression/' + device_properties.rollout_key
    data = json.dumps(body, cls=DatetimeSerializer)
    Logging.get_logger().debug('making request: %s' % data)
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'python/' + (device_properties.lib_version or 'noversion')
    }
    if gzip:
        headers['Content-Encoding'] = 'gzip'
        buf = BytesIO()
        with GzipFile(fileobj=buf, mode='w') as gz:
            # 'data' was produced by json.dumps(), whose default encoding is utf-8.
            gz.write(data.encode('utf-8'))
        data = buf.getvalue()

    res = _session.post(url, data=data, headers=headers, timeout=15)

    if res.status_code == 200:
        Logging.get_logger().debug('data uploaded successfully')
        return res

    try:
        payload = res.json()
        Logging.get_logger().debug('received response: %s' % payload)
        raise APIError(res.status_code, payload['code'], payload['message'])
    except ValueError:
        raise APIError(res.status_code, 'unknown', res.text)


class APIError(Exception):

    def __init__(self, status, code, message):
        self.message = message
        self.status = status
        self.code = code

    def __str__(self):
        msg = "[Segment] {0}: {1} ({2})"
        return msg.format(self.code, self.message, self.status)


class DatetimeSerializer(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()

        return json.JSONEncoder.default(self, obj)
