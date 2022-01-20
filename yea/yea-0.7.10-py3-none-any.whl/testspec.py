"""
Utilities for parsing a test specification.


"""

import ast

import yaml


def load_docstring(filepath):
    file_contents = ""
    with open(filepath) as fd:
        file_contents = fd.read()
    module = ast.parse(file_contents)
    docstring = ast.get_docstring(module)
    if docstring is None:
        docstring = ""
    return docstring


def find_yaml_str(s):
    """Loads YAML from docstring."""
    split_lines = s.split("\n")

    # Cut YAML from rest of docstring
    for index, line in enumerate(split_lines):
        line = line.strip()
        if line == "---" or line.startswith("--- "):
            # TODO: validate, capture type
            # !<tag:wandb.ai,2021:yea>
            cut_from = index + 1
            yaml_string = "\n".join(split_lines[cut_from:])
            return yaml_string
    return None


def load_yaml_from_docstring(docstring):
    found = find_yaml_str(docstring)
    if not found:
        return None
    return load_yaml_from_str(found)


def load_yaml_from_str(yaml_string):
    try:
        data = yaml.load(yaml_string, Loader=yaml.SafeLoader)
    except yaml.scanner.ScannerError:
        print("WARNING: Unable to parse yaml")
        data = {}
    return data


def load_yaml_from_file(filepath):
    file_contents = ""
    with open(filepath) as fd:
        file_contents = fd.read()
    found = find_yaml_str(file_contents)
    found = found or file_contents
    return load_yaml_from_str(found)
