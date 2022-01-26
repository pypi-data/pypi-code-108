from builtins import str
from datetime import datetime, timedelta
from dateutil.parser import isoparse
from dateutil.tz import tzlocal, tzutc
from functools import wraps
import importlib
import math
import pkg_resources
from packaging import version
import os
import re
import shutil
import subprocess
import csv

import click
import tabulate

from spell import deployment_constants
from spell.cli.constants import VERSION_REQUIREMENTS
from spell.cli.log import logger
from spell.cli.exceptions import api_client_exception_handler, ExitException
from spell.shared.projects import NotFoundException, get_project_by_name

ASCII_SPINNER = {
    "interval": 100,
    "frames": ["|", "/", "-", "\\"],
}
STAR_SPINNER = {
    "interval": 200,
    "frames": ["⭐", "🌟"],
}


def on_wsl():
    """Windows subsystem for linux"""
    if not os.path.isfile("/proc/version"):
        return False
    with open("/proc/version") as f:
        contents = f.read()
    return "Microsoft" in contents


def eksctl_version_check():
    current_version = subprocess.check_output(["eksctl", "version"]).decode("utf-8").strip()
    if version.parse(current_version) < version.parse(VERSION_REQUIREMENTS["eksctl"]):
        raise ExitException(
            "Minimum supported version of eksctl is {}. Found {}".format(
                VERSION_REQUIREMENTS["eksctl"], current_version
            )
        )


# NOTE(waldo): The kubectl client version should be w/in one minor version of the k8s api
# (this is a k8s reccomendation, not Spell's). This isn't as big of a deal as making sure
# the api version is within our supported version windows, but still worth checking.
def kubectl_version_check():
    version_str = subprocess.check_output(["kubectl", "version", "--short", "--client"], text=True)
    current_version = re.search(r"Client Version: v([0-9]*\.[0-9]*\.[0-9]*)", version_str).group(1)
    if not current_version:
        raise ExitException("Unable to determine kubectl version")
    if version.parse(current_version) < version.parse(VERSION_REQUIREMENTS["kubectl"]):
        raise ExitException(
            "Minimum supported version of kubectl is {}. Found {}".format(
                VERSION_REQUIREMENTS["kubectl"], current_version
            )
        )


VERSION_CHECKS = {"eksctl": eksctl_version_check, "kubectl": kubectl_version_check}


SIZE_SUFFIXES = ["B", "K", "M", "G", "T", "P"]


AWS_ARN_REGEX = re.compile("arn:aws:iam::(\d+):(user|role)/(.+)")  # noqa


def acct_id_from_role_arn(role_arn):
    """
    >>> acct_id_from_role_arn("arn:aws:iam::002219003547:user/api_machine_local")
    ('366388869580', 'api_machine_local')
    >>> acct_id_from_role_arn("arn:aws:iam::366388869580:role/SpellMinikubeRole")
    ('366388869580', 'SpellMinikubeRole')
    """
    match = AWS_ARN_REGEX.match(role_arn)
    if not match:
        raise ValueError(f"Role ARN {role_arn} is invalid")
    return match.group(1), match.group(3)


def require_install(*pkgs):
    """
    Decorator that asserts that the non-PyPI packages passed in are installed
    (e.g. eksctl, gcloud)
    """

    def require_install_wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            for pkg in pkgs:
                if not is_installed(pkg):
                    raise ExitException(
                        "Package `{}` is not installed. Please " "install it and rerun this command.".format(pkg)
                    )
                if pkg in VERSION_CHECKS:
                    VERSION_CHECKS[pkg]()
            f(*args, **kwargs)

        return wrapped

    return require_install_wrapper


def require_import(*pkgs, pkg_extras=""):
    """
    Decorator that asserts that the packages passed in are importable. The
    optional pkg_extras arg allows for customization of the extras suffix on
    the spell package in the pip install nag.
    """

    def require_import_wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            for pkg in pkgs:
                if "find_spec" in dir(importlib.util):
                    search_func = importlib.util.find_spec
                else:
                    search_func = importlib.find_loader
                if search_func(pkg) is None:
                    extras_suffix = "[{}]".format(pkg_extras) if pkg_extras else ""
                    raise ExitException(
                        "Failed to import package {}. Please run `pip install "
                        "--upgrade 'spell{}'` and rerun this command".format(pkg, extras_suffix)
                    )
            f(*args, **kwargs)

        return wrapped

    return require_import_wrapper


def require_pip(*pkgs, pkg_extras=""):
    """
    Decorator that asserts that the PyPI packages passed in are installed. The
    optional pkg_extras arg allows for customization of the extras suffix on
    the spell package in the pip install nag.
    """

    def require_pip_wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            for pkg in pkgs:
                req = pkg_resources.Requirement(pkg)
                extras_suffix = "[{}]".format(pkg_extras) if pkg_extras else ""
                try:
                    pkg_version = pkg_resources.get_distribution(req.name).version
                except pkg_resources.DistributionNotFound:
                    raise ExitException(
                        "Package {} not installed. Please run `pip install --upgrade "
                        "'spell{}'` and rerun this command.".format(req.name, extras_suffix)
                    )
                if not req.specifier.contains(pkg_version):
                    raise ExitException(
                        "Could not find compatible version of package {} (requires {}, "
                        "found {}). Please run `pip install --upgrade 'spell{}'` and rerun this "
                        "command.".format(req.name, str(req.specifier), pkg_version, extras_suffix)
                    )
            f(*args, **kwargs)

        return wrapped

    return require_pip_wrapper


