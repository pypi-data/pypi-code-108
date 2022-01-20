import re
from spell.cli.exceptions import ExitException


def parse_tag(tag):
    # returns a tuple of (version, name), where one is None
    if not tag.startswith("v"):
        return None, tag
    version_string = tag[1:]
    if version_string.isnumeric():
        return int(version_string), None
    return None, tag


def get_name_and_tag(specifier):
    name, _, tag = specifier.partition(":")
    if tag and not is_valid_specifier_part(tag):
        raise ExitException("Invalid tag {}".format(specifier))
    validate_server_name(name)
    return (name, tag if tag != "" else None)


def validate_server_name(name):
    if not is_valid_specifier_part(name):
        raise ExitException("Invalid name {}".format(name))


def is_valid_specifier_part(part):
    return bool(re.match(r"^\w+[\w._~-]*$", part))


def parse_model_version(model_version):
    model_name, tag = get_name_and_tag(model_version)
    if tag is None:
        raise ExitException("A model tag must be specified in the form model_name:version")
    model_version_id, model_version_name = parse_tag(tag)
    return model_name, model_version_id, model_version_name


def parse_model_versions(model_versions):
    return [parse_model_version(m) for m in model_versions]
