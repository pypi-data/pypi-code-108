#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2022 Evgeniy Privalov, https://linkedin.com/in/evgeniyprivalov/

from pathlib import Path
from typing import (
	Union,
	cast,
	IO,
	Type,
	Optional,
	TYPE_CHECKING
)

from tgsdk.utils.types import FileInput

if TYPE_CHECKING:
	from tgsdk import (
		InputFile,
		TelegramEntity
	)


def is_local_file(obj: Optional[Union[str, Path]]) -> bool:
	"""

	:param obj:
	:return:
	"""
	if obj is None:
		return False

	path = Path(obj)

	try:
		return path.is_file()
	except Exception:
		return False


def get_input_file(
	input_file: Union[FileInput, "TelegramEntity"],
	telegram_file_type: Type["TelegramEntity"] = None,
	as_attach: bool = None,
	file_name: str = None
) -> Union[str, "InputFile"]:
	"""

	:param input_file:
	:param telegram_file_type:
	:param as_attach:
	:param file_name:
	:return:
	"""
	from tgsdk import InputFile

	if isinstance(input_file, str) and input_file.startswith("file://"):
		return input_file

	if isinstance(input_file, (str, Path)):
		if is_local_file(input_file):
			file = Path(input_file).absolute().as_uri()
		else:
			file = input_file

		return file

	if isinstance(input_file, bytes):
		return InputFile(input_file, as_attach=as_attach, file_name=file_name)

	if InputFile.is_file(input_file):
		input_file = cast(IO, input_file)

		return InputFile(input_file, as_attach=as_attach, file_name=file_name)

	if telegram_file_type and isinstance(input_file, telegram_file_type):
		return input_file.file_id

	return input_file
