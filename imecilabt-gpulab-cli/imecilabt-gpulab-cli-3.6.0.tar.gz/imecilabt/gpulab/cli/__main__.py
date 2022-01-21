import hashlib
import re
import signal
import socket
import time
import traceback
from base64 import urlsafe_b64encode
from functools import update_wrapper
from os.path import expanduser
from subprocess import PIPE, STDOUT, DEVNULL, Popen, TimeoutExpired
from time import sleep
from typing import Optional, Any, List

import requests
import yaml
from cryptography import x509
from cryptography.hazmat.backends import default_backend

import sys

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.x509 import Certificate, ExtensionOID, SubjectAlternativeName
from dataclass_dict_convert import ignore_unknown_fields
from imecilabt_utils.utils import strip_null_from_json_dict, datetime_now
from requests.exceptions import SSLError
from urllib3 import Timeout

from imecilabt.gpulab.cli.cert_processor import process_cert
from imecilabt.gpulab.cli.ssh_config_manager import add_job_ssh_config, command_array_to_str, sh_quote_arg, \
    set_jobs_ssh_config, find_free_ssh_tunnel_port
from imecilabt.gpulab.model.job_convert import any_jsondict_to_job2, is_jsondict_job1, is_jsondict_job2
from imecilabt.gpulab.model.job_event import JobEvent, JobEventType

# from imecilabt.gpulab.model.job import Job, JobState, JobPortMapping
from imecilabt.gpulab.model.job2 import Job as Job2, JobStatus, JobPortMapping as Job2PortMapping
from imecilabt.gpulab.model.slave_info2 import SlaveInfo2

from imecilabt.gpulab.cli.apiclient import GpuLabApiClient, JOB_DEFINITION, BadPemPasswordException, \
    GPULAB_LOCALHOST_MODE, GpuLabApiLocalhostModeClient, GpuLabAnonymousApiClient

import datetime
import click
import json
import ssl
import os
import pwd

from imecilabt.gpulab.cli.util import td_format


# Info on other batch job systems:
#
#    Commands for various systems: https://slurm.schedmd.com/rosetta.pdf
#
#    Torque and slurm Job States:
#          https://slurm.schedmd.com/squeue.html
#          ttp://docs.adaptivecomputing.com/torque/4-1-3/Content/topics/commands/qstat.htm
from imecilabt.gpulab.model.slave_info2 import ClusterInfo
from imecilabt_utils.urn_util import URN

API_CLIENT = 'client'
API_CLIENT_FACT = 'client_fact'
API_ANON_CLIENT_FACT = 'client_anon_fact'
CERTFILE = 'cert_filename'
CERTFILE_IN_ARGUMENTS = 'cert_filename_argument_provided'
DEPLOY_ENV_IS_STAGING = 'deploy_environment_is_staging'
VERBOSE_DEBUG = 'verbose_debug'


GPULAB_CLIENT_TIMEOUT = Timeout(connect=2.0, read=7.0)


