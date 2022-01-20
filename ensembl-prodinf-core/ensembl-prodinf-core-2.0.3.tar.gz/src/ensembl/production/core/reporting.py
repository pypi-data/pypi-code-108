#    See the NOTICE file distributed with this work for additional information
#    regarding copyright ownership.
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#        http://www.apache.org/licenses/LICENSE-2.0
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""
Reporting module.
"""
import logging
import socket
from datetime import datetime


_HOSTNAME = socket.gethostname()


reporting_logger = logging.getLogger(__name__)


def make_report(report_type, msg, params=None, resource=''):
    """Return a dictionary compatible with ReportFormatter.
    """
    if params is None:
        params = {}
    return {
        'params': params,
        'resource': resource,
        'report_type': report_type,
        'msg': msg
    }


class ReportFormatter:
    """Formatter class creating messages for the report index.
    """
    def __init__(self, process_name):
        self.process_name = process_name

    def format(self, report):
        """Take a report templated dictionary and return a dictionary formatted
        for the report index.
        """
        try:
            report_type = report['report_type']
        except KeyError:
            raise ValueError("Report: %s is missing report required field 'report_type'" % report)
        return {
            'report_type': report_type, # CRITICAL, ERROR, INFO, DEBUG, WARN
            'host': _HOSTNAME,
            'process': self.process_name,
            'resource': report.get('resource', ''),
            'params': report.get('params', {}),
            'report_time': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3],
            'message': report.get('msg', '')
        }

