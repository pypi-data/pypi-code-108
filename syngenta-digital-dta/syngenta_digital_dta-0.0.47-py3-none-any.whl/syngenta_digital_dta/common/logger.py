import os

from syngenta_digital_dta.common import json_helper


def log(**kwargs):
    if not os.getenv('RUN_MODE') == 'unittest':
        print(json_helper.try_encode_json({
            'level': kwargs.get('level', 'INFO'),
            'log': kwargs.get('log', {})
        }))
