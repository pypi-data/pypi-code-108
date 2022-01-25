from random import sample
from jsonclasses_cli.utils.join_lines import join_lines


def conf_content(name: str) -> str:
    return join_lines([
        '{',
        _pymongo_conf(name),
        _operator_conf(),
        _package_conf(),
        '}'
    ])


def _operator_conf() -> str:
    return f"""
    "operator": {'{'}
        "secretKey": "{_randompuncs()}"
    {'}'},""".strip('\n')


def _randompuncs() -> str:
    ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
    ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    punctuation = r"""!#$%&()*+,-./:;<=>?@[/]^_`{|}~"""
    digits = '0123456789'
    ascii_letters = ascii_lowercase + ascii_uppercase
    return ''.join(sample(punctuation+ascii_letters+digits, 24))


def _pymongo_conf(dbname: str) -> str:
    return f"""
    "pymongo": {'{'}
        "url": "mongodb://localhost:27017/{dbname}"
    {'}'},""".strip('\n')

def _package_conf() -> str:
    return f"""
    "package": {'{'}
        "ts": {'{'}
            "url": "http://127.0.0.1:8000"
        {'}'},
        "swift": {'{'}
            "url": "http://127.0.0.1:8000"
        {'}'},
        "kotlin": {'{'}
            "url": "http://127.0.0.1:8000"
        {'}'}
    {'}'}""".strip('\n')
