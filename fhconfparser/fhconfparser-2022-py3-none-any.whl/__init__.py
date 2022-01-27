"""Provides a config language independent way to read a config file.

## Rationale for project
For instance toml and ini syntax is very similar but not identical. Currently, tools such as
pylint must implement custom ways to deal with this. Hopefully this code
streamlines that a bit.

## Currently supports

- Ini
- Toml
- Json
"""

from __future__ import annotations

from .fhconfparser import FHConfParser
from .simpleconf import SimpleConf
