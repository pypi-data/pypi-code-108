"""
    lager.context

    CLI context management
"""
from enum import Enum
import functools
import os
import json
import signal
import ssl

from uuid import uuid4

import urllib.parse
import urllib3
import requests
import click
from requests_toolbelt.sessions import BaseUrlSession
from . import __version__
from .exceptions import GatewayTimeoutError

_DEFAULT_HOST = 'https://app.lagerdata.com'
_DEFAULT_WEBSOCKET_HOST = 'wss://app.lagerdata.com'
DEFAULT_REGION = 'us-west-1'

def print_openocd_error(error):
    """
        Parse an openocd log file and print the error lines
    """
    if not error:
        return
    parsed = json.loads(error)
    logfile = parsed['logfile']
    if not logfile:
        return
    error_printed = False
    for line in logfile.splitlines():
        if 'Error: ' in line:
            error_printed = True
            click.secho(line, fg='red', err=True)

    if not error_printed:
        click.secho('OpenOCD failed to start', fg='red', err=True)

def print_docker_error(ctx, error):
    """
        Parse an openocd log file and print the error lines
    """
    if not error:
        return
    parsed = json.loads(error)
    stdout = parsed['stdout']
    stderr = parsed['stderr']
    click.echo(stdout, nl=False)
    click.secho(stderr, fg='red', err=True, nl=False)
    ctx.exit(parsed['returncode'])

def print_canbus_error(ctx, error):
    if not error:
        return
    parsed = json.loads(error)
    if parsed['stdout']:
        click.secho(parsed['stdout'], fg='red', nl=False)
    if parsed['stderr']:
        click.secho(parsed['stderr'], fg='red', err=True, nl=False)
        if parsed['stderr'] == 'Cannot find device "can0"\n':
            click.secho('Please check adapter connection', fg='red', err=True)


OPENOCD_ERROR_CODES = {
    'openocd_start_failed',
}

DOCKER_ERROR_CODES = set()

CANBUS_ERROR_CODES = {
    'canbus_up_failed',
}

class ElfHashMismatch(Exception):
    pass


def quote(gateway):
    return urllib.parse.quote(str(gateway), safe='')


