#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from pathlib import Path
from typing import (
	IO,
	TYPE_CHECKING,
	Union
)

if TYPE_CHECKING:
	pass

ID = Union[str, int]

FileInput = Union[str, bytes, Path, Union[IO, "InputFile"]]
