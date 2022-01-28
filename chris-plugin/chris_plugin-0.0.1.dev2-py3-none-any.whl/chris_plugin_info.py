import argparse
import importlib
import sys
from importlib.metadata import Distribution, distribution, packages_distributions
from typing import Iterable, Optional
import json

from chris_plugin._registration import get_registered
from chris_plugin.parameters import serialize
import chris_plugin.links as links

import logging
logging.basicConfig()


parser = argparse.ArgumentParser(description='Get ChRIS plugin description')
parser.add_argument('module_name', nargs='?',
                    help='module name of Python ChRIS plugin. '
                         'If unspecified, tries to guess the module name by '
                         'querying for which installed pip package depends on '
                         f'"{__package__}"')


class GuessException(Exception):
    """
    `chris_module_info` was unable to automatically detect any installed *ChRIS* plugins.
    """
    pass


def get_all_distributions() -> Iterable[Distribution]:
    return map(distribution, get_all_distribution_names())


def get_all_distribution_names() -> Iterable[str]:
    return (
        dist for dists_per_package in packages_distributions().values()
        for dist in dists_per_package
    )


def get_dependents(dependency=__package__) -> Iterable[Distribution]:
    return filter(lambda d: is_dependent(dependency, d), get_all_distributions())


def is_dependent(package_name: str, _d: Distribution) -> bool:
    if _d.requires is None:
        return False
    return package_name in _d.requires


def guess_plugin_distribution() -> Distribution:
    dependents = set(get_dependents())
    if len(dependents) < 1:
        raise GuessException(
            'Could not find ChRIS plugin. Make sure you have "pip installed" '
            'your ChRIS plugin as a python package.'
        )
    if len(dependents) > 1:
        raise GuessException('Found multiple ChRIS plugin distributions, '
                             'please specify one: ' +
                             str([d.name for d in dependents]))
    dist, = dependents
    return dist


def get_distribution_of(module_name: str) -> Distribution:
    dot = module_name.find('.')
    if dot != -1:
        module_name = module_name[:dot + 1]
    # idk why it's a list, i don't want to deal with it
    dist_name = packages_distributions().get(module_name)[0]
    return distribution(dist_name)


def entrypoint_modules(_d: Distribution) -> list[str]:
    return [
        ep.value[:ep.value.index(':')]
        for ep in _d.entry_points
        if ep.group == 'console_scripts'
    ]


def entrypoint_of(d: Distribution) -> str:
    eps = [ep for ep in d.entry_points if ep.group == 'console_scripts']
    if not eps:
        print(f'"{d.name}" does not have any console_scripts defined in its setup.py.\n'
              f'For help, see {links.setup_py_help}', file=sys.stderr)
        sys.exit(1)
    if len(eps) > 1:
        # multiple console_scripts found, but maybe they're just the same thing
        if len(frozenset(eps)) > 1:
            print(f'Multiple console_scripts found for "{d.name}": {str(eps)}', file=sys.stderr)
    return eps[0].name


def get_or_guess(module_name: Optional[str]) -> tuple[list[str], Distribution]:
    if module_name:
        return [module_name], get_distribution_of(module_name)
    try:
        dist = guess_plugin_distribution()
    except GuessException as e:
        print('\n'.join(e.args), file=sys.stderr)
        sys.exit(1)
    mods = entrypoint_modules(dist)
    if not mods:
        print(f'No entrypoint modules found for {dist.name}. '
              "In your ChRIS plugin's setup.py, please specify "
              "entry_points={'console_scripts': [...]}",
              file=sys.stderr)
        sys.exit(1)
    return mods, dist


def main():
    args = parser.parse_args()
    mods, dist = get_or_guess(args.module_name)
    for module_name in mods:
        importlib.import_module(module_name)
    details = get_registered()
    setup = dist.metadata
    info = {
        'type': details.type,
        'parameters': serialize(details.parser),
        'icon': details.icon,
        'authors': f'{setup["Author"]} <{setup["Author-email"]}>',
        'title': details.title if details.title else setup['Name'],
        'category': details.category,
        'description': setup['Summary'],
        'documentation': setup['Home-page'],
        'license': setup['License'],
        'version': setup['Version'],
        'selfpath': '',
        'selfexec': '',
        'execshell': entrypoint_of(dist),
        'min_number_of_workers': details.min_number_of_workers,
        'max_number_of_workers': details.max_number_of_workers,
        'min_memory_limit': details.min_memory_limit,
        'max_memory_limit': details.max_memory_limit,
        'min_cpu_limit': details.min_cpu_limit,
        'max_cpu_limit': details.max_cpu_limit,
        'min_gpu_limit': details.min_gpu_limit,
        'max_gpu_limit': details.max_gpu_limit
    }
    print(json.dumps(info, indent=2))


if __name__ == '__main__':
    main()
