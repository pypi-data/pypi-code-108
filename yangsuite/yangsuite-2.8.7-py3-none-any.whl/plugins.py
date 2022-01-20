# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.

from django.apps import apps
import django.utils.autoreload
from django.core.management import execute_from_command_line
import json
import os
import importlib
from packaging.version import Version, LegacyVersion, InvalidVersion
from pkg_resources import iter_entry_points, VersionConflict
import re
import subprocess
import sys
from github import Github
import requests

from yangsuite.logs import get_logger
from yangsuite.apps import FAILED_APPS, CANARY_FILE
from ysdevices.devprofile import YSDeviceProfile

log = get_logger(__name__)


def inform(message):
    """Pretty-print a message to the user."""
    print('*' * 70)
    print(message)
    print('*' * 70)


def get_plugin_versions():
    """Get the installed YANG Suite plugins and their versions.

    Returns:
      list: of dicts with keys 'package_name', 'installed_version',
        'module_name', 'verbose_name', 'error_message'
    """
    plugins = []
    # For each installed plugin, we have a pkg_resources entry_point which
    # lets us look up a Django YSAppConfig.
    #
    # entry_point:                       pkg_resources.EntryPoint
    #   name = 'yangtree'
    #   module_name = 'ysyangtree.apps'
    #   attrs = ('YSYangTreeConfig', )
    #   extras = ()
    #   dist:                            pkg_resources.DistInfoDistribution
    #     project_name = 'yangsuite-yangtree'
    #     version = '0.4.1'
    #     key = 'yangsuite-yangtree'     (project_name.lower())
    #
    # app_config:                        YSAppConfig
    #   name: 'ysyangtree'               full python module path
    #   label: 'ysyangtree'              last part of name, overridable
    #   verbose_name: 'YANG Tree app'    defaults to label.upper() if unset
    #
    # TODO: we should also be able to use the 'pkginfo' module to read
    # additional package info, such as Summary and Description,
    # but this appears non-trivial.
    for entry_point in iter_entry_points(group='yangsuite.apps', name=None):
        dist = entry_point.dist
        plugin = {
            'package_name': dist.project_name,
            'installed_version': dist.version,
            'module_name': '(unknown)',
            'verbose_name': '(unknown)',
            'error_message': ''
        }
        if dist.project_name in FAILED_APPS:
            plugin['error_message'] = FAILED_APPS[dist.project_name]
        else:
            try:
                ac_class = entry_point.load()
                app_config = apps.get_app_config(ac_class.name)
                plugin['module_name'] = app_config.name
                plugin['verbose_name'] = app_config.verbose_name
            except VersionConflict as exc:
                plugin['error_message'] = exc.report()
            except Exception as exc:
                plugin['error_message'] = str(exc)
        plugins.append(plugin)
    plugins = sorted(plugins, key=lambda x: x['package_name'])
    log.info("Installed plugins: %s", [x['package_name'] for x in plugins])

    return plugins


def call_pip(args):
    """Invoke pip with the given list of
     args and return output as a string."""
    try:
        output = subprocess.check_output(['pip'] + args, stderr=None)
        # On python 3, depending on user locale, subprocess.check_output
        # may return either a str or bytes. Handle it either way
        if not isinstance(output, str):
            output = output.decode()
        return output
    except subprocess.CalledProcessError as exc:
        # May occur if pypi server is unreachable, etc.
        inform("pypi server is unreachable")
        log.error('"pip %s" failed with exit code %d',
                  " ".join(args), exc.returncode)
        log.debug("pip output:\n%s", exc.output)
        return ''


def tag_sort(x):
    xs = x.split('.')
    if xs and len(xs) > 1:
        if xs[0].replace('v', '') == '0':
            return 0
        return int(xs[1])
    return int(1)


EXCLUDED_APPS = [
    'yangsuite-app-template',
    'yangsuite-mapper',
    'yangsuite-impact',
    'yangsuite-ydk',
    'yangsuite-IBCR',
    'yangsuite-doc-builder',
    'yangsuite-mapper-xrcodegen',
    'yangsuite-mapper-erlang',
    'yangsuite-pipeline',
]


