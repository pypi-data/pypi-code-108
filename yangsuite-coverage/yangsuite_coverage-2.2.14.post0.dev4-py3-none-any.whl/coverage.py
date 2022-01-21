# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
# ! /usr/bin/env python
"""Logic to retrieve model coverage."""

from argparse import ArgumentParser
import logging
import requests
import json
from datetime import datetime
import traceback
import netmiko
from yscoverage import analytics
try:
    from yangsuite import get_logger
    log = get_logger(__name__)
except ImportError:
    log = logging.getLogger(__name__)


class YangCoverageException(Exception):
    """All purpose coverage exception."""

    def __init__(self, msg='Yang coverage error'):
        """Raise error with message."""
        super(YangCoverageException, self).__init__(msg)


class YangCoverageInProgress(Exception):
    """User must wait for previous analysis to finish."""

    def __init__(self, msg='Analysis in progress'):
        """Raise error with message."""
        super(YangCoverageException, self).__init__(msg)


def generate_coverage(text=None, url=None):
    """Call to server for model coverage.

    Args:
      text (str): Text to be analysied for model coverage (optional).
      url (str): URL point to analysis server.
    Return:
      (tuple): Marked up CLI and XML equivelant
    """
    if text is None:
        raise YangCoverageException('No configuration text')

    if url is None:
        raise YangCoverageException('No coverage analysis target')

    try:
        resp = requests.post(
            url=url,
            headers={
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "cli": text
            })
        )
        resp.raise_for_status()
        return (resp.json()['coverage'], resp.json()['xml'])
    except requests.exceptions.RequestException:
        return '*** failed ***', ''


class YangCoverage(object):
    """Class providing feature logic for model coverage."""

    coverage_in_progress = False
    total_lines = 0
    line_count_in_progress = 0
    average_lines_per_second = 0

    @classmethod
    def get_config(cls, device):
        """Return show running from Cisco device.

        Args:
          device (ysdevices.YSDeviceProfile): Target device
        Return:
          (str): Show running config
        """
        try:
            netmiko_device = {
                'device_type': device.ssh.device_variant,
                'ip': device.ssh.address,
                'username': device.ssh.username,
                'password': device.ssh.password,
                'port': device.ssh.port,
                'timeout': device.ssh.timeout,
            }
        except Exception as e:
            raise YangCoverageException("Invalid platform")

        resp = 'No response'
        ssh = None

        try:
            ssh = netmiko.ConnectHandler(**netmiko_device)
            log.debug('SSH SEND: show running')
            resp = ssh.send_command('show running')
        except Exception as e:
            log.error("SSH show running failed: %s", e)
            log.error(traceback.format_exc())
            raise YangCoverageException(str(e))
        finally:
            if ssh:
                ssh.disconnect()

        log.debug('SSH RESPONSE:\n{0}'.format(resp))
        return resp

    @classmethod
    def get_releases(cls, ios):
        """Get containers from local Docker server javailable for analysis.

        Args:
          ios (str): IOS-XE, IOS-XR, or NXOS
        Return:
          (dict): Platforms releases and ports available for coverage analysis
        """
        releases = []
        containers = []

        if not ios:
            log.error("No platform specified")
            raise YangCoverageException('No platform specified.')

        try:
            containers = analytics.get_docker_container_list()
        except Exception as e:
            log.error(
                'Local container list retrieve failed\n{0}'.format(str(e)))

        if containers:
            for c in containers:
                if (ios + '_') in c['Image'] and c['State'] == 'running':
                    name = c['Image']
                    name = name[name.find(ios + '_') + len(ios) + 1:]
                    for ports in c['Ports']:
                        if 'PublicPort' in ports and \
                           'PrivatePort' in ports and \
                           ports['PrivatePort'] == 5000:
                            releases.append({'name': name,
                                             'port': ports['PublicPort']})
                            break

        return {'releases': releases}

    @classmethod
    def get_base_releases(cls, uri):
        """Get containers from remote server available for analysis.

        Args:
          uri (str): URL pointing to coverage server.
        Return:
          (dict): Platforms releases names and access ports
        """
        try:
            releases = analytics.get_docker_container_list(uri)
            return releases
        except Exception as e:
            log.error(
                'Remote container list retrieve failed\n{0}'.format(str(e)))
            return {'releases': []}

    @classmethod
    def get_coverage(cls, cli, port=0, url=None):
        """Model coverage of configuration based on IOS release.

        Args:
          cli (str): Cisco CLI configuration.
          port (int): port number of URL (optional).
          url (str): URL pointing to coverage server (default: yang-suite)
        Return:
          (dict): coverage: CLI analysis, xml: equivalent NETCONF.
        """
        if cls.coverage_in_progress:
            raise YangCoverageInProgress()

        if not url:
            if port:
                url = 'http://yang-suite.cisco.com:' + port + '/coverage'
            else:
                url = 'http://yang-suite.cisco.com/coverage'

        cls.coverage_in_progress = True
        cls.total_lines = len(cli.splitlines())
        cls.line_count_in_progress = cls.total_lines
        start_time = datetime.now()

        ycov = ('no return', '')

        try:
            ycov = generate_coverage(cli, url)

            if '*** failed ***' in ycov[0]:
                # Don't update stats for this
                cls.coverage_in_progress = False
                cls.line_count_in_progress = 0
                cls.total_lines = 0
                return ycov
        except Exception as e:
            cls.coverage_in_progress = False
            cls.line_count_in_progress = 0
            cls.total_lines = 0
            raise e

        end_time = datetime.now()
        t = end_time.second - start_time.second
        line_per_second = round(cls.total_lines / t, 2)

        if cls.average_lines_per_second:
            new_average = (cls.average_lines_per_second + line_per_second) / 2
        else:
            new_average = line_per_second

        cls.average_lines_per_second = new_average

        cls.line_count_in_progress = 0
        cls.total_lines = 0
        cls.coverage_in_progress = False

        return ycov

    @classmethod
    def get_progress(cls):
        """Get progress of current evaluation."""
        if not cls.coverage_in_progress:
            return {'max': 1, 'value': 0}
        if not cls.average_lines_per_second:
            per_sec = cls.line_count_in_progress / 20
        else:
            per_sec = cls.line_count_in_progress / cls.average_lines_per_second

        cls.line_count_in_progress -= (per_sec * 2)

        return {'max': cls.total_lines,
                'value': cls.line_count_in_progress,
                'info': ' coverage analysis processing...'}


if __name__ == '__main__':

    parser = ArgumentParser(
        description='CLI coverage tool, RESTful access:')
    parser.add_argument('-c', '--cli', type=str, required=True,
                        help="Filename with CLI to check coverage for")
    parser.add_argument('-u', '--url', type=str, required=False,
                        default='http://127.0.0.1:5000/coverage',
                        help="URL to interrogate for coverage")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="Exceedingly verbose logging to the console")
    args = parser.parse_args()

    #
    # If the user specified verbose logging, set it up.
    #
    if args.verbose:
        handler = log.StreamHandler()
        handler.setFormatter(
            log.Formatter(
                '%(asctime)s:%(name)s:%(levelname)s:%(message)s'))
        log.addHandler(handler)
        log.setLevel(logging.DEBUG)

    #
    # Do the coverage analysis
    #
    # cov, xml = generate_coverage(open(args.cli).read(), args.url)
    cov, xml = YangCoverage.get_coverage(open(args.cli).read(),
                                         5000,
                                         args.url)
    print(cov)
    print(xml)
    print('Average lines per second: {0}'.format(
        YangCoverage.average_lines_per_second))
