import json
from ntpath import join
import os

from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2.nativetypes import NativeEnvironment
from ruamel.yaml import YAML

from x_scaffold.context import ScaffoldContext

class RenderUtils(object):  # pylint: disable=R0903
    """Template utilities."""

    @classmethod
    def read_file(cls, path, parse=False):
        """Used to read a file and return its contents."""

        with open(path, 'r') as file_handle:
            if parse:
                parser = get_parser(path)
                return parser.load(file_handle)
            else:
                return file_handle.read()

    @classmethod
    def read_json(cls, path):
        """Used to read a JSON file and return its contents."""

        with open(path, 'r') as file_handle:
            return json.load(file_handle)

    @classmethod
    def read_yaml(cls, path):
        """Used to read a YAML file and return its contents."""
        yaml = YAML()
        with open(path, 'r') as file_handle:
            return yaml.load(file_handle)
    
    @classmethod
    def random_string(cls, length=16, special_chars=''):
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789" + special_chars
        from os import urandom

        return "".join(chars[c % len(chars)] for c in urandom(length))


def format_list(value, format='{value}'):
    for idx, x in enumerate(value):
        value[idx] = format.format(value=value[idx], index=idx)
    return value


def yaml_format(value):
    if value is None:
        return 'null'
    yaml = YAML()
    return yaml.dump(value)


def json_format(value):
    if value is None:
        return 'null'
    return json.dumps(value)


def join_path(value, added_path):
    if value is None:
        return 'null'
    return os.path.join(value, added_path)


def get_parser(path):
    ext = os.path.splitext(path)[1]
    if ext == '.yaml' or ext == '.yml':
        yaml = YAML()
        return yaml
    elif ext == '.json':
        return json
    else:
        exit('Parser format not supported: %s' % ext)


def render(template_name, context, template_dir):
    """Used to render a Jinja template."""

    env = Environment(loader=FileSystemLoader(template_dir), variable_start_string='${{', variable_end_string='}}')
    add_filters(env)
    utils = RenderUtils()

    template = env.get_template(template_name)

    return template.render(env=os.environ, utils=utils, **context)

def add_filters(env):
    env.filters['formatlist'] = format_list
    env.filters['yaml'] = yaml_format
    env.filters['json'] = json_format
    env.filters['join_path'] = join_path


def render_value(text, context: ScaffoldContext):
    """Used to render a Jinja template."""

    env = NativeEnvironment(variable_start_string='${{', variable_end_string='}}')
    add_filters(env)
    utils = RenderUtils()

    template = env.from_string(text)

    return template.render(env=context.environ, utils=utils, **context)


def render_text(text, context: ScaffoldContext):
    """Used to render a Jinja template."""

    env = Environment(variable_start_string='${{', variable_end_string='}}')
    add_filters(env)
    utils = RenderUtils()

    template = env.from_string(text)

    return template.render(env=context.environ, utils=utils, **context)


def render_value(value, context: ScaffoldContext):
    if isinstance(value, str):
        return render_text(value, context)
    elif isinstance(value, list):
        v_list: list[str] = []
        for x in value:
            v_list.append(render_value(x, context))
        return v_list
    elif isinstance(value, dict):
        opts = value.copy()
        for k, v in opts.items():
            opts[k] = render_value(v, context)
        return opts
    else:
        return value

def render_options(options: dict, context: ScaffoldContext):
    return render_value(options, context)

def render_token_file(path: str, tokens: dict):
    """Used to render a Token File."""

    with open(path, 'r') as file_handle:
        content = file_handle.read()

    return render_tokens(content, tokens)

def render_tokens(content: str, tokens: dict):
    """Used to render a Token File."""

    for token in tokens:
        content = content.replace(token, tokens[token])
    return content