class LagerSession(BaseUrlSession):
    """
        requests session wrapper
    """

    @staticmethod
    def handle_errors(ctx, r, *args, **kwargs):
        """
            Handle request errors
        """
        try:
            current_context = click.get_current_context()
            ctx = current_context
        except RuntimeError:
            pass
        if r.status_code == 404:
            if '/api/v1/gateway/1/download-file' in r.request.path_url:
                r.raise_for_status()
            name = ctx.params.get('gateway') or ctx.params.get('dut') or ctx.obj.default_gateway
            click.secho('You don\'t have a gateway with id `{}`'.format(name), fg='red', err=True)
            click.secho(
                'Please double check your login credentials and gateway id',
                fg='red',
                err=True,
            )
            ctx.exit(1)
        if r.status_code == 422:
            error = r.json()['error']
            if error['code'] == 'gateway_timeout_error':
                raise GatewayTimeoutError(error['description'])
            if error['code'] == 'elf_hash_mismatch':
                raise ElfHashMismatch()

            if error['code'] in OPENOCD_ERROR_CODES:
                print_openocd_error(error['description'])
            elif error['code'] in DOCKER_ERROR_CODES or error['code'] == 'wifi_connection_failed':
                print_docker_error(ctx, error['description'])
            elif error['code'] in CANBUS_ERROR_CODES:
                print_canbus_error(ctx, error['description'])
            else:
                click.secho(error['description'], fg='red', err=True)
            ctx.exit(1)
        if r.status_code >= 500:
            if True:
                print(r.text)
            else:
                click.secho('Something went wrong with the Lager API', fg='red', err=True)
            ctx.exit(1)

        r.raise_for_status()

    def __init__(self, auth, *args, response_hook=None, **kwargs):
        host = os.getenv('LAGER_HOST', _DEFAULT_HOST)
        base_url = '{}{}'.format(host, '/api/v1/')

        super().__init__(*args, base_url=base_url, **kwargs)
        verify = 'NOVERIFY' not in os.environ
        if not verify:
            urllib3.disable_warnings()

        if auth:
            auth_header = {
                'Authorization': '{} {}'.format(auth['type'], auth['token'])
            }
            self.headers.update(auth_header)
        self.headers.update({
            'Lager-Version': __version__,
            'Lager-Invocation-Id': str(uuid4()),
            })
        ci_env = get_ci_environment()
        if ci_env == CIEnvironment.HOST:
            self.headers.update({'Lager-CI-Active': 'False'})
        else:
            self.headers.update({'Lager-CI-Active': 'True'})
            self.headers.update({'Lager-CI-System': ci_env.name})

        self.verify = verify
        if response_hook:
            self.hooks['response'].append(response_hook)

    def should_strip_auth(self, old_url, new_url):
        """
            Decide whether Authorization header should be removed when redirecting, allowing for
            forwarding auth to region-specific lager servers
        """
        old = urllib.parse.urlparse(old_url)
        new = urllib.parse.urlparse(new_url)
        if old.hostname.endswith('.lagerdata.com') and new.hostname.endswith('.lagerdata.com'):
            return False

        return super().should_strip_auth(old_url, new_url)

    def request(self, *args, **kwargs):
        """
            Catch connection errors so they can be handled more cleanly
        """

        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        kwargs['headers'].update({'Lager-Request-Id': str(uuid4())})

        try:
            return super().request(*args, **kwargs)
        except requests.exceptions.ConnectTimeout:
            click.secho('Connection to Lager API timed out', fg='red', err=True)
            click.get_current_context().exit(1)
        except requests.exceptions.ConnectionError:
            click.secho('Could not connect to Lager API', fg='red', err=True)
            click.get_current_context().exit(1)

    def chip_erase(self, gateway, device, interface, transport, speed):
        """
            Chip-erase the DUT
        """
        url = 'gateway/{}/chip-erase'.format(quote(gateway))
        data = {
            'device': device,
            'interface': interface,
            'transport': transport,
            'speed': speed,
        }
        return self.post(url, json=data)

    def start_debugger(self, gateway, files):
        """
            Start the debugger on the gateway
        """
        url = 'gateway/{}/start-debugger'.format(quote(gateway))
        return self.post(url, files=files)

    def debug_connect(self, gateway, mcu):
        """
            connect debugger by mcu
        """
        url = 'gateway/{}/debug-connect'.format(quote(gateway))
        return self.post(url, json={'mcu': mcu})

    def stop_debugger(self, gateway):
        """
            Stop the debugger on the gateway
        """
        url = 'gateway/{}/stop-debugger'.format(quote(gateway))
        return self.post(url)

    def erase_dut(self, gateway, addresses):
        """
            Erase DUT connected to gateway
        """
        url = 'gateway/{}/erase-duck'.format(quote(gateway))
        return self.post(url, json=addresses, stream=True)

    def flash_dut(self, gateway, files):
        """
            Flash DUT connected to gateway
        """
        url = 'gateway/{}/flash-duck'.format(quote(gateway))
        return self.post(url, files=files, stream=True)

    def run_python(self, gateway, files):
        """
            Run python on a gateway
        """
        url = 'gateway/{}/run-python'.format(quote(gateway))
        return self.post(url, files=files, stream=True)

    def run_pip(self, gateway, args):
        """
            Run python on a gateway
        """
        url = 'gateway/{}/run-pip'.format(quote(gateway))
        return self.post(url, json={'args': args}, stream=True)

    def kill_python(self, gateway, lager_process_id, sig=signal.SIGTERM):
        """
            Run python on a gateway
        """
        url = 'gateway/{}/kill-python'.format(quote(gateway))
        return self.post(url, json={'signal': sig, 'lager_process_id': lager_process_id})

    def gateway_hello(self, gateway):
        """
            Say hello to gateway to see if it is connected
        """
        url = 'gateway/{}/hello'.format(quote(gateway))
        return self.get(url)

    def serial_numbers(self, gateway, model):
        """
            Get serial numbers of devices attached to gateway
        """
        url = 'gateway/{}/serial-numbers'.format(quote(gateway))
        return self.get(url, params={'model': model})

    def serial_ports(self, gateway):
        """
            Get serial port devices attached to gateway
        """
        url = 'gateway/{}/serial-ports'.format(quote(gateway))
        return self.get(url)

    def gateway_status(self, gateway):
        """
            Get debugger status on gateway
        """
        url = 'gateway/{}/status'.format(quote(gateway))
        return self.get(url)

    def list_gateways(self):
        """
            Get all gateways for logged-in user
        """
        url = 'gateway/list'
        return self.get(url)

    def reset_dut(self, gateway, halt):
        """
            Reset the DUT attached to a gateway and optionally halt it
        """
        url = 'gateway/{}/reset-duck'.format(quote(gateway))
        return self.post(url, json={'halt': halt})

    def run_dut(self, gateway):
        """
            Run the DUT attached to a gateway
        """
        url = 'gateway/{}/run-duck'.format(quote(gateway))
        return self.post(url, stream=True)

    def uart_gateway(self, gateway, serial_options, test_runner):
        """
            Open a connection to gateway serial port
        """
        url = 'gateway/{}/uart-duck'.format(quote(gateway))

        if test_runner == 'none':
            test_runner = None
        json_data = {
            'serial_options': serial_options,
            'test_runner': test_runner,
        }
        return self.post(url, json=json_data)

    def remote_debug(self, gateway, use_cache, archive, args):
        """
            Start a remote debugging session
        """
        url = 'gateway/{}/remote-debug'.format(quote(gateway))
        files = [
            ('args', json.dumps(args)),
        ]
        if not use_cache:
            files.append(
                ('archive', archive),
            )
        else:
            files.append(
                ('archive', ''),
            )

        try:
            return self.post(url, files=files)
        except ElfHashMismatch:
            files = [
                ('args', json.dumps(args)),
                ('archive', archive),
            ]
            print('retry')
            return self.post(url, files=files)

    def rename_gateway(self, gateway, new_name):
        """
            Rename a gateway
        """
        url = 'gateway/{}/rename'.format(quote(gateway))
        return self.post(url, json={'name': new_name})

    def start_local_gdb_tunnel(self, gateway, fork):
        """
            Start the local gdb tunnel on gateway
        """
        url = 'gateway/{}/local-gdb'.format(quote(gateway))
        return self.post(url, json={'fork': fork})

    def gpio_set(self, gateway, gpio, type_, pull):
        """
            Set a GPIO pin to input or output
        """
        url = 'gateway/{}/gpio/set'.format(quote(gateway))
        return self.post(url, json={'gpio': gpio, 'type': type_, 'pull': pull})

    def gpio_input(self, gateway, gpio):
        """
            Read from the GPIO pin
        """
        url = 'gateway/{}/gpio/input'.format(quote(gateway))
        return self.post(url, json={'gpio': gpio})

    def gpio_output(self, gateway, gpio, level):
        """
            Write to the GPIO pin
        """
        url = 'gateway/{}/gpio/output'.format(quote(gateway))
        return self.post(url, json={'gpio': gpio, 'level': level})

    def gpio_power(self, gateway, bus, level):
        """
            Set a bus enable pin to high or low
        """
        url = 'gateway/{}/gpio/power'.format(quote(gateway))
        return self.post(url, json={'bus': bus, 'level': level})

    def gpio_servo(self, gateway, gpio, pulsewidth, stop):
        """
            Control a servo with GPIO
        """
        url = 'gateway/{}/gpio/servo'.format(quote(gateway))
        return self.post(url, json={'gpio': gpio, 'pulsewidth': pulsewidth, 'stop': stop})

    def gpio_trigger(self, gateway, gpio, pulse_length, level):
        """
            Send a trigger pulse on GPIO
        """
        url = 'gateway/{}/gpio/trigger'.format(quote(gateway))
        return self.post(url, json={'gpio': gpio, 'pulse_length': pulse_length, 'level': level})

    def gpio_hardware_pwm(self, gateway, frequency, dutycycle):
        """
            Start hardware PWM on gpio
        """
        url = 'gateway/{}/gpio/hardware-pwm'.format(quote(gateway))
        return self.post(url, json={'frequency': frequency, 'dutycycle': dutycycle})

    def gpio_hardware_clock(self, gateway, frequency):
        """
            Start hardware clock on gpio
        """
        url = 'gateway/{}/gpio/hardware-clock'.format(quote(gateway))
        return self.post(url, json={'frequency': frequency})

    def get_wifi_state(self, gateway):
        """
            Get the connection state of the specified gateway
        """
        url = 'gateway/{}/wifi/state'.format(quote(gateway))
        return self.get(url)

    def get_wifi_access_points(self, gateway, interface):
        """
            Get access points visible to the specified gateway
        """
        url = 'gateway/{}/wifi/access-points'.format(quote(gateway))
        return self.get(url, params={'interface': interface})

    def connect_wifi(self, gateway, ssid, password, interface):
        """
            Connect the gateway to a wifi network
        """
        url = 'gateway/{}/wifi/connect'.format(quote(gateway))
        return self.post(url, json={'ssid': ssid, 'password': password, 'interface': interface})

    def delete_wifi_connection(self, gateway, ssid):
        """
            Delete the wifi connection for the specified gateway
        """
        url = 'gateway/{}/wifi/delete-connection'.format(quote(gateway))
        return self.post(url, json={'ssid': ssid})

    def can_up(self, gateway, bitrate, interfaces):
        """
            Bring up the CAN bus
        """
        url = 'gateway/{}/canbus/up'.format(quote(gateway))
        return self.post(url, json={'bitrate': bitrate, 'interfaces': interfaces})

    def can_down(self, gateway, interfaces):
        """
            Bring down the CAN bus
        """
        url = 'gateway/{}/canbus/down'.format(quote(gateway))
        return self.post(url, json={'interfaces': interfaces})

    def can_list(self, gateway):
        """
            List can buses
        """
        url = 'gateway/{}/canbus/list'.format(quote(gateway))
        return self.get(url)

    def can_send(self, gateway, interface, frames):
        """
            Send one or more frames on CAN bus
        """
        url = 'gateway/{}/canbus/send'.format(quote(gateway))
        frames = [frame._asdict() for frame in frames]
        return self.post(url, json={'interface': interface, 'frames': frames})

    def can_dump(self, gateway, interface, can_options):
        """
            Dump frames from CAN bus
        """
        url = 'gateway/{}/canbus/dump'.format(quote(gateway))
        return self.post(url, json={'interface': interface, 'can_options': can_options})

    def read_adc(self, gateway, channel, average_count, output):
        """
            Read the ADC
        """
        data = {
            'channel': channel,
            'average_count': average_count,
            'output': output
        }
        url = 'gateway/{}/adc/read'.format(quote(gateway))
        return self.post(url, json=data)

    def reboot_gateway(self, gateway):
        """
            Reboot gateway
        """
        url = 'gateway/{}/reboot'.format(quote(gateway))
        return self.post(url)

    def shutdown_gateway(self, gateway):
        """
            shutdown gateway
        """
        url = 'gateway/{}/poweroff'.format(quote(gateway))
        return self.post(url)

    def ble_scan(self, gateway, timeout):
        """
            scan for BLE devices
        """
        url = 'gateway/{}/ble/scan'.format(quote(gateway))
        return self.get(url, params={'timeout': timeout})

    def download_file(self, gateway, filename):
        """
            download a file from gateway
        """
        url = 'gateway/{}/download-file'.format(quote(gateway))
        return self.get(url, params={'filename': filename}, stream=True)

    def region(self, gateway):
        """
            get the region for the gateway
        """
        url = 'gateway/{}/region'.format(quote(gateway))
        region = self.get(url).json()['region']
        if region == DEFAULT_REGION:
            return None
        return region

