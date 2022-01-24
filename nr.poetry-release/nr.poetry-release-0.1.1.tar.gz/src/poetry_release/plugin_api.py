
import abc
import dataclasses
import pkg_resources
import os
import warnings

from cleo.io.io import IO


@dataclasses.dataclass
class VersionRef:
  """ Represents a reference to a version number in a file that can be updated. """

  filename: str
  start: int
  end: int
  value: str


class PoetryReleasePlugin:
  """ Interface for plugins that can provide additional version references or arbitrarily modify files in
  response to a version change.
  """

  def get_version_refs(self, io: IO) -> list[VersionRef]:
    """ Return a list of references to a version number that will be treated by the `poetry release` command. """

    return []

  def bump_version(self, target_version: str, dry: bool, io: IO) -> list[str]:
    """ Update other files as necessary and return a list of the changed files. """

    return []


def get_plugins() -> list[PoetryReleasePlugin]:
  """ Load all plugins registered via the entrypoint. """

  result = []
  for ep in pkg_resources.iter_entry_points('poetry_release.plugins'):
    cls = ep.load()
    if not isinstance(cls, type) or not issubclass(cls, PoetryReleasePlugin):
      warnings.warn(f'[poetry_release.plugins]: "{ep}" is not a subclass of PoetryReleasePlugin', UserWarning)
    else:
      result.append(cls())

  return result