def is_installed(cmd):
    return bool(shutil.which(cmd))


def with_emoji(emoji, msg, utf8):
    if utf8:
        return "{} {}".format(emoji, msg)
    return msg


def format_run_status(status):
    return (status.title()).replace("_", " ")


def ellipses(utf8=True):
    return "…" if utf8 else "..."


def right_arrow(utf8=True):
    return "→" if utf8 else "->"


def get_star_spinner_frames(is_utf8_enabled):
    return STAR_SPINNER if is_utf8_enabled else ASCII_SPINNER


def tabulate_rows(rows, headers=None, columns=None, raw=False):
    def extract_attrs(row_objs):
        for row_obj in row_objs:
            yield [getattr(row_obj, col) for col in columns]

    if headers is None:
        headers = ()

    if columns is not None:
        rows = extract_attrs(rows)

    if raw:
        echo_raw(rows)
    else:
        click.echo(tabulate.tabulate(rows, headers=headers, tablefmt="plain", numalign="left"))


def _default_dict_formatter(key, value):
    return f"{key}={value}"


def format_multiline_table_output(label, entries, formatter=None):
    if isinstance(entries, dict):
        formatter = formatter or _default_dict_formatter
        entries = list(entries.items())
        lines = [(label, formatter(entries[0][0], entries[0][1]))]
        for key, value in entries[1:]:
            lines.append(("\t", formatter(key, value)))
        return lines
    else:
        formatter = formatter or str
        lines = [(label, formatter(entries[0]))]
        for entry in entries[1:]:
            lines.append(("\t", formatter(entry)))
        return lines


def format_multiline_text_to_table(label, text):
    text_lines = text.split("\n")
    lines = [(label, text_lines[0])]
    for text_line in text_lines[1:]:
        if text_line.strip() == "":
            continue
        lines.append(("\t", text_line))
    return lines


# convert_to_local_time is an alternative to prettify_time that returns the input
# timestamp string in a non-relative way, similar to the way that `ls -al` prints
# timestamps in the local timezone of the user
def convert_to_local_time(t, include_seconds=True):
    if isinstance(t, datetime):
        dt = t.replace(tzinfo=tzutc()).astimezone(tzlocal())
    else:
        dt = isoparse(t).astimezone(tzlocal())
    if datetime.now(tzlocal()) - dt < timedelta(days=364):
        format_str = "%b %d %H:%M:%S" if include_seconds else "%b %d %H:%M"
        return dt.strftime(format_str)
    else:
        return dt.strftime("%b %d %Y")


# prettify_time returns a nice human readable representation of a time delta from 'time' to now
# if the default elapsed=False is specified, the return value describes a historical time (e.g., " 2 days ago")
# if elapsed=True, the return value describes an elapsed time (e.g, "2 days")
def prettify_time(time, elapsed=False):
    """prettify a datetime object"""
    now = datetime.now(tzutc())
    if not elapsed and (now - time).days > 14:
        # date for differences of over 2 weeks
        return "{:%Y-%m-%d}".format(time)

    time_str = prettify_timespan(time, now)
    if elapsed:
        return time_str
    return "{} ago".format(time_str)