class LagerContext:  # pylint: disable=too-few-public-methods
    """
        Lager Context manager
    """
    def __init__(self, ctx, auth, defaults, debug, style, interpreter=None):
        ws_host = os.getenv('LAGER_WS_HOST', _DEFAULT_WEBSOCKET_HOST)
        response_hook = functools.partial(LagerSession.handle_errors, ctx)
        self.session = LagerSession(auth, response_hook=response_hook)
        self.session.max_redirects = 2
        self.defaults = defaults
        self.style = style
        self.ws_host = ws_host
        self.debug = debug
        self.interpreter = interpreter
        if auth:
            self.auth_token = auth['token']

    @property
    def default_gateway(self):
        """
            Get default gateway id from config
        """
        return self.defaults.get('gateway_id')

    @default_gateway.setter
    def default_gateway(self, gateway_id):
        self.defaults['gateway_id'] = str(gateway_id)

    def websocket_connection_params(self, socktype, **kwargs):
        """
            Yields a websocket connection to the given path
        """
        if socktype == 'job':
            path = f'/ws/job/{kwargs["job_id"]}'
        elif socktype == 'jl-tunnel':
            path = f'/ws/gateway/{kwargs["gateway_id"]}/gdb-tunnel/2331'
        elif socktype == 'gdb-tunnel':
            path = f'/ws/gateway/{kwargs["gateway_id"]}/gdb-tunnel/3333'
        elif socktype == 'openocd-tunnel':
            path = f'/ws/gateway/{kwargs["gateway_id"]}/gdb-tunnel/4444'
        elif socktype == 'rtt':
            path = f'/ws/gateway/{kwargs["gateway_id"]}/gdb-tunnel/9090'
        elif socktype == 'webcam-tunnel':
            path = f'/ws/gateway/{kwargs["gateway_id"]}/gdb-tunnel/8081'
        elif socktype == 'pdb':
            path = f'/ws/gateway/{kwargs["gateway_id"]}/gdb-tunnel/5555'
        elif socktype == 'pigpio-tunnel':
             path = f'/ws/gateway/{kwargs["gateway_id"]}/gdb-tunnel/8888'
        elif socktype == 'grafana-tunnel':
             path = f'/ws/gateway/{kwargs["gateway_id"]}/gdb-tunnel/3000'
        else:
            raise ValueError(f'Invalid websocket type: {socktype}')

        if kwargs.get('region') and 'dev.lagerdata.app' not in self.ws_host:
            ws_host = f'wss://{kwargs["region"]}-elb.app.lagerdata.com'
        else:
            ws_host = self.ws_host
        uri = urllib.parse.urljoin(ws_host, path)

        headers = [
            (b'authorization', self.session.headers['Authorization'].encode()),
        ]
        ctx = get_ssl_context()

        return (uri, dict(extra_headers=headers, ssl_context=ctx))

