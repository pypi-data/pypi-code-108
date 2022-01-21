import json
from collections import namedtuple
from typing import Any, Dict, Iterable, List, Union

from valohai.internals.parsing import parse

NOTEBOOK_TAGS = {"parameters", "inputs"}

ParametersAndInputs = namedtuple("ParametersAndInputs", ["parameters", "inputs", "uses_tags"])


def parse_parameters_and_inputs(content_or_str: Union[str, dict]) -> ParametersAndInputs:
    """
    Parse parameters and inputs from a notebook content

    :param content_or_str: See parse_ipynb()
    :return: Tuple of (parameters, inputs)
    """
    contents = parse_ipynb(content_or_str)

    if notebook_uses_tags(contents, NOTEBOOK_TAGS):
        return ParametersAndInputs(
            parameters=parse_with_tag(contents, "parameters"),
            inputs=parse_with_tag(contents, "inputs"),
            uses_tags=True,
        )

    # No tags so let's try to parse with valohai-utils
    source = get_notebook_source_code(contents)
    config = parse(source)
    return ParametersAndInputs(
        parameters=config.parameters,
        inputs=config.inputs,
        uses_tags=False,
    )


def parse_ipynb(content_or_str: Union[str, dict]) -> dict:
    """
    "Smartly" parse content that contains a notebook.

    * If a string, it's first JSON deserialized.
    * If it's a "wrapped" dict (i.e. contains "type" == "notebook" and "content"), unwraps the content
    * Asserts the content smells like a notebook ("nbformat")

    :param content: See above.
    :return: Notebook data.
    """
    if isinstance(content_or_str, str):
        content = json.loads(content_or_str)
    else:
        content = content_or_str
    if not isinstance(content, dict):
        raise ValueError('Ipynb not a dict')
    assert isinstance(content, dict)
    if content.get('type') == 'notebook':
        content = content['content']

    nbformat = content.get('nbformat')
    if not isinstance(nbformat, int):
        raise ValueError('Nbformat value %s invalid' % nbformat)
    return content


def get_notebook_source_code(contents: dict) -> str:
    source = [cell['source'] for cell in contents['cells'] if cell['cell_type'] == 'code']

    # Some notebook versions store it as list of rows already. Some as single string.
    source = [row if isinstance(row, list) else row.split('\n') for row in source]

    # Even when it was a list, the linefeeds are still there.
    source = [row.rstrip() for sublist in source for row in sublist]

    # Replace magic lines like "!pip install tensorflow" with magic comments ("#!pip install...")
    source = [
        (("#" + row) if row.startswith(("!", "%")) else row)
        for row in source
    ]

    return '\n'.join(source)


def notebook_uses_tags(content: dict, tags: Iterable[str]) -> bool:
    tag_set = set(tags)
    for cell in content['cells']:
        if tag_set & set(get_tags(cell)):
            return True
    return False


def parse_with_tag(content: dict, tag: str) -> dict:
    code = get_notebook_tagged_code(content, tag)
    return execute_cell_code(code, tag=tag)


def get_notebook_tagged_code(content: dict, tag: str) -> str:
    result = ""
    for cell in content['cells']:
        if tag in get_tags(cell):
            result += '%s\r\n' % ''.join(cell['source'])
    return result


def get_tags(cell: dict) -> List[str]:
    if (
        cell
        and 'source' in cell
        and 'metadata' in cell
        and 'tags' in cell['metadata']
    ):
        return list(cell['metadata']['tags'])
    return []


def get_type_name(value: Union[str, int, None]) -> str:
    pythonic_name = type(value).__name__
    if pythonic_name == 'int':
        return "integer"
    if pythonic_name == 'bool':
        return "flag"
    if pythonic_name == 'str':
        return "string"
    return pythonic_name


def execute_cell_code(code: str, tag: str) -> dict:
    ns: Dict[str, Any] = {}
    try:
        compiled = compile(code, "<CODE>", "exec")
    except SyntaxError as err:
        raise SyntaxError(
            f"Syntax error in notebook cell tagged \"{tag}\" at line {err.lineno}: {err}."
        ) from err
    try:
        exec(compiled, globals(), ns)
    except Exception as err:
        raise Exception(
            f"Error executing notebook cell tagged \"{tag}\": {err}"
        ) from err
    return ns
