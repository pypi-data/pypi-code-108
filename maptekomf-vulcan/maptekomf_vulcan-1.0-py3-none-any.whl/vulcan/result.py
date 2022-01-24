"""Module containing objects used to represent the results of an import
from an OMF file.

"""
###############################################################################
#
# (C) Copyright 2021, Maptek Pty Ltd. All rights reserved.
#
###############################################################################
import enum
import itertools

class Outcome(enum.Enum):
  """Enum of possible outcomes of importing or exporting an object."""
  SUCCESS = 0,
  """The operation was a success."""
  ERROR = 1,
  """The operation failed due to an error."""
  SKIPPED = 2,
  """The object was skipped due to an error."""
  FATAL = 3,
  """The operation failed due to a fatal error.

  This indicates that no further objects from the file should be imported.
  """

class ImportSummary:
  """Class representing a summary of the import of an OMF file.

  Successful import results are stored in a dictionary keyed by the
  destination file name.

  Failed and skipped import results are stored in a list.
  """
  def __init__(self):
    # Dictionary containing successful imports keyed by filename.
    self.successful_imports_dict = {}
    # Backing field containing a cached version of successful_imports_dict
    # as a flat list.
    self.__successful_imports = None
    # List of failed imports.
    self.failed_imports = []
    # If any error was considered fatal.
    self.fatal_error = False

  def add_result(self, result):
    """Add an import result to the object.

    Parameters
    ----------
    result : ImportResult
      The result of an import.

    """
    if not isinstance(result, ImportResult):
      type_name = type(result).__qualname__
      raise TypeError(f"Result must be ImportResult, not: {type_name}")
    if result.outcome is Outcome.SUCCESS:
      if result.destination_path in self.successful_imports_dict:
        self.successful_imports_dict[result.destination_path].append(result)
      else:
        self.successful_imports_dict[result.destination_path] = [result]
    else:
      self.failed_imports.append(result)
      if result.outcome is Outcome.FATAL:
        self.fatal_error = True
    # Delete the cached value for success results because a new result
    # was added to the object.
    self.__successful_imports = None

  def add_results(self, results):
    """Add an iterator of import results to the object.

    This also accepts a single ImportResult.

    Parameters
    ----------
    results : iterator or ImportResult
      Iterator of import result objects to add to the object or
      a single ImportResult object to add to the iterator.

    """
    if isinstance(results, ImportResult):
      self.add_result(results)
    else:
      for result in results:
        self.add_result(result)

  @property
  def successful_imports(self):
    """List containing all successful imports."""
    if self.__successful_imports is None:
      self.__successful_imports = list(
        itertools.chain(*self.successful_imports_dict.values()))
    return self.__successful_imports

  def file_names(self):
    """The names of the files successfully imported."""
    return self.successful_imports_dict.keys()

  def raise_first_error(self):
    """Raises the first error encountered by the import."""
    if self.failed_imports:
      raise self.failed_imports[0].error

  def __str__(self):
    lines = []
    for file_path, imported_objects in self.successful_imports_dict.items():
      if len(imported_objects) == 1:
        item = imported_objects[0]
        lines.append(f"Imported '{item}' to '{file_path}'")
      else:
        lines.append(f"The following objects were imported to: '{file_path}'")
        for item in self.successful_imports_dict[file_path]:
          lines.append(f"* {item}")
    if not self.successful_imports_dict:
      lines.append("No objects were successfully imported.")
    if self.failed_imports:
      lines.append("Failed to import the following objects:")
      for item in self.failed_imports:
        lines.append(f"* {item}")
    return "\n".join(lines)


class ImportResult:
  """Represents the result of the import of a single object from an OMF file.

  Parameters
  ----------
  outcome : Outcome
    Outcome enum value for the import.
  source : string
    Name of the object which was imported.
  destination_path : string
    Path to the destination the object was imported to. This should be
    None (default) if the import was not a success.
  layer_name : string
    The layer the object was placed in if it was imported to a dgd.isis
    file. This should be None (default) if not importing to a dgd.isis file.
  error : Exception
    The error which caused the import of this object to fail or be skipped.
    This should be None (default) if the import was not a success.
  error_is_fatal : bool
    The error is considered fatal and the import should stop without importing
    any more objects.

  Raises
  ------
  ValueError
    If any destination information is set for a failed or skipped import,
    or if error is set for a successful import.
  TypeError
    If result is not a member of the Outcome enum or error is not
    None or an Exception.
  """
  def __init__(self, outcome, source, *, destination_path=None,
               layer_name=None, object_name=None, error=None):
    if not isinstance(outcome, Outcome):
      raise TypeError(
        f"Unsupported type for outcome: {type(outcome).__qualname__}")
    any_destination_information = any(
      (destination_path, layer_name, object_name))
    if any_destination_information and outcome is not Outcome.SUCCESS:
      raise ValueError("Destination path only supported for outcome.SUCCESS")
    if error and outcome is Outcome.SUCCESS:
      raise ValueError("Error is only supported for outcome.ERROR")
    if not isinstance(error, (Exception, type(None))):
      raise TypeError("Error must be an Exception or None")

    self.outcome = outcome
    self.source = source
    self.destination_path = destination_path
    self.layer_name = layer_name
    self.object_name = object_name if object_name else source
    self.error = error

  def raise_if_error(self):
    """Raises the error if there is one."""
    if self.error:
      raise self.error

  def __str__(self):
    message = ""
    if self.outcome is Outcome.SUCCESS:
      message += f"{self.object_name}"
      if self.layer_name:
        message += f" (layer: {self.layer_name})"
    elif self.outcome is Outcome.ERROR or self.outcome is Outcome.FATAL:
      message += (f"'{self.source}' due to the "
                  f"following error: '{self.error}'")
    elif self.outcome is Outcome.SKIPPED:
      message += (f"Skipped: '{self.source}' due to the "
                  f"following error: '{self.error}'")
    assert message, "Message should not be empty"
    return message