def get_default_gateway(ctx):
    """
        Check for a default gateway in config; if not present, check if the user
        only has 1 gateway. If so, use that one.
    """
    name = os.getenv('LAGER_GATEWAY')
    if name is None:
        name = ctx.obj.default_gateway

    if name is None:
        session = ctx.obj.session
        resp = session.list_gateways()
        resp.raise_for_status()
        gateways = resp.json()['gateways']

        if not gateways:
            click.secho('No gateways found! Please contact support@lagerdata.com', fg='red')
            ctx.exit(1)
        if len(gateways) == 1:
            ctx.obj.default_gateway = gateways[0]['id']
            return gateways[0]['id']

        hint = 'NAME. Set a default using `lager set default gateway <id>`'
        raise click.MissingParameter(
            param=ctx.command.params[0],
            param_hint=hint,
            ctx=ctx,
            param_type='argument',
        )
    return name

def get_ssl_context():
    """
        Get an SSL context, with custom CA cert if necessary
    """
    cafile_path = os.getenv('LAGER_CAFILE_PATH')
    if not cafile_path:
        # Use default system CA certs
        return None
    ctx = ssl.create_default_context()
    ctx.load_verify_locations(cafile=cafile_path)
    return ctx

def ensure_debugger_running(gateway, ctx):
    """
        Ensure debugger is running on a given gateway
    """
    session = ctx.obj.session
    gateway_status = session.gateway_status(gateway).json()
    if not gateway_status['running']:
        click.secho('Gateway debugger is not running. Please use `lager connect` to run it', fg='red', err=True)
        ctx.exit(1)
    return gateway_status

