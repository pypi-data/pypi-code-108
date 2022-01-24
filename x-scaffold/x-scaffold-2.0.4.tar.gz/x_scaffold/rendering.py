import json
import os

from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2.nativetypes import NativeEnvironment

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

        with open(path, 'r') as file_handle:
            return yaml.load(file_handle, Loader=yaml.FullLoader)


def format_list(value, format='{value}'):
    for idx, x in enumerate(value):
        value[idx] = format.format(value=value[idx], index=idx)
    return value


def yaml_format(value):
    if value is None:
        return 'null'
    return yaml.dump(value, default_flow_style=True)


def json_format(value):
    if value is None:
        return 'null'
    return json.dumps(value)


def get_parser(path):
    ext = os.path.splitext(path)[1]
    if ext == '.yaml' or ext == '.yml':
        return yaml
    elif ext == '.json':
        return json
    else:
        exit('Parser format not supported: %s' % ext)


def render(template_name, context, template_dir):
    """Used to render a Jinja template."""

    env = Environment(loader=FileSystemLoader(template_dir), variable_start_string='${{', variable_end_string='}}')
    env.filters['formatlist'] = format_list
    env.filters['yaml'] = yaml_format
    env.filters['json'] = json_format
    utils = RenderUtils()

    template = env.get_template(template_name)

    return template.render(env=os.environ, utils=utils, **context)


def render_text(text, context: ScaffoldContext):
    """Used to render a Jinja template."""

    env = NativeEnvironment(variable_start_string='${{', variable_end_string='}}')
    env.filters['formatlist'] = format_list
    env.filters['yaml'] = yaml_format
    env.filters['json'] = json_format
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