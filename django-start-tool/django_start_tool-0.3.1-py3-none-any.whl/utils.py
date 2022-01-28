import random
from jinja2 import Template


def get_content(file, context):
    template = Template(file.read_text())
    content = template.render(**context)
    eof = get_eof(file)
    return content + eof


def get_eof(file):
    ends = ['', '\n']
    size = file.stat().st_size
    return ends[size > 0]


def get_random_secret_key():
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return ''.join(random.choice(chars) for _ in range(50))


def get_subdir_name(url):
    url = url.replace('https://', '').split('/')
    repo = url[2]
    branch = url[4].replace('.zip', '')
    return f'{repo}-{branch}'


def is_url(template):
    template = str(template)
    schemes = ['http', 'https', 'ftp']

    if ':' not in template:
        return False

    scheme = template.split(':', 1)[0].lower()
    return scheme in schemes
