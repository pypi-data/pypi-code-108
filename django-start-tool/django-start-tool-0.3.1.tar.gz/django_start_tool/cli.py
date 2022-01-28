import argparse
from pathlib import Path

from .handlers import handle_template
from .types import extra
from .types import files
from .types import target
from .types import template
from .utils import get_random_secret_key


DEFAULT_TEMPLATE = Path(__file__).resolve().parent / 'template'


def start(context):
    project_name = context.get('project_name')
    target = context.pop('target')
    template = context.pop('template')
    files_patterns = context.pop('files')
    context.setdefault(
        'secret_key',
        'django-insecure-' + get_random_secret_key()
    )

    handle_template(
        project_name,
        target,
        template,
        files_patterns,
        context
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'project_name',
        nargs='?',
        default='config',
        help='Name of the project. Default: "config"'
    )
    parser.add_argument(
        'target',
        nargs='?',
        type=target,
        default='.',
        help='Optional destination directory. Default: "."'
    )
    parser.add_argument(
        '-t', '--template',
        default=DEFAULT_TEMPLATE,
        type=template,
        help='The path or URL to load the template from.'
    )
    parser.add_argument(
        '-f', '--files',
        action='extend',
        default=['*-tpl'],
        type=files,
        help='The file glob pattern(s) that should be rendered.'
             ' Separate multiple file patterns with spaces.'
             ' Default: ["*-tpl"].'
    )
    parser.add_argument(
        '-e', '--extra',
        type=extra,
        help='Extra configuration parameters that should be rendered.'
             ' Separate multiple parameters with spaces and key value pairs'
             ' with equal sign. Will be available from `extra` object.'
    )

    context = parser.parse_args().__dict__
    start(context)


if __name__ == '__main__':
    main()
