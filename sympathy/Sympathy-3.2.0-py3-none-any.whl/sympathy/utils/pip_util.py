# This file is part of Sympathy for Data.
# Copyright (c) 2017, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
"""
Module/script for extracting license information from pip and updating
third party licenses for Sympathy/Package/Windows/License.txt.in.
"""
import sys
import os
import re
import io
import subprocess
import argparse


license_info = {
    'alabaster': 'BSD',
    'backports.functools-lru-cache': 'MIT',
    'entrypoints': 'MIT',
    'jsonschema': 'MIT',
    'keyring': 'MIT',
    'pandocfilters': 'BSD',
    'testpath': 'BSD',
    'h5py': 'BSD',
    'lxml': 'BSD',
    'pbr': 'APACHE',
    'prompt-toolkit': 'BSD',
    'svgutils': 'MIT',
    'kiwisolver': 'BSD',
    'backports-abc': 'PSF'}


_freeze = None


def install_args(package, *args, executable=sys.executable, constraints=None):
    res = [executable, '-m', 'pip', 'install', *args, package]
    if constraints:
        res.extend(['-c', constraints])
    return res


def uninstall_args(package, *args, executable=sys.executable):
    return [executable, '-m', 'pip', 'uninstall', '--yes', *args, package]


def freeze_args(executable=sys.executable):
    return [executable, '-m', 'pip', 'freeze']


def freeze():
    global _freeze
    if _freeze is None:
        output = subprocess.check_output(
            [sys.executable, '-m', 'pip', 'freeze'], universal_newlines=True)
        _freeze = freeze_from_str(output)
    return _freeze


def freeze_from_str(output):
    pkgs = dict(
        (k.strip().split('\n')[-1], v.strip())
        for k, v in re.findall('^([^=<>]*)[ \t]*[=<>]*[ \t]*(.*)$', output,
                               re.MULTILINE) if k.strip())
    # Remove current development versions.
    return {k: v for k, v in pkgs.items() if not k.startswith('-e ')}


def show(pkg):
    output = subprocess.check_output(
        [sys.executable, '-m', 'pip', 'show', pkg], universal_newlines=True)
    return _show_str(output)


def requirements(filename):
    if os.path.exists(filename):
        with io.open(filename) as f:
            data = f.read()
            return freeze_from_str(data)
    else:
        try:
            return dict.fromkeys(re.findall('[ \t]*([^ \t,]+),?',
                                            show('Sympathy')['Requires']))
        except Exception:
            return {}


def _show_str(output, ignore_missing=False):
    res = dict(
        (k.strip(), v.strip())
        for k, v in re.findall('^([^:]*): *(.*)$', output, re.MULTILINE))
    lice = res.get('License')
    if lice is None or lice == 'UNKNOWN':
        name = res['Name']
        try:
            res['License'] = license_info[name]
        except KeyError:
            if ignore_missing:
                pass
            else:
                raise KeyError(
                    'Missing license for included package: "{name}" '
                    'please add that information to license_info'.format(
                        name=name))
    return res


def showall(names=None, ignore_missing=False):
    if not names:
        names = list(freeze().keys())

    output = subprocess.check_output(
        [sys.executable, '-m', 'pip', 'show'] + names, universal_newlines=True)
    pkgs = re.split('^---.*$[\r\n]+', output, flags=re.MULTILINE)
    return sorted([_show_str(pkg, ignore_missing) for pkg in pkgs],
                  key=lambda x: x['Name'])


def format_third_party(pkg):
    return '{name} ({home}) {lice}'.format(
        name=pkg['Name'],
        home=pkg['Home-page'],
        lice=pkg['License'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-I', '--input', action='store', default=None,
                        help='Input file used as template for expansion')
    parser.add_argument('-O', '--output', action='store', default=None,
                        help='Output file used for storing result')
    parsed = parser.parse_args()
    pkgs = showall()
    template = '{PYTHON_LICENSES}\n'
    indent = ''

    if parsed.input:
        with io.open(parsed.input) as f:
            template = f.read()

    match = re.search('^(.*){PYTHON_LICENSES}.*$', template, re.MULTILINE)
    if match:
        indent = match.group(1)
    text = ('\n' + indent).join(format_third_party(pkg) for pkg in pkgs)
    res = template.format(PYTHON_LICENSES=text)

    if parsed.output:
        with io.open(parsed.output, 'w') as f:
            f.write(res)
    else:
        print(res)