# modified version of:
# https://stackoverflow.com/questions/44247099/click-command-line-interfaces-make-options-required-if-other-optional-option-is
class NotRequiredIf(click.Option):
    def __init__(self, *args, **kwargs):
        self.not_required_if = kwargs.pop('not_required_if')
        assert self.not_required_if, "'not_required_if' parameter required"
        kwargs['help'] = (kwargs.get('help', '') +
                          ' NOTE: This argument is mutually exclusive with %s' %
                          self.not_required_if
                          ).strip()
        super(NotRequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        we_are_present = self.name in opts
        other_present = self.not_required_if in opts

        if other_present:
            if we_are_present:
                raise click.UsageError(
                    "Illegal usage: `%s` is mutually exclusive with `%s`" % (
                        self.name, self.not_required_if))
            else:
                self.prompt = None
        else:
            if not we_are_present:
                raise click.UsageError(
                    "Illegal usage: Either `%s` or `%s` must be specified" % (
                        self.name, self.not_required_if))

        return super(NotRequiredIf, self).handle_parse_result(
            ctx, opts, args)


# Date to string conversion for console
def _date_to_str(dt: Optional[datetime.datetime]) -> Optional[str]:
    if not dt:
        return None
    used_dt = dt - datetime.timedelta(microseconds=dt.microsecond)
    # change timezone to local
    used_dt = used_dt.astimezone(tz=None)
    return used_dt.isoformat()


def _print_table(headers: List[str], rows: List[List[Any]], add_vert_lines: bool = False, add_hor_lines: bool = False,
                 seperator : Optional[str] = None):
    rows_and_headers = list(rows)
    if headers:
        rows_and_headers.append(headers)
    widths = [max(map(len, map(str, col))) for col in zip(*rows_and_headers)]

    vert_hor_sep = seperator
    if not seperator:
        if add_vert_lines:
            seperator = ' | '
            vert_hor_sep = '-+-'
        else:
            seperator = '  '
            vert_hor_sep = seperator
    total_len = sum(widths) + ((len(widths)-1) * len(seperator))

    hor_line = ''
    if add_vert_lines:
        hor_line = vert_hor_sep.join((('-' * (width)) for val, width in zip(headers, widths)))
    else:
        hor_line = '-' * total_len

    if add_hor_lines:
        click.echo(hor_line)
    if headers:
        click.echo(seperator.join((val.ljust(width) for val, width in zip(headers, widths))))
        if add_hor_lines:
            click.echo(hor_line)
    for row in rows:
        click.echo(seperator.join((str(val).ljust(width) for val, width in zip(row, widths))))
        if add_hor_lines:
            click.echo(hor_line)


def _date_to_ago_str(dt: Optional[datetime.datetime]) -> Optional[str]:
    if not dt:
        return None
    used_dt = dt - datetime.timedelta(microseconds=dt.microsecond)
    # change timezone to local
    # used_dt = used_dt.astimezone(tz=None)
    # now_dt = datetime.datetime.now(datetime.timezone.utc)
    used_dt = used_dt
    now_dt = datetime.datetime.now(datetime.timezone.utc)
    diff_seconds = (now_dt - used_dt).total_seconds()
    if diff_seconds < 0:
        return '{} seconds in the future'.format(-diff_seconds)
    if diff_seconds < 60:
        return '{:.1f} seconds ago'.format(diff_seconds)
    if diff_seconds < 3600:
        return '{:.1f} minutes ago'.format(diff_seconds/60.0)
    if diff_seconds < 3600*24:
        return '{:.1f} hours ago'.format(diff_seconds/3600.0)
    return '{:.2f} days ago'.format(diff_seconds/(3600.0*24.0))


def _ssh_port_command(port: Optional[int]) -> str:
    if port and port != 22:
        return ' -oPort={}'.format(port)
    return ''


def _port_mapping_format(port_mappings: List[Job2PortMapping]) -> str:
    try:
        res = []
        for port_mapping in port_mappings:
            res.append('{} -> {}'.format(port_mapping.container_port, port_mapping.host_port))
        return ', '.join(res)
    except:
        return 'Error processing port mappings: {}'.format(port_mappings)


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

GPULAB_VERSION = '3.6.0'


def check_and_warn_version(ctx):
    client = ctx.obj[API_CLIENT]
    session = client.get_session()
    try:
        res = session.get(client.get_api_url(2) + "version", params={}, timeout=GPULAB_CLIENT_TIMEOUT)
    except:
        click.secho("Could not check availability of new GPULab version",
                    err=True, nl=True, fg='red')
        return

    if not res.ok:
        click.secho("Could not check availability of new GPULab version",
                    err=True, nl=True, fg='red')
        return

    version_info = None
    try:
        version_info = res.json()
        latest_version = version_info['latest_client_version']
    except:
        click.secho("Error parsing availability of new GPULab version: {}".format(json.dumps(version_info)),
                    err=True, nl=True, fg='red')
        return

    def to_version_list(version_str: str) -> List[int]:
        return list(map(int, version_str.split(".")))

    def is_older_than(a: List[int], b: List[int]) -> bool:
        """
        :param a:
        :param b:
        :return: True if a is an older version, so a lower number
        """
        if len(a) > len(b):
            for i, val in enumerate(b):
                if a[i] > val:
                    return False
                if a[i] < val:
                    return True
            return False
        else:
            for i, val in enumerate(a):
                if b[i] > val:
                    return True
                if b[i] < val:
                    return False
            return len(b) != len(a)

    try:
        cur_num_ver = to_version_list(GPULAB_VERSION)
        latest_num_ver = to_version_list(latest_version)
        latest_is_older = is_older_than(latest_num_ver, cur_num_ver)
    except:
        latest_is_older = False

    if not latest_is_older and latest_version != GPULAB_VERSION:
        click.secho(f"A new version ({latest_version}) of gpulab-cli is available. (This is version {GPULAB_VERSION})",
                    err=True, nl=True, fg='yellow')
        click.secho("Upgrade with:  pip3 install --upgrade imecilabt-gpulab-cli",
                    err=True, nl=True, fg='yellow')


# Partial commands also match
class AliasedGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        # first, also allow some hardcoded aliases
        #   Note: NEVER rely on any of these not to be removed for a new gpulab version!
        if cmd_name == 'logs':
            cmd_name = 'log'
        if cmd_name == 'slaves' or cmd_name == 'slave':
            cmd_name = 'clusters'

        if cmd_name == 'job':  # already handled below, but so frequent that we also handle it here
            cmd_name = 'jobs'

        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv

        # not a matching command -> we'll look if it can be auto-completed to find a command
        full_commands = list(self.list_commands(ctx))

        # first remove dangerous commands we don't want to have auto-completed
        dangerous_commands = ['rm', 'cancel']
        for dan in dangerous_commands:
            full_commands.remove(dan)
            # we use startswith to avoid confusing matches, such as "r" matching release without this
            if dan.startswith(cmd_name):
                return None

        matches = [x for x in full_commands if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail('Too many matches: %s' % ', '.join(sorted(matches)))


def modify_usage_error():
    """
    a method to append the help menu to an usage error
    :return: None
    """

    from click._compat import get_text_stderr
    from click.utils import echo

    def show(self, file=None):
        if file is None:
            file = get_text_stderr()
        color = None
        if self.ctx is not None:
            color = self.ctx.color
        msg = self.format_message()
        if msg == 'Missing option "--cert".':
            echo('Error: "--cert" option (or GPULAB_CERT environment var) required.\n',
                 # 'For help, try:\n   gpulab-cli --help'
                 # '\nor:'
                 # '\n   gpulab-cli <command> --help\n\n'
                 file=file, color=color)
            if self.ctx is not None:
                echo(self.ctx.get_help() + '\n', file=file, color=color)
        else:
            if self.ctx is not None:
                echo(self.ctx.get_usage() + '\n', file=file, color=color)
            echo('Error: %s\n\nFor more help, try:\n   gpulab-cli --help' % msg, file=file, color=color)
        # import sys
        # sys.argv = [sys.argv[0]]  #not sure what this is supposed to do...
        # main_command()  #seems to cause recursion error
    click.exceptions.UsageError.show = show


@click.command(cls=AliasedGroup, invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
# @click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.option("--cert", type=click.Path(readable=True), envvar='GPULAB_CERT', required=True, help='Login certificate')
@click.option("-p", "--password", type=click.STRING, help='Password associated with the login certificate')
@click.option("--dev", 'deployment_environment', flag_value='staging', allow_from_autoenv=False,
              help='Use the GPULab staging environment (this option is only kept for backward compatibility. '
                   'It was renamed to --staging)')
@click.option("--staging", 'deployment_environment', flag_value='staging', allow_from_autoenv=False,
              help='Use the GPULab staging environment')
@click.option("--stable", 'deployment_environment', flag_value='production', allow_from_autoenv=False,
              help='Use the GPULab production environment (this option is only kept for backward compatibility. '
                   'It was renamed to --production)')
@click.option("--production", 'deployment_environment', flag_value='production', allow_from_autoenv=False,
              help='Use the GPULab production environment (default)')
@click.option("--custom-master-url", type=click.STRING, envvar='GPULAB_CUSTOM_MASTER_URL', required=False, help='Use a custom URL as GPULab master')
@click.option("--debug", is_flag=True, help='Some extra debugging output')
@click.option("--servercert", type=click.Path(readable=True), envvar='GPULAB_SERVER_CERT', required=False,
              help='The file containing the servers (self-signed) certificate. Only required when the server uses '
                   'a self signed certificate.')
# See click.version_option(). note that similar arguments can be made with "click Eager Options"
@click.version_option(GPULAB_VERSION, message='%(version)s')
@click.pass_context
def cli(ctx: click.Context, cert, password, deployment_environment: str, servercert, debug, custom_master_url):
    """GPULab client version 3.6.0

    \b
    This is the general help. For help with a specific command, try:
       gpulab-cli <command> --help

    \b
    Send bugreports, questions and feedback to: gpulab@ilabt.imec.be

    \b
    Documentation: https://doc.ilabt.imec.be/ilabt/gpulab/
    Overview page: https://gpulab.ilabt.imec.be/
    Overview page (for --dev): https://dev.gpulab.ilabt.imec.be/
    """

    master_base_url = None
    # These click feature switches make interaction with envvars more difficult. We need to handle it manually:
    #   (easier with boolean flags, but then we'd have -dev/--no-dev which is less nice)
    if deployment_environment is None:
        deployment_environment_envvar_count = 0
        if os.environ.get('GPULAB_STABLE') == 'True' or os.environ.get('GPULAB_PROD') == 'True' or os.environ.get('GPULAB_PRODUCTION') == 'True':
            deployment_environment = 'production'
            deployment_environment_envvar_count += 1
        if os.environ.get('GPULAB_DEV') == 'True' or os.environ.get('GPULAB_STAGING') == 'True':
            deployment_environment = 'staging'
            deployment_environment_envvar_count += 1
        if os.environ.get('GPULAB_DEPLOYMENT_ENVIRONMENT'):
            deployment_environment = os.environ.get('GPULAB_DEPLOYMENT_ENVIRONMENT')
            deployment_environment_envvar_count += 1
        if deployment_environment_envvar_count > 1:
            click.secho('WARNING: Conflicting GPULAB_* env vars controlling the deployment_environment are set to "True": Will fall back to "production".',
                        err=True, nl=True, fg='yellow')
            deployment_environment = 'production'
        if deployment_environment is None:
            deployment_environment = 'production'

        if custom_master_url is not None:
            if not custom_master_url.startswith('https://'):
                raise click.ClickException("--custom-master-url must be an URL, not '{}'".format(custom_master_url))
            # Do not set: deployment_environment = 'staging'
            master_base_url = custom_master_url
    if deployment_environment != 'production' and deployment_environment != 'staging':
        raise click.ClickException("Something went wrong with --dev/--stable flag: '{}'".format(deployment_environment))

    is_staging = deployment_environment == 'staging'

    ctx.obj[CERTFILE_IN_ARGUMENTS] = cert is not None
    if cert is not None and not os.path.isfile(cert):
        raise click.ClickException("The certificate file cannot be found ('{}').".format(cert))
    if ctx.invoked_subcommand is None:
        click.echo(cli.get_help(ctx))

    def make_api_client(ctx):
        ctx.obj[API_CLIENT] = GpuLabApiClient(certfile=cert, keyfile=cert, password=password, dev=is_staging,
                                              server_self_signed_cert=servercert,
                                              master_base_url=master_base_url)

    def make_anon_api_client(ctx):
        ctx.obj[API_CLIENT] = GpuLabAnonymousApiClient(server_self_signed_cert=servercert, master_base_url=master_base_url)

    ctx.obj[CERTFILE] = cert
    ctx.obj[DEPLOY_ENV_IS_STAGING] = is_staging
    ctx.obj[VERBOSE_DEBUG] = debug
    ctx.obj[API_CLIENT_FACT] = make_api_client
    ctx.obj[API_ANON_CLIENT_FACT] = make_anon_api_client


def _load_api_client_helper(ctx):
    try:
        ctx.obj[API_CLIENT_FACT](ctx)
    except BadPemPasswordException:
        raise click.ClickException("The certificate is encrypted. You need to specify the correct password.")
    except ssl.SSLError as e:
        if e.strerror and 'password' in e.strerror.lower():
            raise click.ClickException(
                "The certificate is encrypted. You need to specify the correct password. ('{}')".format(e.strerror))
        elif e.strerror and 'EE_KEY_TOO_SMALL' in e.strerror:
            traceback.print_exc()
            raise click.ClickException("Exception while reading key and/or certificate from PEM.\n"
                                       "Your system SSL settings in /etc/ssl/openssl.cnf are probably very strict, "
                                       "and do not allow the key size used in '{}'".format(ctx.obj[CERTFILE]))
        else:
            traceback.print_exc()
            raise click.ClickException("Something went wrong trying to setup the SSL parameters. \n"
                                       "See the traceback for details.\n"
                                       "Some possible causes are: Bad password provided, very strict SSL settings, invalid PEM file, ...")


def _load_anonymous_client_helper(ctx):
    ctx.obj[API_ANON_CLIENT_FACT](ctx)


def require_ctx_loggedin_api_client(f):
    @click.pass_context
    def load_api_client_in_ctx(ctx, *args, **kwargs):
        _load_api_client_helper(ctx)
        return f(*args, **kwargs)
    return update_wrapper(load_api_client_in_ctx, f)


def require_ctx_any_api_client(f):
    @click.pass_context
    def load_api_client_in_ctx(ctx, *args, **kwargs):
        try:
            _load_api_client_helper(ctx)
        except Exception as e:
            click.echo("Failed to load client PEM ('{}'). Will continue without.".format(e), err=True)
            _load_anonymous_client_helper(ctx)
        return f(*args, **kwargs)
    return update_wrapper(load_api_client_in_ctx, f)


def optional_ctx_any_api_client(f):
    @click.pass_context
    def load_api_client_in_ctx(ctx, *args, **kwargs):
        try:
            _load_api_client_helper(ctx)
        except Exception as e:
            click.echo("Failed to load client PEM ('{}'). Will continue without.".format(e), err=True)
            try:
                _load_anonymous_client_helper(ctx)
            except Exception as e:
                click.echo("Failed to load anonymous client. Will continue without.".format(e), err=True)
                ctx.obj[API_CLIENT] = None
        return f(*args, **kwargs)
    return update_wrapper(load_api_client_in_ctx, f)


def _call_ext(*params: str, **kwargs) -> str:
    res = ''
    com: List[str] = params
    kwargs['stdout'] = PIPE
    kwargs['stderr'] = STDOUT
    kwargs['universal_newlines'] = True
    with Popen(com, **kwargs) as proc:
        for line in proc.stdout:
            res += line
        res_code = proc.wait()
        if res_code != 0:
            raise Exception('Command returned error ({}): {} (command={} )'.format(res_code, res.strip(), com))
    return res.strip()


@click.command('bugreport', short_help="Get context info for including in a bug report")
@click.pass_context
@optional_ctx_any_api_client
def print_bugreport_context(ctx):
    try:
        uname = _call_ext('uname', '-a')
    except:
        uname = 'error calling "uname -a"'

    try:
        with open('/etc/issue', 'r') as file:
            issue = file.read()
    except:
        issue = 'error fetching /etc/issue'

    try:
        with open('/etc/lsb-release', 'r') as file:
            lsb_release = file.read()
    except:
        lsb_release = 'error fetching /etc/lsb-release'

    try:
        with open('/etc/os-release', 'r') as file:
            os_release = file.read()
    except:
        os_release = 'error fetching /etc/os-release'

    try:
        with open(ctx.obj[CERTFILE], 'r') as pemfile:
            cert_begin_delim = '-----BEGIN CERTIFICATE-----'
            cert_end_delim = '-----END CERTIFICATE-----'
            pem_data = pemfile.read()
            pem_cert_data = re.findall(r"{begin}.*?{end}".format(begin=cert_begin_delim, end=cert_end_delim),
                                       pem_data, re.DOTALL)
    except:
        pem_cert_data = 'error fetching user cert'

    try:
        cert_info = process_cert(ctx.obj[CERTFILE]).to_dict()
    except:
        cert_info = 'error in process_cert'

    try:
        public_keys = _get_public_keys(ctx)
    except:
        public_keys = 'error fetching public_keys'

    try:
        email_address = _get_email_address(ctx)
    except:
        email_address = 'error fetching email_address'

    try:
        with open(ctx.obj[CERTFILE], 'r') as f:
            cert_content = f.read().encode('utf-8')  # encode because load_pem_x509_certificate needs bytes
        cert = x509.load_pem_x509_certificate(cert_content, default_backend())
        ext = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
        urns = ext.value.get_values_for_type(x509.UniformResourceIdentifier)
        client_cert_user_urn = urns[0]
    except:
        client_cert_user_urn = None

    res = {
        'environment': dict(os.environ),
        'ctx': {
            'CERTFILE': ctx.obj[CERTFILE],
            'DEPLOY_ENV_IS_STAGING': ctx.obj[DEPLOY_ENV_IS_STAGING],
            'VERBOSE_DEBUG': ctx.obj[VERBOSE_DEBUG],
            'API_CLIENT.get_base_url': ctx.obj[API_CLIENT].get_base_url() if API_CLIENT in ctx.obj else None,
            'API_CLIENT.get_api_url(2)': ctx.obj[API_CLIENT].get_api_url(2) if API_CLIENT in ctx.obj else None,
            'API_CLIENT.get_api_url(3)': ctx.obj[API_CLIENT].get_api_url(3) if API_CLIENT in ctx.obj else None,
            'type(API_CLIENT)': '{}'.format(type(ctx.obj[API_CLIENT])) if API_CLIENT in ctx.obj else None,
        },
        'uname': uname,
        'cert_info': cert_info,
        'python_version_info': str(sys.version_info),
        'python_version': sys.version,
        'gpulab_version': GPULAB_VERSION,
        'user_urn': ctx.obj[API_CLIENT].user_urn if API_CLIENT in ctx.obj else None,
        'client_cert_user_urn': client_cert_user_urn,
        'public_keys': public_keys,
        'email_address': email_address,
        'user_cert': pem_cert_data,
        '/etc/lsb_release': lsb_release,
        '/etc/issue': issue,
        '/etc/os-release': os_release,
        'timezone': time.strftime("%Z %z ")+str(time.timezone),
    }
    click.echo('Bug Report Context info:\n{}'.format(json.dumps(res, indent=3)))


@click.command(cls=AliasedGroup, invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
# @click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.version_option(GPULAB_VERSION, message='%(version)s')
@click.pass_context
def localhost_mode_cli(ctx):
    """GPULab client version 3.6.0 (in LOCALHOST_MODE!)

    \b
    Send bugreports, questions and feedback to: gpulab@ilabt.imec.be

    \b
    Documentation: https://doc.ilabt.imec.be/ilabt/gpulab/
    """
    if ctx.invoked_subcommand is None:
        click.echo(localhost_mode_cli.get_help(ctx))
    try:
        local_username = pwd.getpwuid(os.getuid()).pw_name  # this doesn't work on windows, but that's ok
        fixed_project_urn = os.environ[GPULAB_LOCALHOST_MODE]
        assert fixed_project_urn
        ctx.obj[API_CLIENT] = GpuLabApiLocalhostModeClient(local_username, fixed_project_urn)
        ctx.obj[CERTFILE] = None
        ctx.obj['project_urn'] = fixed_project_urn
        ctx.obj['project_name'] = re.sub(r'^.*\+project\+', '', fixed_project_urn)
    except (ssl.SSLError, BadPemPasswordException):
        raise click.ClickException("The certificate is encrypted. You need to specify the correct password.")


@click.command('submit', short_help="Submit a job request")
@click.option('-h', '--hold', is_flag=True, help="Do not queue job, immediately put it on hold")
@click.option('--wait-run', is_flag=True, help="Wait until job is running.")
@click.option('--wait-done', is_flag=True, help="Wait until job is done.")
@click.option('--email-run', is_flag=True, help="Send email when job is running.")
@click.option('--email-done', is_flag=True, help="Send email when job is done.")
# @click.option('-I','--interactive', is_flag=True, help="Interactive jobs. Wait for job ready, then connect terminal.")
@click.pass_context
@require_ctx_loggedin_api_client
def run_fixed_project(ctx, hold, wait_run, wait_done, email_run, email_done):
    actual_run(ctx, ctx.obj['project_urn'], hold, wait_run, wait_done,
               email_queued=None, email_run=email_run, email_done=email_done, ssh_pub_key=None)


def _get_project_urn(ctx, project_name: str) -> str:
    client = ctx.obj[API_CLIENT]
    userurn_auth = URN(urn=client.user_urn).authority
    return URN(authority=userurn_auth, type="project", name=project_name).urn_string()


def _get_public_keys(ctx) -> List[str]:
    res = []

    # Add pubkey from login PEM
    if ctx.obj[CERTFILE]:
        with open(ctx.obj[CERTFILE], 'rb') as pemfile:
            pem_data = pemfile.read()
        cert = x509.load_pem_x509_certificate(pem_data, default_backend())  # type: Certificate
        public_key = cert.public_key()
        if public_key and isinstance(public_key, RSAPublicKey):
            public_key_openssh = public_key.public_bytes(
                serialization.Encoding.OpenSSH,
                serialization.PublicFormat.OpenSSH).decode("utf-8")
            # click.echo('public key in openssh format: {}'.format(public_key_openssh))
            res.append(public_key_openssh)

    # Add ~/.ssh/id_rsa.pub
    typical_pubkey_filename = expanduser("~/.ssh/id_rsa.pub")
    if os.path.isfile(typical_pubkey_filename):
        with open(typical_pubkey_filename, 'r') as opensshfile:
            public_key_openssh = opensshfile.read().strip(' \t\r\n')
            # click.echo('~/.ssh/id_rsa.pub: {}'.format(public_key_openssh))
            res.append(public_key_openssh)

    return res


# find the client's email address in the X509 cert
def _get_email_address(ctx) -> Optional[str]:
    try:
        # Get email from login PEM
        if ctx.obj[CERTFILE]:
            with open(ctx.obj[CERTFILE], 'rb') as pemfile:
                pem_data = pemfile.read()
            cert = x509.load_pem_x509_certificate(pem_data, default_backend())  # type: Certificate
            subj_alt_name = cert.extensions.get_extension_for_oid(
                ExtensionOID.SUBJECT_ALTERNATIVE_NAME)  # type: Optional[SubjectAlternativeName]
            if not subj_alt_name:
                return None
            emails = subj_alt_name.value.get_values_for_type(x509.RFC822Name)
            if emails:
                return emails[0]
    except Exception as e:
        raise e
        # return None
    return None


# variations seen for this commands:  "submit"  "batch"
@click.command('interactive', short_help="Request an \"interactive\" job.")
@click.option("--project", envvar='GPULAB_PROJECT', required=True, prompt=False)
@click.option("--duration-minutes", required=True, prompt=False)
@click.option("--docker-image", required=True, prompt=False)
@click.option('-p', '--proxy', 'proxy', flag_value='yes', default=True,
              help="Use the jFed proxy to reach the container")
@click.option('-P', '--no-proxy', 'proxy', flag_value='no', default=False,
              help="Don't use the jFed proxy to reach the container (requires IPv6 or VPN)")
@click.option('--auto-proxy', 'proxy', flag_value='auto', default=False,
              help="Automatically use the jFed proxy to reach the container")
@click.option("--only-show", is_flag=True,
              help="Do nothing except showing the job request")
@click.option('--cpus', required=False, type=click.INT,
              help="Number of CPU cores required (default 1)")
@click.option('--gpus', required=False, type=click.INT,
              help="Number of GPU's required (default 1)")
@click.option('--mem', required=False, type=click.INT,
              help="Memory required, in GB (default 2)")
@click.option('--cluster-id', required=False, type=click.INT,
              help="Wanted cluster ID (default any)")
@click.option('--ssh-pub-key', multiple=True, help="Add an SSH public key. "
                                                   "This can be used to access the running job's container. "
                                                   "Uses the openssh public key format. "
                                                   "This option can be specified more than once, to add multiple keys.")
@click.pass_context
@require_ctx_loggedin_api_client
def run_interactive(ctx, project, duration_minutes, docker_image, proxy, ssh_pub_key: List[str],
                    only_show, cpus, gpus, mem, cluster_id):
    cpu_mem_gb = mem

    if ctx.obj[VERBOSE_DEBUG]:
        click.secho('DEBUG: run_interactive with ssh_pub_key={!r}'.format(ssh_pub_key),
                    err=False, nl=True, fg='magenta')

    command = "bash -c 'echo Interactive job wait loop starting;" \
              "echo remove /tmp/running to stop the job early;" \
              "touch /tmp/running;" \
              "I=0; " \
              "while [ $I -lt {} -a -e /tmp/running ]; " \
              "do " \
              "   for j in $(seq 1 60); " \
              "   do " \
              "      sleep 1; " \
              "      if [ ! -e /tmp/running ];" \
              "      then" \
              "         echo will stop job as /tmp/running was removed;" \
              "         exit 0;" \
              "      fi; " \
              "   done;" \
              "   let I+=1; " \
              "   echo Slept $I minutes in total; " \
              "done;" \
              "echo Interactive job wait loop finished;'".format(duration_minutes)
    deployment_env = 'staging' if ctx.obj[DEPLOY_ENV_IS_STAGING] else 'production'
    job_request = Job2.from_dict({
        "deploymentEnvironment": deployment_env,
        "name": "cli-interactive-{}min".format(duration_minutes),
        "description": "Interactive job, max {} minutes duration".format(duration_minutes),
        "request": {
            "docker": {
                "image": docker_image,
                "command": command,
                "storage": [{"containerPath": "/project"}]
            },
            "resources": {
                "clusterId": cluster_id,  # None is fine here
                "cpus": cpus if cpus is not None else 1,
                "gpus": gpus if gpus is not None else 1,
                "cpuMemoryGb": cpu_mem_gb if cpu_mem_gb is not None else 2
            },
            "extra": {
                "sshPubKeys": list(ssh_pub_key)
            },
            "scheduling": {
                "interactive": True,
                "restartable": False,
                "maxDuration": "{} minutes".format(duration_minutes),
            },
        },
    })

    if only_show:
        job_request_dict = strip_null_from_json_dict(
            job_request.to_dict(), strip_empty_dict=True, strip_empty_list=True, process_lists=True)
        print(json.dumps(job_request_dict, indent=4))
        # print(yaml.dump(jobdef, default_flow_style=False))
        return None

    job_id = actual_run_with_job(
        ctx, _get_project_urn(ctx, project),
        False, True, False, False, False, False,
        ssh_pub_key, job_request)
    actual_ssh(ctx, job_id, False, False, proxy)


# variations seen for this commands:  "submit"  "batch"
@click.command('submit', short_help="Submit a job request")
# prompt MUST be false: otherwise, stdin will be used, and we need that later!
@click.option("--project", envvar='GPULAB_PROJECT', required=True, prompt=False)
# @click.option('-I','--interactive', is_flag=True, help="Interactive jobs. Wait for job ready, then connect terminal.")
@click.option('--wait-run', is_flag=True, help="Wait until job is running.")
@click.option('--wait-done', is_flag=True, help="Wait until job is done.")
@click.option('--email-queued', is_flag=True, help="Send email when job is queued.")
@click.option('--email-run', is_flag=True, help="Send email when job is running.")
@click.option('--email-done', is_flag=True, help="Send email when job is done.")
@click.option('--hold', is_flag=True, help="Do not queue job, immediately put it on hold")
@click.option('--ssh-pub-key', multiple=True, help="Add an SSH public key. "
                                                   "This can be used to access the running job's container. "
                                                   "Uses the openssh public key format. "
                                                   "This option can be specified more than once, to add multiple keys.")
@click.pass_context
@require_ctx_loggedin_api_client
def run(ctx, project: str, hold: bool, wait_run: bool, wait_done: bool,
        email_queued: bool, email_run: bool, email_done: bool, ssh_pub_key: List[str]):
    actual_run(ctx, _get_project_urn(ctx, project), hold, wait_run, wait_done, email_queued, email_run, email_done, ssh_pub_key)


def actual_run(ctx, project_urn: str, hold: bool, wait_run: bool, wait_done: bool,
               email_queued: bool, email_run: bool, email_done: bool, ssh_pub_key: List[str],):
    """Submit a docker image to run on a GPU node"""
    deployment_env = 'staging' if ctx.obj[DEPLOY_ENV_IS_STAGING] else 'production'
    job_json_raw = None
    try:
        job_json_raw = str(click.get_text_stream('stdin').read())
        job_json_dict = json.loads(job_json_raw)
        if is_jsondict_job1(job_json_dict):
            job_json_dict['gpulab_version'] = deployment_env
        else:
            job_json_dict['deploymentEnvironment'] = deployment_env
        job = any_jsondict_to_job2(job_json_dict)  # support both Job1 and Job2
        assert job.deployment_environment == deployment_env
        assert job.state is None
    except:
        if ctx.obj[VERBOSE_DEBUG]:
            click.secho('Could not parse provided Job: {!r}'.format(job_json_raw),
                        err=True, nl=True, fg='red')
            traceback.print_exc()
        raise click.ClickException("Could not parse provided Job (--debug for max details)")
    # job = Job2.from_json(job_json_raw)
    return actual_run_with_job(ctx, project_urn, hold, wait_run, wait_done, email_queued, email_run, email_done,
                               ssh_pub_key, job)


def actual_run_with_job(ctx, project_urn: str, hold: bool, wait_run: bool, wait_done: bool,
                        email_queued: bool, email_run: bool, email_done: bool, ssh_pub_key: List[str],
                        job: Job2):
    """Submit a docker image to run on a GPU node"""
    assert job.state is None

    client = ctx.obj[API_CLIENT]

    assert client.user_urn
    assert not job.owner or not job.owner.project_urn or job.owner.project_urn == project_urn
    assert not job.owner or not job.owner.user_urn or job.owner.user_urn == client.user_urn
    client_email_address = _get_email_address(ctx)
    if not client_email_address:
        click.secho('Could not find your email address (will continue without email triggers)',
                    err=True, nl=True, fg='red')
        # will probably fail next because client_email_address may not be None...
    job = job.replace_owner_attrs(user_urn=client.user_urn, user_email=client_email_address, project_urn=project_urn)

    try:
        extra_ssh_pubkeys = _get_public_keys(ctx)
        if ssh_pub_key:
            extra_ssh_pubkeys.append(ssh_pub_key)
        if extra_ssh_pubkeys:
            job = job.replace_request_extra_attrs(ssh_pub_keys=extra_ssh_pubkeys)
        if ctx.obj[VERBOSE_DEBUG]:
            click.secho('Added {} SSH keys to submit request which now has {} keys'
                        .format(len(extra_ssh_pubkeys), len(job.request.extra.ssh_pub_keys)), nl=True)
    except:
        click.secho('Error while trying to add public ssh key(s) to job (will continue without)',
                    err=True, nl=True, fg='red')

    def _unique(inp: list) -> list:
        helper = set()
        res = []
        for e in inp:
            if e not in helper:
                res.append(e)
            helper.add(e)
        return res

    if client_email_address and (email_queued or email_run or email_done):
        if email_queued:
            job = job.replace_request_extra_attrs(
                email_on_queue=_unique(([client_email_address] if email_queued else []) + job.request.extra.email_on_queue),
                email_on_run=_unique(([client_email_address] if email_run else []) + job.request.extra.email_on_run),
                email_on_end=_unique(([client_email_address] if email_done else []) + job.request.extra.email_on_end),
                email_on_halt=[],
                email_on_restart=[],
            )

    if ctx.obj[VERBOSE_DEBUG]:
        click.secho('Final Job Definition:\n{}'.format(json.dumps(job.to_dict(remove_none=True), indent=4)), nl=True)

    s = client.get_session()
    params = {}
    if hold:
        params['hold'] = 'true'
    url = client.get_api_url(3) + "jobs"
    r = s.post(url, json=job.to_dict(remove_none=True), params=params, timeout=GPULAB_CLIENT_TIMEOUT)

    if r.ok:
        job_id = r.text
        print(job_id)
    elif r.status_code == 403:
        raise click.ClickException('No permission to submit job. Did you specify a correct project? ({!r})'.format(r.text))
    else:
        raise click.ClickException('Job submission to {!r} failed: {!r}'.format(url, r.content))

    if wait_run or wait_done:
        actual_wait(ctx, job_id, wait_run, wait_done)

    return job_id


# queue has been merged as special case of "jobs"

# # variations seen for this commands:  "queue"  "stat"   "query"   "history"
# @click.command("queue", short_help="list queued jobs")
# @click.option('-u','--user', is_flag=True, help="Only jobs for the calling user")
# @click.option('-r','--raw', is_flag=True, help="Return JSON-objects")
# @click.pass_context
def queue(ctx, raw: bool, user: bool, always_add_running_jobs: bool,
          max_hours: Optional[int], max_count: Optional[int]):
    """Returns the list of queued jobs"""
    check_and_warn_version(ctx)

    client = ctx.obj[API_CLIENT]
    s = client.get_session()
    params = {}

    if user:
        if not client.user_urn:
            raise click.ClickException("--user option caused internal error: could not find user_urn")
        params['user_urn'] = client.user_urn
        if always_add_running_jobs:
            params['other_user_running'] = True

    if not max_hours and user:
        max_hours = 7 * 24  # increase default if only for calling user
    if not max_count and user:
        max_count = 50    # increase default if only for calling user

    if max_hours:
        params['max_hours'] = max_hours
    if max_count:
        params['max_count'] = max_count

    r = s.get(client.get_api_url(3) + "jobs", params=params, timeout=GPULAB_CLIENT_TIMEOUT)

    if not r.ok:
        raise click.ClickException("Could not retrieve queued jobs: {}".format(r.text))

    try:
        def ignore_unknown_fields(field_name: str):
            if ctx.obj[VERBOSE_DEBUG]:
                click.secho('WARNING: ignoring unknown field in reply: {!r}'.format(field_name),
                            err=False, nl=True, fg='red')

        jobs_raw_dicts = r.json()
        jobs: List[Job2] = Job2.from_dict_list(jobs_raw_dicts, on_unknown_field_override=ignore_unknown_fields)
    except:
        if ctx.obj[VERBOSE_DEBUG]:
            traceback.print_exc()
        raise click.ClickException("Could not parse server answer: {!r}".format(r.content))

    if raw:
        print(json.dumps(jobs_raw_dicts, indent=4))
    else:
        print("%-36s %-20.20s %-20.20s %-25.25s %-12.12s %-15.15s %-3s %-10.10s" % (
            "TASK ID", "NAME", "COMMAND", "CREATED", "USER", "PROJECT", "CID", "STATUS"))

        jobs_for_ssh_config = []
        for job in jobs:
            assert job is not None

            def handle_none(none_or_str: Optional[str]):
                if not none_or_str:
                    return '***'
                else:
                    return none_or_str

            job_status = job.state.status.name if job.state else None

            print("%-36s %-20.20s %-20.20s %-25.25s %-12.12s %-15.15s %-3s %-10.10s" %
                  (job.uuid,
                   handle_none(job.name),
                   handle_none(job.request.docker.command_as_str),
                   handle_none(_date_to_str(job.state.event_times.created) if job.state else None),
                   handle_none(job.owner.user_mini_id),
                   handle_none(job.owner.project_name),
                   handle_none(job.state.resources.cluster_id if job.state and job.state.resources else None),
                   handle_none(job_status)
                   ))
            if job.owner.user_urn.lower() == ctx.obj[API_CLIENT].user_urn.lower() and \
                    job.state.status in (JobStatus.RUNNING, ):  # ignoring JobStatus.ASSIGNED, JobStatus.STARTING
                jobs_for_ssh_config.append(job)

        if jobs_for_ssh_config:
            set_jobs_ssh_config(
                login_pem_filename=ctx.obj[CERTFILE],
                jobs=jobs_for_ssh_config,
                debug=ctx.obj[VERBOSE_DEBUG]
            )
        elif ctx.obj[VERBOSE_DEBUG]:
            click.echo(f'No running user owned jobs (of {len(jobs)} jobs) to write to ssh_config')

# variations seen for this commands:  "revoke" "abort" "cancel" "del" "rm"  "edit"
@click.command("rm", short_help="Remove job")
@click.argument('job_id', type=click.STRING)
@click.option('-f', '--finished', is_flag=True, help="Allow removing finished (and aborted) jobs")
@click.option('-r', '--real', is_flag=True, help="Really delete the Job (requires admin access). "
                                                 "If not specified, the job is only marked as deleted")
@click.option('-F', '--force', is_flag=True, help="Delete job in whatever state it is. (requires admin access)")
@click.pass_context
@require_ctx_loggedin_api_client
def rm(ctx, job_id, finished, real, force):
    if not real and force:
        raise click.ClickException("Incompatible options: --force requires --real")

    client = ctx.obj[API_CLIENT]
    s = client.get_session()
    params = {}
    if finished:
        params['finished'] = 'true'
    if real:
        params['real'] = 'true'
    if force:
        params['force'] = 'true'
    r = s.delete(client.get_api_url(3) + "jobs/" + job_id, params=params, timeout=GPULAB_CLIENT_TIMEOUT)

    if r.ok:
        print(job_id)
    else:
        raise click.ClickException("Error while revoking request: {}".format(r.text))


# variations seen for this commands:  "revoke" "abort" "cancel" "del" "rm"  "edit"
@click.command("cancel", short_help="Cancel running job")
@click.argument('job_id', type=click.STRING)
@click.pass_context
@require_ctx_loggedin_api_client
def cancel(ctx, job_id):
    client = ctx.obj[API_CLIENT]
    s = client.get_session()
    r = s.put("{}jobs/{}/state/status".format(client.get_api_url(3), job_id), data='CANCELLED', timeout=GPULAB_CLIENT_TIMEOUT)

    if r.ok:
        print(job_id)
    else:
        raise click.ClickException("Error while cancelling job: {}".format(r.text))


@click.command("halt", short_help="Halt a running job. This is used to test the HALTING procedure of a job. "
                                  "Status change: RUNNING -> MUSTHALT -> HALTING -> FAILURE or HALTED")
@click.argument('job_id', required=True, type=click.STRING)
@click.pass_context
@require_ctx_loggedin_api_client
def halt_job(ctx, job_id):
    client = ctx.obj[API_CLIENT]
    s = client.get_session()
    r = s.put("{}jobs/{}/state/status".format(client.get_api_url(3), job_id), data='MUSTHALT', timeout=GPULAB_CLIENT_TIMEOUT)

    if r.ok:
        print(job_id)
    else:
        raise click.ClickException("Error while halting job: {}".format(r.text))


# variations seen for this commands:  "revoke" "abort" "cancel" "del" "rm"  "edit"
@click.command("hold", short_help="Hold queued job(s). Status will change from QUEUED to ONHOLD")
@click.argument('job_id', required=False, type=click.STRING)
@click.option('-a', '--all', is_flag=True, help="Hold all (currently QUEUED) jobs of the calling user")
@click.pass_context
@require_ctx_loggedin_api_client
def hold_job(ctx, job_id, all):
    if not job_id and not all:
        raise click.ClickException("Not enough options: --all or a <job_id> required")
    if job_id and all:
        raise click.ClickException("Incompatible options: Either --all or a <job_id> required, but not both")
    if all:
        raise click.ClickException("--all is not yet implemented")

    client = ctx.obj[API_CLIENT]
    s = client.get_session()
    r = s.put("{}jobs/{}/state/status".format(client.get_api_url(3), job_id), data='ONHOLD', timeout=GPULAB_CLIENT_TIMEOUT)

    if r.ok:
        print(job_id)
    else:
        raise click.ClickException("Error while holding job: {}".format(r.text))


# variations seen for this commands:  "revoke" "abort" "cancel" "del" "rm"  "edit"
@click.command("release", short_help="Release held job(s). Status will change from ONHOLD to QUEUED")
@click.argument('job_id', required=False, type=click.STRING)
@click.option('-a', '--all', is_flag=True, help="Release all (currently ONHOLD) jobs of the calling user")
@click.pass_context
@require_ctx_loggedin_api_client
def release(ctx, job_id, all):
    if not job_id and not all:
        raise click.ClickException("Not enough options: --all or a <job_id> required")
    if job_id and all:
        raise click.ClickException("Incompatible options: Either --all or a <job_id> required, but not both")
    if all:
        raise click.ClickException("--all is not yet implemented")

    client = ctx.obj[API_CLIENT]
    s = client.get_session()
    r = s.put("{}jobs/{}/state/status".format(client.get_api_url(3), job_id), data='QUEUED', timeout=GPULAB_CLIENT_TIMEOUT)

    if r.ok:
        print(job_id)
    else:
        raise click.ClickException("Error while releasing job: {}".format(r.text))


# variations seen for this commands:  "log" "tail"
@click.command("log", short_help="Retrieve a job's log")
@click.argument('job_id', type=click.STRING)
# @click.option('-t', '--tail', is_flag=True, help="receive only last bytes of the log")
@click.option('-f', '--follow', is_flag=True, help="Keep receiving data as it becomes available (experimental feature, bugs possible!)")
# @click.option('-r', '--raw', is_flag=True, help="Return JSON-objects")
# @click.option('--timestamps/--no-timestamps', help="Show timestamps", default=True)
@click.pass_context
@require_ctx_loggedin_api_client
def get_log(ctx, job_id, follow):
    # def get_logs(ctx, job_id, raw, timestamps):
    client = ctx.obj[API_CLIENT]  # type: Union[GpuLabApiLocalhostModeClient, GpuLabApiClient]
    s = client.get_session()  # type: requests.Session

    if follow:
        click.secho('You are using the experimental --follow option. \nWhile it mostly works, '
                    'there are some client and server side bugs that pop up from time to time. \n'
                    'In case of problems, please retry, or check the log without --follow. \n'
                    'You may also send a bug report to: gpulab@ilabt.imec.be',
                    err=True, nl=True, fg='yellow')

    previous_end_byte = None
    while previous_end_byte is None or follow:
        # if follow, then keep requesting periodically (infinitely!), using range header
        headers = {}
        if previous_end_byte:
            headers['Range'] = 'bytes={}-'.format(previous_end_byte)
            sleep(1.0)

        with s.get("{}jobs/{}/log".format(client.get_api_url(2), job_id), stream=True, headers=headers, timeout=GPULAB_CLIENT_TIMEOUT) as r:
            if not r.ok:
                raise click.ClickException("Error while fetching log for {}: {}".format(job_id, r.text))

            if r.status_code == 200 or r.status_code == 206: # 200 OK  206 Partial content
                for line in r.iter_lines():
                    print(line.decode())

                if 'Content-Range' in r.headers:
                    content_range = r.headers.get('Content-Range')  # format: "bytes {0}-{1}/{2}"
                    match = re.match(r'bytes ([0-9]+)-([0-9]+)/([0-9]+)', content_range)
                    previous_end_byte = int(match.group(2))
                else:
                    if 'Content-Length' in r.headers:
                        previous_end_byte = int(r.headers.get('Content-Length'))
                    else:
                        previous_end_byte = 0
            elif r.status_code == 204:  # 204 No content
                if follow:
                    pass  # no data at the moment
                else:
                    click.secho('No log data available (yet?)', err=True, nl=True, fg='yellow')
            else:
                click.secho('Unexpected reply HTTP status in GPULab reply: {}'.format(r.status_code),
                            err=True, nl=True, fg='red')


@click.command("debug",
               short_help="Retrieve a job's debug info. (Do not rely on the presence or format of this info. "
                          "It will never be stable between versions. If this has the only source of info you need, "
                          "ask the developers to expose that info in a different way!)")
@click.argument('job_id', type=click.STRING)
@click.option('-r', '--raw', is_flag=True, help="Return JSON-objects")
@click.pass_context
@require_ctx_loggedin_api_client
def get_debug(ctx, job_id, raw):
    client = ctx.obj[API_CLIENT]
    s = client.get_session()  # type: requests.Session

    with s.get("{}jobs/{}/debug".format(client.get_api_url(2), job_id), stream=True, timeout=GPULAB_CLIENT_TIMEOUT) as r:
        if not r.ok:
            raise click.ClickException("Error while fetching events for {}: {}".format(job_id, r.text))

        try:
            events = r.json()
        except ValueError:
            raise click.ClickException("Could not parse server answer")

        if raw:
            print(json.dumps(events, indent=4))
        else:
            for e in events:
                assert e is not None
                event = JobEvent.from_dict(e)

                if event.type == JobEventType.STATUS_CHANGE:
                    print('{} STATE CHANGED -> {}'.format(_date_to_str(event.time), event.new_status.name if event.new_status else 'unknown new_state'))
                else:
                    print('{} LOG {}: {}'.format(_date_to_str(event.time), event.type.name, event.msg))


@click.command("clusters",
               short_help="Retrieve info about the available clusters. "
                          "If a cluster_id is specified, detailed info about the slaves of that cluster is shown.")
@click.argument('cluster_id', type=click.STRING, required=False)
@click.option('-r', '--raw', is_flag=True, help="Return JSON-objects")
@click.option('-a', '--all', is_flag=True, help="(if no <cluster_id>) Show all slave info")
@click.option('-n', '--no-lines', is_flag=True, help="Do not draw lines to seperate the columns")
@click.option('-s', '--short', is_flag=True, help="(if <cluster_id> provided) "
                                                  "Short summary (excluding some data)")
@click.pass_context
@require_ctx_any_api_client
def get_slave_info(ctx, cluster_id: Optional[str], all: bool, raw: bool, short: bool, no_lines: bool):
    """Returns info for each cluster.

    When --short is used, slash-seperated numbers represent the 'free' and 'total' quantity for Workers, GPUs, CPUs and memory (format XX/YY)
    (for example: XX/YY means  now XX free, of YY in total)"""
    client = ctx.obj[API_CLIENT]
    s = client.get_session()  # type: requests.Session

    if cluster_id is None and not all:
        with s.get("{}clusters".format(client.get_api_url(3)), stream=True, timeout=GPULAB_CLIENT_TIMEOUT) as r:
            if not r.ok:
                raise click.ClickException("Error while fetching clusters: {}".format(r.text))

            try:
                cluster_info_dicts = r.json()
                cluster_infos: List[ClusterInfo] = \
                    ClusterInfo.from_dict_list(cluster_info_dicts, on_unknown_field_override=ignore_unknown_fields)
            except ValueError:
                raise click.ClickException("Could not parse server answer")

            if raw:
                print(json.dumps(cluster_info_dicts, indent=4))
            else:
                header = [ 'ID', 'GPU Model', 'Comment', 'Slaves', 'GPUs', 'CPUs' ]
                rows = []
                for cluster_info in cluster_infos:
                    assert cluster_info is not None
                    rows.append([
                        '{} {}'.format(cluster_info.cluster_id, cluster_info.deployment_environment),
                        ','.join([m.name for m in cluster_info.gpu_model]),
                        cluster_info.comment,
                        cluster_info.slave_count,
                        '{}/{}'.format(cluster_info.gpu.available, cluster_info.gpu.acquired),
                        '{}/{}'.format(cluster_info.cpu.available, cluster_info.cpu.acquired)
                    ])
                _print_table(header, rows, add_hor_lines=not no_lines, add_vert_lines=not no_lines)
    else:
        with s.get("{}slaves".format(client.get_api_url(3)), stream=True, timeout=GPULAB_CLIENT_TIMEOUT) as r:
            if not r.ok:
                raise click.ClickException("Error while fetching slaves: {}".format(r.text))

            try:
                slave_info_dicts = r.json()
                slave_infos: List[SlaveInfo2] = \
                    SlaveInfo2.from_dict_list(slave_info_dicts, on_unknown_field_override=ignore_unknown_fields)
            except ValueError:
                raise click.ClickException("Could not parse server answer")

            if not all and cluster_id is not None:
                slave_infos = [x for x in slave_infos if str(x.cluster_id) == str(cluster_id)]

            if raw:
                print(json.dumps(slave_info_dicts, indent=4))
            else:
                if short:
                    header = ['Slave host', 'Cluster', 'DeployEnv', 'Workers', 'GPUs', 'CPUs', 'Memory (GB)']
                    rows = []
                    for slave_info in slave_infos:
                        assert isinstance(slave_info, SlaveInfo2)
                        rows.append([slave_info.name,
                                     slave_info.cluster_id,
                                     slave_info.deployment_environment,
                                     '{:d}/{:d}'.format(slave_info.worker.available, slave_info.worker.acquired),
                                     '{:d}/{:d}'.format(slave_info.gpu.available, slave_info.gpu.acquired),
                                     '{:d}/{:d}'.format(slave_info.cpu.available, slave_info.cpu.acquired),
                                     '{:>.2f}/{:<.2f}'.format((slave_info.cpu_memory_mb.available) / 1000,
                                                              slave_info.cpu_memory_mb.acquired / 1000)
                                     ])
                    _print_table(header, rows, add_hor_lines=not no_lines, add_vert_lines=not no_lines)
                else:
                    print('*' * 80)
                    print('Full Cluster info (use --short for a summary)')
                    for slave_info in slave_infos:
                        assert isinstance(slave_info, SlaveInfo2)
                        print('*' * 80)
                        print('Host "{}"'.format(slave_info.name))
                        print('Cluster {}'.format(slave_info.cluster_id))
                        print('Deployment Environment "{}"'.format(slave_info.deployment_environment))
                        print('            Free    | Total')
                        print('   Workers: {:<7d} | {:<7d}'.format(slave_info.worker.available,
                                                                   slave_info.worker.acquired))
                        print('   GPUs:    {:<7d} | {:<7d}'.format(slave_info.gpu.available,
                                                                   slave_info.gpu.acquired))
                        print('   CPUs:    {:<7d} | {:<7d}'.format(slave_info.cpu.available,
                                                                   slave_info.cpu.acquired))
                        print('   Memory:  {:<7.2f} | {:<7.2f} (GB)'.format(
                            (slave_info.cpu_memory_mb.available) / 1000,
                            slave_info.cpu_memory_mb.acquired / 1000))
                        print('   GPU model: {}'.format(', '.join([m.name for m in slave_info.gpu_model])))
                        print('   CPU model: {}'.format(', '.join(slave_info.cpu_model)))
                        print('   CUDA version: {}'.format(slave_info.cuda_version_full))
                        print('   Updated: {} ({})'.format(_date_to_str(slave_info.last_update),
                                                           _date_to_ago_str(slave_info.last_update)))
                        print('   Comment: {}'.format(slave_info.comment))
                    print('*' * 80)


# variations seen for this commands:  "queue" "info" "query" "show" "stat" "status"
@click.command("jobs", short_help="Get info about one or more jobs")
@click.argument('job_id', type=click.STRING, required=False)
@click.option('-H', '--max-hours', required=False, type=click.INT,
              help="Show all jobs in the last X hours (default 12 (168 with -u), max 744 (=31 days))")
@click.option('-c', '--max-count', required=False, type=click.INT,
              help="Show no more than X jobs (default 10 (50 with -u), max 200)")
@click.option('-u', '--user', is_flag=True, help="Info on all jobs for the calling user + other user's running jobs")
@click.option('-U', '--strict-user', is_flag=True, help="Info on all jobs for the calling user (and no other user's jobs)")
@click.option('-r', '--raw', is_flag=True, help="Return JSON-object")
@click.option('-d', '--definition', is_flag=True, help="Show only the job definition (requires <job_id>)")
@click.pass_context
@require_ctx_loggedin_api_client
def get_info(ctx, job_id: str, raw: bool, user: bool, definition: bool,
             max_hours: Optional[int], max_count: Optional[int],
             strict_user: bool):
    if job_id and user:
        raise click.ClickException("Incompatible options: Either --user or a <job_id>, but not both.  (job_id={})".format(job_id))

    if definition and not job_id:
        raise click.ClickException("Incompatible options: --definition requires a <job_id>")

    if not job_id:
        return queue(ctx, raw, user or strict_user, not strict_user, max_hours, max_count)

    client = ctx.obj[API_CLIENT]
    s = client.get_session()  # type: requests.Session

    r = s.get(client.get_api_url(3) + "jobs/" + job_id, timeout=GPULAB_CLIENT_TIMEOUT)

    if r.ok:
        job_dict = r.json()

        if raw:
            print(json.dumps(job_dict, indent=4))
        else:
            def ignore_unknown_fields(field_name: str):
                if ctx.obj[VERBOSE_DEBUG]:
                    click.secho('WARNING: ignoring unknown field in reply: {!r}'.format(field_name),
                                err=False, nl=True, fg='red')

            job: Job2 = Job2.from_dict(job_dict, on_unknown_field_override=ignore_unknown_fields)

            if definition:
                print(json.dumps(job.nvdocker_data, indent=4))
            else:
                def handle_none(i: Optional[Any]) -> Any:
                    if i is None:
                        return '-'
                    else:
                        return i

                print("{:>15}: {}".format("Job ID", job.uuid))
                print("{:>15}: {}".format("Name", handle_none(job.name)))
                print("{:>15}: {}".format("Description", handle_none(job.description)))
                print("{:>15}: {}".format("Project", handle_none(job.owner.project_name) if job.owner else None))
                print("{:>15}: {}".format("User URN", handle_none(job.owner.user_urn) if job.owner else None))
                print("{:>15}: {}".format("User ID", handle_none(job.owner.user_mini_id) if job.owner else None))
                print("{:>15}: {}".format("Docker image", handle_none(job.request.docker.image_nopass)))
                print("{:>15}: {}".format("Command", handle_none(job.request.docker.command_as_str)))

                status = job.state.status.name if job.state and job.state.status else None
                print("{:>15}: {}".format("Status", handle_none(status)))
                if job.state == JobStatus.FAILED:
                    print("{:>15}  {}".format("", 'More info about FAILED: gpulab-cli{} debug {}'.format((' --staging' if ctx.obj[DEPLOY_ENV_IS_STAGING] else ''), job.uuid)))
                print("{:>15}: {}".format("Cluster ID", handle_none(job.state.resources.cluster_id) if job.state and job.state.resources else None))
                print("{:>15}: {}".format("Worker ID", handle_none(job.state.resources.worker_id) if job.state and job.state.resources else None))
                if job.state and job.state.resources:
                    if job.state.resources.slave_name:
                        print("{:>15}: {}".format("Worker Name", job.state.resources.slave_name) if job.state and job.state.resources else None)
                    if job.state.resources.port_mappings:
                        print("{:>15}: {}".format("Port Mappings", _port_mapping_format(job.state.resources.port_mappings) if job.state and job.state.resources else None))
                        if job.state.resources.slave_host:
                            print("{:>15}: {}".format("Worker Host", job.state.resources.slave_host) if job.state and job.state.resources else None)
                    if job.state.resources.ssh_username and job.state.resources.ssh_host and job.state.resources.ssh_port:
                        cert_arg = ' -i \'{}\''.format(ctx.obj[CERTFILE]) if ctx.obj[CERTFILE_IN_ARGUMENTS] else ''
                        ssh_login_str = 'ssh{}{} {}@{}'.format(
                            cert_arg,
                            _ssh_port_command(job.state.resources.ssh_port),
                            job.state.resources.ssh_username, job.state.resources.ssh_host)
                        if job.state.resources.ssh_proxy_host:
                            ssh_proxy_login_str = ' -oProxyCommand="ssh{}{} {}@{} -W %h:%p"'.format(
                                cert_arg,
                                _ssh_port_command(job.state.resources.ssh_proxy_port),
                                job.state.resources.ssh_proxy_username, job.state.resources.ssh_proxy_host)
                            ssh_login_str += ssh_proxy_login_str
                        print("{:>15}: {}".format("SSH login:", ssh_login_str))
                if job.state:
                    def _show_rel(shown_dt: Optional[datetime.datetime],
                                  earlier_dt: Optional[datetime.datetime],
                                  after_subject) -> str:
                        if not shown_dt or not earlier_dt:
                            return ''
                        rel_str = td_format(shown_dt - earlier_dt)
                        return ' ({} after {})'.format(rel_str, after_subject)
                    def _show_ago(shown_dt: Optional[datetime.datetime]) -> str:
                        if not shown_dt:
                            return ''
                        rel_str = td_format(datetime_now() - shown_dt)
                        return ' ({} ago)'.format(rel_str)
                    print("{:>15}: ".format("Timing"))
                    if job.state.event_times:
                        print("{:>20}: {}".format("Created", handle_none(_date_to_str(job.state.event_times.created)))
                              +_show_ago(job.state.event_times.created))
                        print("{:>20}: {}".format("Queued", handle_none(_date_to_str(job.state.event_times.QUEUED)))
                              +_show_rel(job.state.event_times.QUEUED, job.state.event_times.created, 'job creation'))
                        print("{:>20}: {}".format("Assigned", handle_none(_date_to_str(job.state.event_times.ASSIGNED)))
                              +_show_rel(job.state.event_times.ASSIGNED, job.state.event_times.QUEUED, 'QUEUED'))
                        print("{:>20}: {}".format("Starting", handle_none(_date_to_str(job.state.event_times.STARTING)))
                              +_show_rel(job.state.event_times.STARTING, job.state.event_times.ASSIGNED, 'ASSIGNED'))
                        print("{:>20}: {}".format("Running", handle_none(_date_to_str(job.state.event_times.RUNNING)))
                              +_show_rel(job.state.event_times.RUNNING, job.state.event_times.STARTING, 'STARTING'))
                        if job.state.event_times.MUSTHALT and job.state.event_times.HALTING:
                            print("{:>20}: {}".format("HALT request", handle_none(_date_to_str(job.state.event_times.MUSTHALT)))
                                  +_show_rel(job.state.event_times.MUSTHALT, job.state.event_times.RUNNING, 'RUNNING'))
                            print("{:>20}: {}".format("HALT procedure start", handle_none(_date_to_str(job.state.event_times.HALTING)))
                                  +_show_rel(job.state.event_times.HALTING, job.state.event_times.MUSTHALT, 'HALT request'))
                            if job.state.event_times.HALTED:
                                print("{:>20}: {}".format("HALT success", handle_none(_date_to_str(job.state.event_times.HALTED)))
                                      +_show_rel(job.state.event_times.HALTED, job.state.event_times.HALTING, 'HALT procedure start'))
                            if job.state.event_times.FAILED:
                                print("{:>20}: {}".format("HALT failure", handle_none(_date_to_str(job.state.event_times.FAILED)))
                                      +_show_rel(job.state.event_times.FAILED, job.state.event_times.HALTING, 'HALT procedure start'))
                        print("{:>20}: {}".format("Ended", handle_none(_date_to_str(job.state.event_times.end_date())))
                              #+_show_rel(job.state.event_times.end_date(), job.state.event_times.RUNNING, 'RUNNING')
                              +_show_ago(job.state.event_times.end_date()))
                        duration = job.state.event_times.get_duration()
                        print("{:>20}: {}".format("Duration", td_format(duration) if duration else "-"))
                        print("{:>20}: {}".format("State Updated", handle_none(_date_to_str(job.state.event_times.status_updated)))
                              +_show_ago(job.state.event_times.status_updated))

            # also store job SSH config if needed
            add_job_ssh_config(
                login_pem_filename=ctx.obj[CERTFILE],
                job=job,
                return_proxy_fake_hostname=True,
                debug=ctx.obj[VERBOSE_DEBUG]
            )
    else:
        raise click.ClickException("Could not retrieve info for job '{}': {}".format(job_id, r.text))


@click.command("wait", short_help="Wait for a job to change state")
@click.argument('job_id', type=click.STRING)
@click.option('--wait-run', is_flag=True, help="Wait until job is running.",
              cls=NotRequiredIf, not_required_if='wait_done')
@click.option('--wait-done', is_flag=True, help="Wait until job is done.",
              cls=NotRequiredIf, not_required_if='wait_run')
@click.pass_context
@require_ctx_loggedin_api_client
def wait(ctx, job_id, wait_run, wait_done):
    actual_wait(ctx, job_id, wait_run, wait_done)


def actual_wait(ctx, job_id, wait_run, wait_done):
    client = ctx.obj[API_CLIENT]
    s = client.get_session()

    job_update_url = client.get_api_url(3) + "jobs/" + job_id

    sys.stdout.flush()
    sys.stderr.flush()

    outstream = sys.stderr

    prev_status = None
    prev_state_start_time = datetime.datetime.now(datetime.timezone.utc)

    start_wait_time = datetime.datetime.now(datetime.timezone.utc)

    # print('Wait line format: <absolute time> - <relative time> - message', file=sys.stderr)

    def now_localtz() -> datetime:
        return datetime.datetime.now().astimezone()

    def line_prefix(show_relative: bool = True):
        rel_time = datetime.datetime.now(datetime.timezone.utc) - start_wait_time
        rel_time_str = td_format(rel_time)
        needed_spaces = 10 - len(rel_time_str)
        if needed_spaces > 0:
            rel_time_str += ' ' * needed_spaces
        return '{:%Y-%m-%d %H:%M:%S %z} - {} - '.format(
            now_localtz(),
            rel_time_str if show_relative else (' ' * 10)
        )

    wait_line_prefix = (' ' * 39) + '  '

    prev_state_wait_time_pass = False

    if wait_run or wait_done:
        print(line_prefix(False)+'Waiting for Job to start running...', file=sys.stderr)
        queued = True
        print_requires_newline_first = False
        print_for_backspace_required = 0
        while queued:
            sys.stdout.flush()
            sys.stderr.flush()
            sleep(2)
            wait_time = datetime.datetime.now(datetime.timezone.utc) - start_wait_time
            r = s.get(job_update_url, timeout=GPULAB_CLIENT_TIMEOUT)
            if r.ok:
                job2_dict = r.json()

                def ignore_unknown_fields(field_name: str):
                    if ctx.obj[VERBOSE_DEBUG]:
                        click.secho('WARNING: ignoring unknown field in reply: {!r}'.format(field_name),
                                    err=False, nl=True, fg='red')

                job: Job2 = Job2.from_dict(job2_dict, on_unknown_field_override=ignore_unknown_fields)
                if prev_status != job.state:
                    if print_requires_newline_first:
                        print(file=outstream)
                    print(line_prefix()+'Job is in state {}'
                          .format(job.state.status.name if job.state else 'None'),
                          file=outstream)
                    prev_state_start_time = datetime.datetime.now(datetime.timezone.utc)
                    print_requires_newline_first = False
                    print_for_backspace_required = 0
                else:
                    cur_state_time = datetime.datetime.now(datetime.timezone.utc) - prev_state_start_time
                    toprint = wait_line_prefix+'    state unchanged for {}'.format(td_format(cur_state_time))
                    print(('\b' * print_for_backspace_required)+toprint, file=outstream, end='')
                    print_for_backspace_required = len(toprint)
                    print_requires_newline_first = True

                outstream.flush()
                queued = job.state.status == JobStatus.QUEUED \
                         or job.state.status == JobStatus.ASSIGNED \
                         or job.state.status == JobStatus.STARTING
                prev_status = job.state.status
            else:
                if print_requires_newline_first:
                    print_requires_newline_first = False
                    print(file=outstream)
                print(line_prefix()+'Error fetching job info. Give up waiting.', file=outstream)
                queued = False
                return
        prev_state_wait_time_pass = True
        if print_requires_newline_first:
            print_requires_newline_first = False
            print(file=outstream)
        print(line_prefix()+'Job is now running', file=outstream)

    if not prev_state_wait_time_pass:
        prev_status = None

    if wait_done:
        print_requires_newline_first = False
        print_for_backspace_required = 0
        print(line_prefix()+'Waiting for Job to finish...', file=outstream)
        # start_wait_time = datetime.datetime.now(datetime.timezone.utc)  # no new wait start for second wait
        running = True
        while running:
            sys.stdout.flush()
            outstream.flush()
            sleep(2)
            wait_time = datetime.datetime.now(datetime.timezone.utc) - start_wait_time
            r = s.get(job_update_url, timeout=GPULAB_CLIENT_TIMEOUT)
            if r.ok:
                def ignore_unknown_fields(field_name: str):
                    if ctx.obj[VERBOSE_DEBUG]:
                        click.secho('WARNING: ignoring unknown field in reply: {!r}'.format(field_name),
                                    err=False, nl=True, fg='red')
                job2_dict = r.json()
                job: Job2 = Job2.from_dict(job2_dict, on_unknown_field_override=ignore_unknown_fields)
                if prev_status != job.state.status or prev_state_wait_time_pass:
                    if print_requires_newline_first:
                        print(file=outstream)
                    print(line_prefix()+'Job is in state {}'
                          .format(job.state.status.name if job.state else 'None'),
                          file=outstream)
                    if not prev_state_wait_time_pass:
                        prev_state_start_time = datetime.datetime.now(datetime.timezone.utc)
                    print_requires_newline_first = False
                    print_for_backspace_required = 0
                    prev_state_wait_time_pass = False
                else:
                    cur_state_time = datetime.datetime.now(datetime.timezone.utc) - prev_state_start_time
                    toprint = wait_line_prefix+'    state unchanged for {}'.format(td_format(cur_state_time))
                    print(('\b' * print_for_backspace_required)+toprint, file=outstream, end='')
                    print_for_backspace_required = len(toprint)
                    print_requires_newline_first = True

                running = job.state.status == JobStatus.STARTING \
                          or job.state.status == JobStatus.RUNNING \
                          or job.state.status == JobStatus.MUSTHALT \
                          or job.state.status == JobStatus.HALTING
                prev_status = job.state.status
            else:
                if print_requires_newline_first:
                    print_requires_newline_first = False
                    print(file=outstream)
                print(line_prefix()+'Error fetching job info. Give up waiting.', file=outstream)
                running = False
                return
        if print_requires_newline_first:
            print_requires_newline_first = False
            print(file=outstream)
        print(line_prefix()+'Job has finished', file=outstream)

    sys.stdout.flush()
    sys.stderr.flush()


@click.command("ssh", short_help="Log in to a Job's container using SSH.")
@click.argument('job_id', required=True, type=click.STRING)
@click.option('-s', '--show', is_flag=True, help="Do not connect, only show the SSH command.")
@click.option('-p', '--proxy', 'proxy', flag_value='yes', default=False,
              help="Use the jFed proxy to reach the container")
@click.option('-P', '--no-proxy', 'proxy', flag_value='no', default=False,
              help="Don't use the jFed proxy to reach the container (requires IPv6 or VPN)")
@click.option('--auto-proxy', 'proxy', flag_value='auto', default=True,
              help="Automatically use the jFed proxy if needed to reach the container (Default)")
@click.option('-a', '--show-ansible', is_flag=True,
              help="Do not login, just show the ansible inventory line for the node. "
                   "(this never includes the jFed proxy, which must be added in the ansible ssh config)")
@click.pass_context
@require_ctx_loggedin_api_client
def ssh(ctx, job_id, show, show_ansible, proxy):
    actual_ssh(ctx, job_id, show, show_ansible, proxy)


def _has_gftp() -> bool:
    from shutil import which
    return which('gftp') is not None


def _has_filezilla() -> bool:
    from shutil import which
    return which('filezilla') is not None


@click.command("sftp", short_help="Access files in a Job's container using SFTP.")
@click.argument('job_id', required=True, type=click.STRING)
@click.option('-s', '--show', is_flag=True, help="Do not connect, only show the SFTP command.")
@click.option('-p', '--proxy', 'proxy', flag_value='yes', default=False,
              help="Use the jFed proxy to reach the container")
@click.option('-P', '--no-proxy', 'proxy', flag_value='no', default=False,
              help="Don't use the jFed proxy to reach the container (requires IPv6 or VPN)")
@click.option('--auto-proxy', 'proxy', flag_value='auto', default=True,
              help="Automatically use the jFed proxy if needed to reach the container (Default)")
@click.option('-f', '--sftp', 'sftp_command', flag_value='sftp', default=False,
              help="Use sftp command: sftp (CLI)")
@click.option('-G', '--gftp', 'sftp_command', flag_value='gftp', default=False,
              help="Use sftp command: gftp (GUI)")
@click.option('-z', '--filezilla', 'sftp_command', flag_value='filezilla', default=False,
              help="Use sftp command: filezilla (GUI)")
@click.option('-g', '--gui', 'sftp_command', flag_value='gui', default=False,
              help="Use sftp command: gftp or filezilla (GUI) (auto detect, gftp gets priority)")
@click.option('--ask-sftp-command', 'sftp_command', flag_value='ask', default=True,
              help="Use sftp command: ask if multiple present (Default)")
@click.pass_context
@require_ctx_loggedin_api_client
def sftp(ctx, job_id, show, proxy, sftp_command):
    if sftp_command == 'ask':
        has_fz = _has_filezilla()
        has_g = _has_gftp()
        if has_fz or has_g:
            keep_asking = True
            while keep_asking:
                if has_fz and has_g:
                    choice = click.prompt('Use sftp (0), gftp (1) or filezilla (2)', type=int)
                elif has_fz:
                    choice = click.prompt('Use sftp (0) or filezilla (2)', type=int)
                else:
                    choice = click.prompt('Use sftp (0) or gftp (1)', type=int)
                if choice == 0:
                    sftp_command = 'sftp'
                    keep_asking = False
                elif choice == 1:
                    sftp_command = 'gftp'
                    keep_asking = False
                elif choice == 2:
                    sftp_command = 'filezilla'
                    keep_asking = False
                else:
                    click.secho(f'Invalid value "{choice}". Try again.', err=True, nl=True, fg='red')
                    keep_asking = True
        else:
            sftp_command = 'sftp'
    if sftp_command == 'gui':
        if _has_gftp():
            sftp_command = 'gftp'
        else:
            if not _has_filezilla():
                click.secho(f'No GUI sftp client available. Install gftp or filezilla.', err=True, nl=True, fg='red')
                raise ValueError('No GUI sftp client available. Install gftp or filezilla. (Or use sftp cli.)')
            sftp_command = 'filezilla'
    actual_ssh(ctx, job_id, show, False, proxy,
               sftp_command=sftp_command)


def actual_ssh(ctx, job_id, show, show_ansible, proxy, *, sftp_command=None):
    """Log in to a Job's container using SSH."""
    client = ctx.obj[API_CLIENT]
    debug = ctx.obj[VERBOSE_DEBUG]
    s = client.get_session()  # type: requests.Session

    assert sftp_command is None or sftp_command in ('sftp', 'gftp', 'filezilla')

    r = s.get(client.get_api_url(3) + "jobs/" + job_id, timeout=GPULAB_CLIENT_TIMEOUT)

    if r.ok:
        def ignore_unknown_fields(field_name: str):
            if debug:
                click.secho('WARNING: ignoring unknown field in reply: {!r}'.format(field_name),
                            err=False, nl=True, fg='red')

        job2_dict = r.json()
        job: Job2 = Job2.from_dict(job2_dict, on_unknown_field_override=ignore_unknown_fields)

        if not job.state or not job.state.resources or not job.state.resources.ssh_username or not job.state.resources.ssh_host:
            raise click.ClickException("No SSH info for job")

        if proxy == 'auto':
            # Try to resolve worker, if it doesn't assume we need the proxy
            # (reason: IDLab Gent hostnames have public IPv6, but not IPv4.)
            try:
                proxy_ip = socket.gethostbyname(job.state.resources.slave_host)
                proxy = 'no'

                # Also hardcode that uantwerpen needs proxy.
                # (reason: uantwerpen nodes are firewalled)
                if job.state.resources.slave_host.endswith('.idlab.uantwerpen.be'):
                    proxy = 'yes'
            # except socket.gaierror as e:
            except OSError as e:
                proxy = 'yes'

        fake_hostname = add_job_ssh_config(
            login_pem_filename=ctx.obj[CERTFILE],
            job=job,
            return_proxy_fake_hostname=proxy == 'yes',
            debug=debug,
        )
        if debug:
            click.secho(f'Configured fake hostname for easy ssh access: '
                        f'fake={fake_hostname!r} -> real={job.state.resources.ssh_host}')

        if show_ansible:
            ssh_command = 'ssh-add {}\n# ansible_ssh_port={} ansible_ssh_host={} ansible_ssh_user={}' \
                .format(ctx.obj[CERTFILE], job.state.resources.ssh_port, fake_hostname, job.state.resources.ssh_username)
            click.echo(ssh_command)
        else:
            if sftp_command == 'gftp':
                command = [
                    'gftp',
                    'ssh2://{}@{}:{}'.format(
                        job.state.resources.ssh_username,
                        fake_hostname,  # instead of: job.state.resources.ssh_host,  (because of IdentityFile, proxy, etc.)
                        job.state.resources.ssh_port)
                ]

                # with Popen(command, stderr=DEVNULL, stdout=DEVNULL, universal_newlines=True) as proc:
                #     # for l in proc.stdout:
                #     #     click.secho(l)
                #     res_code = proc.wait()

                if show:
                    click.echo(command_array_to_str(command))
                else:
                    if debug:
                        click.secho(f'Calling: {command!r}')
                    # Note: This REPLACES the current python process!
                    os.execvp('gftp', command)
            elif sftp_command == 'filezilla':
                if proxy == 'yes':
                    # FileZilla ignores ~/.ssh/config !
                    # and it does not support SSH proxies
                    # So we need to setup the tunnel ourself
                    local_tunnel_port = find_free_ssh_tunnel_port(debug)
                    local_tunnel_hostname = 'localhost'

                    filezilla_command = [
                        'filezilla',
                        'sftp://{}@{}:{}'.format(
                            job.state.resources.ssh_username,
                            local_tunnel_hostname,
                            local_tunnel_port)
                    ]

                    # alternativly, we could use -D to make ssh create a SOCKS proxy, and make filezilla use that.
                    # but filezilla won't let you configure a SOCKS proxy from the command line, so this is less handy.
                    ssh_tunnel_command = [
                        'ssh',
                        '-L', f'{local_tunnel_port}:{job.state.resources.ssh_host}:{job.state.resources.ssh_port}',  # tunnel
                        '-N', # No remote command (shell)
                        f'{job.state.resources.ssh_proxy_username}@{job.state.resources.ssh_proxy_host}',
                    ]

                    if show:
                        click.echo(command_array_to_str(ssh_tunnel_command))
                        click.echo(command_array_to_str(filezilla_command))
                    else:
                        if debug:
                            click.secho(f'Calling: {ssh_tunnel_command!r}')
                            click.secho(f'Calling: {filezilla_command!r}')
                        with Popen(ssh_tunnel_command,
                                   stderr=DEVNULL if not debug else sys.stderr,
                                   stdout=DEVNULL if not debug else sys.stdout) as ssh_proc:
                            if debug:
                                click.echo('SSH tunnel started.')
                            with Popen(filezilla_command,
                                       stderr=DEVNULL if not debug else sys.stderr,
                                       stdout=DEVNULL if not debug else sys.stdout) as filezilla_proc:
                                if debug:
                                    click.echo('Filezilla Started.')
                                filezilla_res_code = filezilla_proc.wait()
                                if debug:
                                    click.echo('Filezilla exited.')
                                    click.echo('Sending SIGINT to SSH.')
                                ssh_proc.send_signal(signal.SIGINT)
                                try:
                                    ssh_res_code = ssh_proc.wait()
                                    if debug:
                                        click.echo('SSH exited.')
                                except TimeoutExpired:
                                    if debug:
                                        click.echo('SSH did not exit on time: KILL')
                                    ssh_proc.kill()
                                    ssh_proc.wait()
                                    if debug:
                                        click.echo('SSH exited.')
                else:
                    # No proxy is simple
                    filezilla_command = [
                        'filezilla',
                        'sftp://{}@{}:{}'.format(
                            job.state.resources.ssh_username,
                            job.state.resources.ssh_host,
                            job.state.resources.ssh_port)
                    ]
                    if show:
                        click.echo(command_array_to_str(filezilla_command))
                    else:
                        if debug:
                            click.secho(f'Calling: {filezilla_command!r}')
                        # Note: This REPLACES the current python process!
                        os.execvp('filezilla', filezilla_command)
            else:
                c = 'ssh' if sftp_command is None else sftp_command
                command_full = [
                    c,
                    '-i', ctx.obj[CERTFILE],
                    '-oPort={}'.format(job.state.resources.ssh_port)]
                command_short = [c, fake_hostname]

                if proxy == 'yes':
                    proxy_username = job.state.resources.ssh_proxy_username
                    proxy_host = job.state.resources.ssh_proxy_host
                    proxy_port = job.state.resources.ssh_proxy_port
                    if not proxy_username:
                        raise click.ClickException("--proxy option cannot be used: no SSH proxy info in job. "
                                                   "(You could try again with --no-proxy but that requires IPv6 or VPN.)")
                    command_full.append('-oProxyCommand=ssh -i {} {} {}@{} -W %h:%p'
                                        .format(sh_quote_arg(ctx.obj[CERTFILE]), _ssh_port_command(proxy_port), proxy_username,
                                                proxy_host))
                command_full.append('{}@{}'.format(job.state.resources.ssh_username, job.state.resources.ssh_host))
                if show:
                    click.echo('Short: '+command_array_to_str(command_short))
                    click.echo('Full:  '+command_array_to_str(command_full))
                else:
                    # Note: This REPLACES the current python process!
                    os.execvp(c, command_full)
    else:
        raise click.ClickException("Could not retrieve info for job '{}': {}".format(job_id, r.text))


@click.command("convert", short_help="Convert a Job to Job2 format")
@click.pass_context
def convert_to_job2(ctx):
    deployment_env = 'staging' if ctx.obj[DEPLOY_ENV_IS_STAGING] else 'production'
    job_json_raw = None
    try:
        job_json_raw = str(click.get_text_stream('stdin').read())
        job_json_dict = json.loads(job_json_raw)
        strip_deployment_env = 'gpulab_version' not in job_json_dict and 'deploymentEnvironment' not in job_json_dict
        job_json_dict['gpulab_version'] = deployment_env
        if is_jsondict_job1(job_json_dict):
            job_json_dict['gpulab_version'] = deployment_env
        if is_jsondict_job2(job_json_dict):
            job_json_dict['deploymentEnvironment'] = deployment_env

        job = any_jsondict_to_job2(job_json_dict)  # support both Job1 and Job2

        assert job.deployment_environment == deployment_env
        assert job.state is None
        job2_dict = strip_null_from_json_dict(job.to_dict(remove_none=True),
                                              strip_empty_dict=True, strip_empty_list=True, process_lists=True)

        if strip_deployment_env and 'deploymentEnvironment' in job2_dict:
            del job2_dict['deploymentEnvironment']

        click.secho('{}'.format(json.dumps(job2_dict, indent=4)), nl=True)
    except:
        if ctx.obj[VERBOSE_DEBUG]:
            click.secho('Could not parse provided Job: {!r}'.format(job_json_raw),
                        err=True, nl=True, fg='red')
            traceback.print_exc()
        raise click.ClickException("Could not parse provided Job (--debug for max details)")



cli.add_command(run)
# cli.add_command(queue)
cli.add_command(rm)
cli.add_command(cancel)
cli.add_command(halt_job)
cli.add_command(hold_job)
cli.add_command(release)
cli.add_command(get_log)
cli.add_command(get_debug)
cli.add_command(get_slave_info)
cli.add_command(get_info)
cli.add_command(wait)
cli.add_command(ssh)
cli.add_command(sftp)
cli.add_command(run_interactive)
cli.add_command(print_bugreport_context)
cli.add_command(convert_to_job2)

localhost_mode_cli.add_command(run_fixed_project)
# localhost_mode_cli.add_command(queue)
localhost_mode_cli.add_command(rm)
localhost_mode_cli.add_command(cancel)
localhost_mode_cli.add_command(halt_job)
localhost_mode_cli.add_command(hold_job)
localhost_mode_cli.add_command(release)
localhost_mode_cli.add_command(get_log)
localhost_mode_cli.add_command(get_debug)
localhost_mode_cli.add_command(get_slave_info)
localhost_mode_cli.add_command(get_info)
localhost_mode_cli.add_command(wait)
localhost_mode_cli.add_command(ssh)
localhost_mode_cli.add_command(sftp)
localhost_mode_cli.add_command(run_interactive)
localhost_mode_cli.add_command(print_bugreport_context)
localhost_mode_cli.add_command(convert_to_job2)


GPULAB_SLAVE_RESERVED_ENVVARS = [
    'GPULAB_USERNAME',
    'GPULAB_USER_URN',
    'GPULAB_USERURN_NAME',
    'GPULAB_USERURN_AUTH',
    'GPULAB_USER_MINI_ID',
    'GPULAB_PROJECT',
    'GPULAB_VERSION',
    'GPULAB_DEPLOYMENT_ENVIRONMENT',
    'GPULAB_JOB_ID',
    'GPULAB_CLUSTER_ID',
    'GPULAB_SLAVE_HOSTNAME',
    'GPULAB_SLAVE_DNSNAME',
    'GPULAB_SLAVE_INSTANCE_ID',
    'GPULAB_SLAVE_PID',
    'GPULAB_WORKER_ID',
    'GPULAB_MEM_RESERVED',
    'GPULAB_GPUS_RESERVED',
    'GPULAB_CPUS_RESERVED',
]


def main():
    if 'https_proxy' in os.environ and os.environ.get('https_proxy'):
        print('Error: You have the "https_proxy" environment variable set (to "{}"). \n'
              '       HTTPS proxies prevent client SSL authentication (man-in-the-middle), which GPULab needs. \n'
              '       GPULab cannot work with a HTTPS proxy.'.format(os.environ.get('https_proxy')),
              file=sys.stderr)
        exit(1)
    try:
        try:
            for ignored_envvar in GPULAB_SLAVE_RESERVED_ENVVARS:
                os.environ.pop(ignored_envvar, None)
                #removed = os.environ.pop(ignored_envvar, None)
                # if removed:
                #     print('Ignoring envvar {}'.format(ignored_envvar))
        except:
            print('Error ignoring envvars. Will ignore.\n{}'.format(traceback.format_exc()))

        if GPULAB_LOCALHOST_MODE in os.environ:
            localhost_mode_cli(obj={}, auto_envvar_prefix="GPULAB")
        else:
            cli(obj={}, auto_envvar_prefix="GPULAB")
    except SSLError as e:
        s = str(e).lower()
        if 'certificate' in s and 'expired' in s:
            print('ERROR: The certificate in your login PEM has expired.')
        else:
            raise e


modify_usage_error()

if __name__ == "__main__":
    main()
