import re


def camel_to_underscore(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def verify_regex(pattern, value, param_name=''):
    is_valid = False
    if isinstance(value, str) and bool(value):
        is_valid = bool(re.match(pattern, value))
    if not is_valid:
        msg = 'Invalid <{}>, ${} require match <{}>'.format(value, param_name, pattern)
        raise ValueError(msg)


def verify_varname(value, param_name="name"):
    rp = "^[A-Za-z_][A-Za-z0-9_]*$"
    verify_regex(rp, value, param_name)


def verify_version(version):
    rp = "^\d+(?:\.\d+)*$"
    verify_regex(rp, version, 'version')


def check_version_ext(value):
    if value and isinstance(value, str):
        value = value.strip()
        rp = "\d+(?:\.\d+)*"
        m = re.match(rp, value)
        if m:
            version = m.group()
            ext = value.rsplit(version, 1)[-1].split('.', 1)[-1]
            if ext:
                return version, ext
    msg = 'Invalid <{}>, require format in $version.$file_ext'.format(value)
    raise ValueError(msg)
