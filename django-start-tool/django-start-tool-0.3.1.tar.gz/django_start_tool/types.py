from pathlib import Path

from .utils import is_url


def extra(context):
    result = {}

    for item in context.split():
        key, value = item.split('=')
        result.update({key: value})

    return result


def files(files):
    return files.split()


def target(path):
    return Path(path).resolve()


def template(path):
    if is_url(path):
        return path

    path = Path(path).resolve()
    if path.exists():
        return path

    raise Exception(f'Template does not exists: {str(path)}')
