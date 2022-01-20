
import re
import yaml

from .exceptions import BrokenYamlError, MissingSubstitutionKeyError


def load_yaml(yaml_content):
    try:
        return list(yaml.full_load_all(fix_yaml(yaml_content)))

    except yaml.parser.ParserError:
        raise BrokenYamlError("""
            It seems that you're yaml file is broken.

            Run in through some online validators to find the reason behind it.
        """)


def dump_yaml(yaml_content):
    return yaml.dump_all(yaml_content, default_flow_style=False)


def fix_yaml(yaml_content):
    FIX_PATTERN = re.compile(  # noqa
        r'(?P<start>^|\n)'
        r'(?P<indent>\s*)'
        r'(?P<key>[\w\-\s]+)\:\s*'
        r'\{\{\s*'
        r'(?P<variable>[\w\.\-]+)'
        r'\s*\}\}'
        r'(?P<rest>[\w\/\_\-\?\{\}\=\.]*)'
    )

    return FIX_PATTERN.sub(
        r"\g<start>\g<indent>\g<key>: '{{\g<variable>}}\g<rest>'",
        yaml_content)


def flatten(env):

    def _flatten(d, flat=None, keys=None):
        keys = keys or []
        for k, v in d.items():
            if isinstance(v, dict):
                _flatten(v, flat, keys + [k])

            else:
                env_name = '_'.join(keys + [k])
                flat[env_name] = v

    flat = {}
    _flatten(env, flat)
    return flat


def substitute(env):

    SUBSTITUTE_PATTERN = re.compile(r'{{\s*(?P<key>[\w\.]+)\s*}}')  # noqa

    def _substitute(match):
        key = match.group('key')

        try:
            return env[key.replace('.', '_')]

        except KeyError:
            raise MissingSubstitutionKeyError(f"""
                Your template variable is referring non-existent value under
                the '{key}' key.
            """)

    for k, v in env.items():
        if isinstance(v, str):
            env[k] = SUBSTITUTE_PATTERN.sub(_substitute, str(v))

    return env
