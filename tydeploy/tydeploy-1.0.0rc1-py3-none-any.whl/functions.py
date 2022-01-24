from typing import List


def virtual_root(abspath: str, source_abspath: str) -> str:
    return abspath[len(source_abspath):].replace("\\", "/")


def unixpath(*values: str):
    stripped_values = [value.replace("\\", "/").strip("/") for value in values]
    return "/".join(stripped_values)
