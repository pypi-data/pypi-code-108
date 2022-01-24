
import dataclasses
import re
import sys
import typing as t
from pathlib import Path

from cleo.io.io import IO
from ._config import VersionRefConfig
from .plugin_api import PoetryReleasePlugin, VersionRef


#regex = r'^\s*version\s*:\s*[\'"]?(.*?)[\'"]?\s*(#.*)?$'

def match_version_ref_pattern(filename: str, pattern: str) -> VersionRef:
  """ Matches a regular expression in the given file and returns the location of the match. The *pattern*
  should contain at least one capturing group. The first capturing group is considered the one that contains
  the version number exactly.

  :param filename: The file of which the contents will be checked against the pattern.
  :param pattern: The regular expression that contains at least one capturing group.
  """

  compiled_pattern = re.compile(pattern, re.M | re.S)
  if not compiled_pattern.groups:
    raise ValueError(
      f'pattern must contain at least one capturing group (filename: {filename!r}, pattern: {pattern!r})'
    )

  with open(filename) as fp:
    match = compiled_pattern.search(fp.read())
    if match:
      return VersionRef(filename, match.start(1), match.end(1), match.group(1))


@dataclasses.dataclass
class VersionRefConfigMatcherPlugin(PoetryReleasePlugin):
  """ This plugin matches a list of #VersionRefConfig definitions and returns the matched version references. This
  plugin is used to match the `tool.nr.poetry-release.references` config option and is always used. It should not be
  registered in the `poetry_release.plugins` entrypoint group.
  """

  PYPROJECT_CONFIG = VersionRefConfig('pyproject.toml', r'^version\s*=\s*[\'"]?(.*?)[\'"]')

  references: list[VersionRefConfig]

  def get_version_refs(self, io: IO) -> list[VersionRef]:
    results = []
    for config in [self.PYPROJECT_CONFIG] + self.references:
      pattern = config.pattern.replace('{version}', r'(.*)')
      version_ref = match_version_ref_pattern(config.file, pattern)
      if version_ref is not None:
        results.append(version_ref)
    return results


@dataclasses.dataclass
class SourceCodeVersionMatcherPlugin(PoetryReleasePlugin):
  """ This plugin searches for a `__version__` key in the source code of the project and return it as a version
  reference. Based on the Poetry configuration (considering `tool.poetry.packages` and searching in the `src/`
  folder if it exists), the following source files will be checked:

  * `__init__.py`
  * `__about__.py`
  * `_version.py`

  Note that configuring `tool.poetry.packages` is needed for the detection to work correctly with PEP420
  namespace packages.
  """

  VERSION_REGEX = r'^__version__\s*=\s*[\'"]([^\'"]+)[\'"]'
  FILENAMES = ['__init__.py', '__about__.py', '_version.py']

  #: The `tool.poetry.packages` configuration from `pyproject.toml`.
  packages_conf: list[dict[str, dict[str, t.Any]]] | None = None

  def get_version_refs(self, io: IO) -> list[VersionRef]:
    results = []
    for directory in self.get_package_roots():
      for filename in self.FILENAMES:
        path = directory / filename
        if path.exists():
          version_ref = match_version_ref_pattern(str(path), self.VERSION_REGEX)
          if version_ref:
            results.append(version_ref)
            break
    if not results:
      message = '<fg=yellow>warning: unable to detect <b>__version__</b> in a source file'
      if not self.packages_conf:
        message += ' (if your package is a PEP420 namespacepackage, configure <info>tool.poetry.packages</info>)'
      io.write_error_line(message + '</fg>')
    return results

  def get_package_roots(self) -> list[Path]:
    """ Tries to identify the package roots that may contain source files with a `__version__`. """

    src_dir = Path('.')
    if (sub_dir := src_dir / 'src').is_dir():
      src_dir = sub_dir

    results = []
    if self.packages_conf:
      for conf in self.packages_conf:
        results.append(src_dir / conf['include'])
    else:
      for item in src_dir.iterdir():
        if item.is_dir():
          results.append(item)

    return results