class CIEnvironment(Enum):
    """
        Enum representing supported CI systems
    """
    HOST = 'host'
    DRONE = 'drone'
    GITHUB = 'github'
    BITBUCKET = 'bitbucket'
    GITLAB = 'gitlab'
    GENERIC_CI = 'ci'
    JENKINS = 'jenkins'

_CONTAINER_CI = set((
    CIEnvironment.DRONE,
    CIEnvironment.GITHUB,
    CIEnvironment.BITBUCKET,
    CIEnvironment.GITLAB,
))

def is_container_ci(ci_env):
    """
        Supported container-based CI solutions
    """
    return ci_env in _CONTAINER_CI

def get_ci_environment():
    """
        Determine whether we are running in CI or not
    """

    if os.getenv('CI') == 'true':
        if os.getenv('DRONE') == 'true':
            return CIEnvironment.DRONE
        if os.getenv('GITHUB_RUN_ID'):
            return CIEnvironment.GITHUB
        if os.getenv('BITBUCKET_BUILD_NUMBER'):
            return CIEnvironment.BITBUCKET
        if 'gitlab' in os.getenv('CI_SERVER_NAME', '').lower():
            return CIEnvironment.GITLAB
        if 'jenkins' in os.getenv('BUILD_TAG', '').lower():
            return CIEnvironment.JENKINS
        return CIEnvironment.GENERIC_CI

    return CIEnvironment.HOST