# prettify_timespan returns a nice human readable representation of a time delta from 'start' to 'end'
def prettify_timespan(start, end):
    """prettify a timedelta object"""
    delta = end - start
    if delta.days > 1:
        # days ago for differences of over a day
        return "{} days".format(delta.days)
    if delta.days > 0:
        return "1 day"
    if delta.seconds > 7200:
        # hours ago for differences of over an hour
        return "{} hours".format(delta.seconds // 3600)
    if delta.seconds > 3600:
        return "1 hour"
    if delta.seconds > 120:
        # minutes ago for differences of over a minute
        return "{} minutes".format(delta.seconds // 60)
    if delta.seconds > 60:
        return "1 minute"
    return "{} seconds".format(delta.seconds)


def prettify_size(size):
    """prettify an int representing file size in bytes"""
    if size < 0:
        raise ValueError("Negative size value {}".format(size))
    if size == 0:
        return "0B"

    order = int(math.log(size, 2) / 10)
    if order == 0:
        return "{}B".format(size)
    if order >= len(SIZE_SUFFIXES):
        raise ValueError("Unparsable size value {}".format(size))
    size_suffix = SIZE_SUFFIXES[order]

    scaled = size / 2 ** (10.0 * order)
    if scaled >= 10:
        return "{}{}".format(int(scaled), size_suffix)
    return "{:.1f}{}".format(scaled, size_suffix)


def truncate_string(raw, width, fixed_width=False, utf8=True):
    truncated = False

    s = str(raw)
    split = s.split("\n")
    if len(split) > 1:
        s = split[0]
        truncated = True
    dots = ellipses(utf8)
    if len(s) > width:
        s = s[: width - len(dots)]
        truncated = True
    if truncated:
        s = s + dots
    if fixed_width:
        s = s.ljust(width)
    return s


def fetch_project(client, project_name):
    with api_client_exception_handler():
        all_projects = client.list_projects()
    proj = get_project_by_name(all_projects, project_name)
    return proj


def get_or_create_project(client, project_name):
    with api_client_exception_handler():
        all_projects = client.list_projects()
    try:
        proj = get_project_by_name(all_projects, project_name)
    except NotFoundException:
        if click.confirm(
            f"A project named '{project_name}' could not be found. " "Would you like to create a new one?"
        ):
            with api_client_exception_handler():
                proj = client.create_project({"name": project_name})
        else:
            raise

    return proj


def echo_raw(data):
    """print rows of data (iterable of iterables) to stdout in CSV form"""
    ts = click.get_text_stream("stdout", encoding="utf-8")
    ts.writelines([",".join(row) + "\n" for row in data])


def remove_path(path, prompt=False):
    """remove file or directory at path"""
    if os.path.isdir(path):
        if prompt:
            click.confirm(
                "Spell will now delete the existing directory {}. Do you wish to continue?".format(path),
                abort=True,
            )
        logger.info("removing existing directory: {}".format(path))
        shutil.rmtree(path)
    if os.path.isfile(path):
        if prompt:
            click.confirm(
                "Spell will now delete the existing file {}. Do you wish to continue?".format(path),
                abort=True,
            )
        logger.info("removing existing file: {}".format(path))
        os.remove(path)


def add_known_host(hostname, port=22):
    """If hostname is not in ~/.ssh/known_hosts this function uses ssh-keyscan
    to add it. This allows us to avoid showing the user a yes/no would you like
    to continue connecting prompt, and still provides the safety of strict host
    checking
    """
    ssh_dir = os.path.expanduser("~/.ssh")
    os.makedirs(ssh_dir, exist_ok=True)
    with open(os.path.join(ssh_dir, "known_hosts"), "ab+") as f:
        full_hostname = "[{}]:{}".format(hostname, port) if port != 22 else hostname
        try:
            if subprocess.check_output(["ssh-keygen", "-F", full_hostname]):
                return
        except subprocess.CalledProcessError:
            # failure to find returns error code 1
            pass
        # Write stderr to devnull to avoid printing extra information returned
        # by ssh-keyscan, i.e. '# git.spell.ml:22 SSH...'
        with open(os.devnull, "w") as devnull:
            command = ["ssh-keyscan", "-t", "ecdsa"]
            if port != 22:
                command = command + ["-p", str(port)]
            command = command + [hostname]
            key = subprocess.check_output(command, stderr=devnull)
            f.write(key)


def try_add_known_host(ctx):
    """Attempt to add GitLab git cache host to known_hosts, ignore failures"""
    # NOTE(aleksey): when run within a run in dev, add dev host, in all other cases add prod host
    if os.environ.get("SPELL_RUN", False) and ctx.obj["client_args"]["base_url"].startswith("https://dev-api"):
        gitlab_url, gitlab_port = "dev-git.spell.ml", 22
    else:
        gitlab_url, gitlab_port = deployment_constants.gitlab_url, deployment_constants.gitlab_port
    try:
        add_known_host(gitlab_url, port=gitlab_port)
    except Exception:
        pass


def cli_ssh_key_path(config_handler):
    return os.path.join(config_handler.spell_dir, "spell.pem")


def cli_ssh_config_path(config_handler):
    return os.path.join(config_handler.spell_dir, "ssh_config")


def write_ssh_config_file(config_handler):
    with open(cli_ssh_config_path(config_handler), "w") as f:
        f.write("# empty spell ssh config")


def write_rows(dest, values, header=None):
    with open(dest, "w") as f:
        write = csv.writer(f)
        if header is not None:
            write.writerow(header)
        write.writerows(values)


class LazyChoice(click.Choice):
    """A type similar to click.Choice that loads its choices lazily. It is initialized with a function that
    returns an iterable (probably a generator) for the possible choices. It can optionally be case-sensitive
    or insensitive, and it defaults to case-insensitive
    """

    name = "lazy_choice"

    def __init__(self, choice_fn, case_sensitive=False):
        self.choice_fn = choice_fn
        super(LazyChoice, self).__init__(self.choice_fn(), case_sensitive=case_sensitive)

    def __getattribute__(self, name):
        # Override any calls to "choices" with the generator
        if name == "choices":
            return self.choice_fn()
        return super(LazyChoice, self).__getattribute__(name)

    def convert(self, value, param, ctx):
        if value is None:
            return None
        for choice in self.choices:
            if self.case_sensitive and value == choice or not self.case_sensitive and value.lower() == choice.lower():
                return choice
        self.fail(
            "invalid choice: {}. (choose from {})".format(value, ", ".join(self.choices)),
            param,
            ctx,
        )