def check_public_versions():
    """Check pypi.org version numbers for YANG Suite."""
    plugins = []
    sess = requests.Session()
    sess.headers.update({'Accept': 'application/json'})

    for app in iter_entry_points(group='yangsuite.apps', name=None):
        resp = sess.get(
            "https://pypi.org/pypi/{0}/json".format(app.dist.project_name),
            verify=False
        )
        if resp.ok:
            data = resp.json()
            releases = data.get('releases', {}).keys()
            # Don't report pre-releases.
            filtered_rel = [r for r in releases if '.post' not in r]
            # Don't report yanked releases.
            for rel in filtered_rel:
                for blob in data['releases'][rel]:
                    if blob['yanked'] is True:
                        filtered_rel.remove(rel)
                        break
            releases = filtered_rel

            if releases:
                revs = sorted(
                    releases,
                    key=(lambda x: [
                         int(v) if v.isdigit() else 0 for v in
                         x.split('.')]),
                    reverse=True
                )
                plugins.append({
                    'package_name': app.dist.project_name,
                    'description': app.dist.project_name,
                    'latest_version': revs[0]
                })
    return plugins


def check_for_plugin_updates():
    """Check upstream repository for available YANG Suite plugins.

    Since this involves network operations it can be somewhat slow, which
    is why this is a separate function from :func:`get_plugin_versions`.

    Returns:
      list: of dicts with keys 'package_name', 'latest_version', 'description',
      or an empty list in case of various failures.
    """
    plugins = []
    try:
        smod = importlib.import_module(os.getenv(
            'DJANGO_SETTINGS_MODULE',
            'yangsuite.settings.production')
        )
    except ImportError:
        log.error("Unable to find github settings:\n{0}\n{1}\n{2}".format(
            'GITHUB_BASE_URL', 'GITHUB_TOKEN', 'GITHUB_ORG'))
        return plugins
    if not hasattr(smod, 'GITHUB_BASE_URL'):
        return check_public_versions()
    try:
        ghub = Github(
            base_url=smod.GITHUB_BASE_URL,
            login_or_token=smod.GITHUB_TOKEN
        )
        org = ghub.get_organization(smod.GITHUB_ORG)
        for repo in org.get_repos():
            if repo.name.startswith('yangsuite'):
                if repo.name in EXCLUDED_APPS:
                    continue
                tags = [((t.name).replace(
                                  'v', '')).strip() for t in repo.get_tags()]
                tag_names = sorted(tags,
                                   key=(lambda x: [
                                        int(v) if v.isdigit() else 0 for v in
                                        x.split('.')]),
                                   reverse=True)
                if len(tag_names) > 0:
                    tag_name = tag_names[0].replace('v', '')
                else:
                    tag_name = 'unknown'
                plugins.append({
                    'package_name': repo.name,
                    'description': repo.description,
                    'latest_version': tag_name
                })
        plugins = sorted(plugins, key=lambda x: x['package_name'])
        log.info(
            "All available plugins: %s", [x['package_name'] for x in plugins])
    except Exception as e:
        log.error("Unable to collect repository infomation {0}".str(e))

    return plugins


def update_ys_database():
    """Migrate changes to database if needed for plugin updates."""
    try:
        for entry_point in iter_entry_points(
                group='yangsuite.apps', name=None):
            try:
                app = entry_point.load()
                execute_from_command_line(
                    ['manage', 'makemigrations', app.name, '--no-color']
                )
            except Exception:
                continue
        execute_from_command_line(['manage', 'migrate', '--no-color'])
    except Exception as exc:
        log.error('Database migrations failed: {0}'.format(str(exc)))


