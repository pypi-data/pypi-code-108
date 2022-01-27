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

import configparser
import json
import json.decoder
import os.path
from pathlib import Path
from typing import Any, Callable

import attr
import tomli


@attr.s(auto_attribs=True)
class FHConfParser:
	"""FHConfParser.

	Returns:
		FHConfParser: parser object.
		- Call `parseConfigList` to parse files
		- Call `data` to access the internal rep
	"""

	data: dict = attr.ib(factory=dict, init=False)

	def parseConfigList(
		self,
		confList: list[tuple[str, str]],
		tomlNamespace: list[str] | None = None,
		jsonNamespace: list[str] | None = None,
	) -> list[str]:
		"""Parse a list of tuples containing paths to config files and the format.

		...and update the internal rep with the new data.

		e.g.

		>>> parseConfigList([("pyproject.toml", "toml"), (".config.ini", "ini")])

		Note that data is not overwritten so if "pyproject.toml" and ".config.ini"
		define some data at section.option then the value defined by "pyproject.toml"
		takes precedent.

		Args:
			confList (list[tuple[str, str]]): A list of tuples of config files
			and format. e.g. [("pyproject.toml", "toml"), (".config.ini", "ini")]
			tomlNamespace (list[str], optional): table to treat as root . Defaults to None.
			jsonNamespace (list[str], optional): define root. Defaults to None.

		Returns:
			list[str]: list of successfully parsed files
		"""
		readOK = []
		dispatchers = {
			"ini": self.parseIni,
			"toml": self.parseToml,
			"json": self.parseJson,
		}
		for conf in confList:
			if os.path.isfile(conf[0]):
				readOK.extend(
					dispatchers[conf[1]](
						conf[0], tomlNamespace=tomlNamespace, jsonNamespace=jsonNamespace
					)
				)
		return readOK

	def parseIni(self, file: str, throws: bool = False, **kwargs) -> list[str]:
		"""Parse a single ini file and update the internal rep with the new data.

		Args:
			file (str): config file to parse
			throws (bool): Throw an exception if there is a parsing failure.
			Defaults to False.
			kwargs: ignored

		Raises:
			ParsingError: if throws = True

		Returns:
			list[str]: list of successfully parsed files
		"""
		del kwargs
		ini = configparser.ConfigParser()
		try:
			ini.read(file)
		except configparser.ParsingError as error:
			if throws:
				raise error
			return []

		# Populate the data
		for section in ini.sections():
			options = self.data.get(section, {})
			for option in ini.options(section):
				# Get raw
				data = ini.get(section, option)
				# Cast to bool
				try:
					data = ini.getboolean(section, option)
				except ValueError:
					# Cast to float
					try:
						data = float(data)  # pylint:disable=redefined-variable-type
					except ValueError:
						# Cast to list (untyped)
						dataList = data.split(",")
						if len(dataList) > 1:
							data = [x.strip() for x in dataList]
				options[option] = data
			self.data[section] = options

		return [file]

	def parseToml(
		self, file: str, tomlNamespace: list[str] | None = None, throws: bool = False, **kwargs
	) -> list[str]:
		"""Parse a single toml file and update the internal rep with the new data.

		Args:
			file (str): config file to parse
			tomlNamespace (list[str], optional): table to treat as root . Defaults to None.
			throws (bool): Throw an exception if there is a parsing failure.
			Defaults to False.
			kwargs: ignored

		Raises:
			ParseError: if throws = True

		Returns:
			list[str]: list of successfully parsed files
		"""
		del kwargs
		try:
			doc = tomli.loads(Path(file).read_text(encoding="utf-8"))
		except tomli.TOMLDecodeError as error:
			if throws:
				raise error
			return []
		# **new, **original to prevent overwriting existing values
		self.data = {**_resolveNamespace(doc, tomlNamespace), **self.data}
		return [file]

	def parseJson(
		self, file: str, jsonNamespace: list[str] | None = None, throws: bool = False, **kwargs
	) -> list[str]:
		"""Parse a single json file and update the internal rep with the new data.

		Args:
			file (str): config file to parse
			jsonNamespace (list[str], optional): define root. Defaults to None.
			throws (bool): Throw an exception if there is a parsing failure.
			Defaults to False.
			kwargs: ignored

		Raises:
			JSONDecodeError: if throws = True

		Returns:
			list[str]: list of successfully parsed files
		"""
		del kwargs
		try:
			doc = json.loads(Path(file).read_text(encoding="utf-8"))
		except json.decoder.JSONDecodeError as error:
			if throws:
				raise error
			return []
		# **new, **original to prevent overwriting existing values
		self.data = {**_resolveNamespace(doc, jsonNamespace), **self.data}
		return [file]

	def hasSection(self, section: str | None) -> bool:
		"""Return True if the section present in the data rep.

		Args:
			section (str): section to get

		Returns:
			bool: Return True if the section present in the data rep.
		"""
		return section in self.data

	def hasOption(self, section: str | None, option: str) -> bool:
		"""Return True if the option present in the data rep (under a given section.

		Args:
			section (str): section to get
			option (str): ... and option to get

		Returns:
			bool: Return True if the option present in the data rep (under a given section
		"""
		return self.hasSection(section) and option in self.data[section]

	def defaults(self) -> dict[str, Any]:
		"""Return a dictionary containing the defaults.

		Returns:
			list[str]: A dictionary containing the defaults
		"""
		return {x: self.data[x] for x in self.data if not isinstance(self.data[x], dict)}

	def sections(self) -> list[str]:
		"""Return a list of the sections available.

		Returns:
			list[str]: A list of sections
		"""
		return [x for x in self.data if isinstance(self.data[x], dict)]

	def options(self, section: str | None) -> list[str]:
		"""Return a list of options available in the specified section.

		Args:
			section (str): the specified section

		Returns:
			list[str]: list of options
		"""
		return list(self.data[section])

	def get(self, section: str | None, option: str, fallback: Any = None) -> Any:
		"""Get a value from section.option with some fallback for if it doesn't exist.

		Args:
			section (str): the specified section
			option (str): the specified key/ option
			fallback (Any, optional): the fallback value for if it doesn't exist.
			Defaults to None.

		Returns:
			Any: the value at section.option or fallback
		"""
		if section is None and option in self.data:
			return self.data[option]
		if self.hasOption(section, option):
			return self.data[section][option]
		return fallback

	def getint(
		self, section: str | None, option: str, fallback: Any = None, strict: bool = True
	) -> int:
		"""Get a value from section.option with some fallback for if it doesn't exist as an int.

		Args:
			section (str): the specified section
			option (str): the specified key/ option
			fallback (Any, optional): the fallback value for if it doesn't exist.
			Defaults to None.
			strict (bool): raise an error if the cast fails when true, else return
			the value uncasted. Defaults to True

		Returns:
			int: the value at section.option or fallback (Any if strict=False)
		"""
		return _cast(self.get(section, option, fallback), int, strict)

	def getfloat(
		self, section: str | None, option: str, fallback: Any = None, strict: bool = True
	) -> float:
		"""Get a value from section.option with some fallback for if it doesn't exist as an float.

		Args:
			section (str): the specified section
			option (str): the specified key/ option
			fallback (Any, optional): the fallback value for if it doesn't exist.
			Defaults to None.
			strict (bool): raise an error if the cast fails when true, else return
			the value uncasted. Defaults to True

		Returns:
			float: the value at section.option or fallback (Any if strict=False)
		"""
		return _cast(self.get(section, option, fallback), float, strict)

	def getbool(
		self, section: str | None, option: str, fallback: Any = None, strict: bool = True
	) -> bool:
		"""Get a value from section.option with some fallback for if it doesn't exist as an bool.

		Args:
			section (str): the specified section
			option (str): the specified key/ option
			fallback (Any, optional): the fallback value for if it doesn't exist.
			Defaults to None.
			strict (bool): raise an error if the cast fails when true, else return
			the value uncasted. Defaults to True

		Returns:
			bool: the value at section.option or fallback (Any if strict=False)
		"""
		return _cast(self.get(section, option, fallback), bool, strict)

	def getstr(
		self, section: str | None, option: str, fallback: Any = None, strict: bool = True
	) -> str:
		"""Get a value from section.option with some fallback for if it doesn't exist as an str.

		Args:
			section (str): the specified section
			option (str): the specified key/ option
			fallback (Any, optional): the fallback value for if it doesn't exist.
			Defaults to None.
			strict (bool): raise an error if the cast fails when true, else return
			the value uncasted. Defaults to True

		Returns:
			str: the value at section.option or fallback (Any if strict=False)
		"""
		return _cast(self.get(section, option, fallback), str, strict)


def _resolveNamespace(doc: dict[str, Any], namespace: list[str] | None = None) -> dict[str, Any]:
	"""Take some document object and set the root to the namespace.

	Args:
		doc (dict[str, Any]): some document object dict[str, Any]
		namespace (list[str], optional): a list representing a namespace. e.g.
		["tool", "poetry"]. Defaults to None.

	Returns:
		dict[str, Any]: resolved document
	"""
	if namespace is None:
		return doc
	for part in namespace:
		doc = doc[part]
	return doc


def _cast(payload: Any, castFunc: Callable[[Any], Any], strict: bool = True) -> Any:
	"""Handy cast function. Raises a ValueError if fails when strict=True else...

	returns data unconverted.

	Args:
		payload (Any): data to convert
		castFunc (Callable[[Any], Any]): cast function eg int
		strict (bool, optional): throw error if true, otherwise return payload.
		Defaults to True.

	Raises:
		ValueError: if the cast fails and strict=True

	Returns:
		Any: casted payload
	"""
	try:
		payload = castFunc(payload)
	except ValueError as error:
		if strict:
			raise error
	return payload
