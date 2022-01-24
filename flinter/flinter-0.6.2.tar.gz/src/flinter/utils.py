
import glob
import pkg_resources
import shutil

import yaml
from lizard_languages import languages


MAP_DEFAULT_RULE_NAMES = {
    'fortran': 'fortran_rc_default',
    'python': 'python_rc_default',
    'cpp': 'cpp_rc_default'
}

DEFAULT_RULE_NAMES = tuple(MAP_DEFAULT_RULE_NAMES.values())


def _get_default_rule_filename(rule_name):
    return pkg_resources.resource_filename("flinter", f'default_rules/{rule_name}.yml')


def load_default_rule(rule_name):
    filename = _get_default_rule_filename(rule_name)
    return load_rule(filename)


def load_default_rules(default_rule_names=DEFAULT_RULE_NAMES):
    return {rule_name: load_default_rule(rule_name) for rule_name in default_rule_names}


def load_rule(filename):
    with open(filename) as fin:
        rules = yaml.load(fin, Loader=yaml.FullLoader)

    return rules


def get_available_lizard_exts():
    exts = []
    for language in languages():
        exts.extend(language.ext)

    return set(exts)


def get_available_exts(rule_sets):
    lizard_exts = get_available_lizard_exts()
    return [ext for ext in lizard_exts if rule_sets.is_ext_available(ext)]


def get_all_analysable_files(dirname, rule_sets):
    exts = get_available_exts(rule_sets)

    files = []
    for ext in exts:
        files.extend(glob.glob(fr'{dirname}/**/*.{ext}', recursive=True))

    return files


def copy_default_rule(language, filename=None):
    rule_name = MAP_DEFAULT_RULE_NAMES[language]

    if filename is None:
        filename = f'{rule_name}.yaml'

    shutil.copy2(_get_default_rule_filename(rule_name), filename)

    return filename