def update_plugins(plugins):
    """Update the given plugin to the latest release or pre-release version.

    Args:
      plugins (list): of dictionaries with keys 'plugin', 'version'

    Returns:
      dict: Package names as keys, each value is one of "updated",
      "unchanged", or "failed"
    """
    args = ['install',
            '--no-cache',
            '--upgrade',
            '--extra-index-url',
            'https://engci-maven.cisco.com/artifactory/'
            'api/pypi/yang-suite-dev-pypi/simple']
    result = {}
    any_updated = False
    for plugin_info in plugins:
        plugin = plugin_info.get('plugin')
        version = plugin_info.get('version')
        if version:
            args.append("{0}=={1}".format(plugin, version))
        else:
            args.append(plugin)

    # Prevent Django from detecting file changes midway through the plugin
    # installation sequence and auto-reloading the development server before
    # we're done installing.
    # Note that this is using undocumented Django APIs, and *will* break when
    # we migrate to Django 2.1 due to major refactoring of these APIs:
    # https://github.com/django/django/pull/8819
    cached_filenames = django.utils.autoreload._cached_filenames
    django.utils.autoreload._cached_filenames = []
    try:
        output = call_pip(args)
        for plugin_info in plugins:
            plugin = plugin_info.get('plugin')
            if not output:
                result[plugin] = "failed"
            elif re.search('Successfully installed .*{0}'.format(plugin),
                           output):
                result[plugin] = "updated"
                any_updated = True
            else:
                result[plugin] = "unchanged"
    finally:
        # Re-enable autoreloading, if applicable
        django.utils.autoreload._cached_filenames = cached_filenames

    if any_updated:
        # Update the canary file.
        # If we're running in development mode without '--noreload', this will
        # cause the Django server to self-restart, picking up the new code.
        os.utime(CANARY_FILE)
        update_ys_database()

    return result


def _version_list_from_pip_command(extra_args=None):
    """Calls 'pip list --format=json [extra_args]' and parses the output.

    Helper for :func:`python_report`.

    The above command gives us a list of dicts, of form
    ``[{'name': 'foo', 'version': "0.1.2"}, ..]`` or
    ``[{'name': 'bar', 'version': "0.1.2", 'latest_version': "1.2.0"}, ...]``

    Args:
      extra_args (list): List of additional args to pass to the base
        'pip list --format=json' command

    Returns:
      dict: {name: latest_version, name: latest_version, ...},
        or None in case of error.
    """
    args = ['list', '--format=json']
    if extra_args:
        args += extra_args
    try:
        # Check if there's a newer release version than what we have
        output = call_pip(args)
        if not output:
            return None

        # Even though we redirect stderr above, pip has a bad habit of
        # printing error messages to stderr which result in malformed "JSON",
        # such as:
        # Could not fetch URL https://<...> There was a problem...
        #
        # As a rough attempt at a workaround, we'll drop lines until we get to
        # a line that looks like it could be JSON.
        pkgs_lines = []
        for line in output.splitlines():
            if not line.startswith("[{"):
                continue
            pkgs_lines.append(line)
        pkgs_json = "\n".join(pkgs_lines)
        pkgs_list = json.loads(pkgs_json)
    except ValueError:
        log.error("Unable to decode message as JSON")
        log.debug("pip output:\n%s", pkgs_json)
        return None

    # The above command gives us a list of dicts, of form
    # [{'name': 'foo', 'version': "0.1.2"},]
    # Let's change it around to something a bit more useful for our needs.
    result = {}
    for entry in pkgs_list:
        # Get 'latest_version' if available, else 'version'
        vers = entry.get('latest_version', entry['version'])
        try:
            # PEP-440-compliant version
            version = Version(vers)
        except InvalidVersion:
            # Not PEP-440-compliant, treat as legacy version string
            version = LegacyVersion(vers)
        result[entry['name']] = version

    return result


def python_report():
    """Report on the overall Python system status.

    Returns:
      dict: {python: {version: "3.6.5 ..."}, modules: [...]}
    """
    installed_pkgs = _version_list_from_pip_command()
    for name in installed_pkgs.keys():
        installed_pkgs[name] = str(installed_pkgs[name])
    return {
        "python": {"version": str(sys.version)},
        "modules": installed_pkgs,
    }


def _verify_callback(data):
    if data:
        ln = [ln for ln in data.splitlines()
              if ln.strip().startswith('dna-advantage')]
        if ln:
            line = ln[0].split()
            if line[len(line) - 1] == 'EXPIRED':
                return False
            else:
                return True
    return False


def _check_available(dev, cmd='show license summary',
                     callback=_verify_callback):
    """Check availability of a device."""
    if isinstance(dev, YSDeviceProfile):
        dev_profile = dev
    else:
        dev_profile = YSDeviceProfile.get(dev)
    try:
        dev_profile.ssh.connect()
        return callback(dev_profile.ssh.send_exec(cmd))
    except Exception:
        print('Check class failed: {0}'.format((str(Exception))))
        return False
