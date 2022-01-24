"""Convert from OMF to Vulcan types and converts from Vulcan types
to OMF types.
"""
###############################################################################
#
# (C) Copyright 2021, Maptek Pty Ltd. All rights reserved.
#
###############################################################################
import itertools
import logging
import numpy as np
import omf
import os
import pathlib
import shutil

from .result import ImportResult, ImportSummary, Outcome
from .internal.util import setup_vulcan_environment

setup_vulcan_environment()
from maptek import vulcan

LOGGER = logging.getLogger('vulcanomf.import')

# The maximum suffix which can be given to make a name unique.
# This is the largest number representable by a length 5 string because
# for isis design databases 5 characters are allowed for the numerical suffix.
# This is ~7.5 times more than I have seen in an OMF file (2021-11-19).
MAXIMUM_NUMERICAL_SUFFIX = 99999

DEFAULT_POINT_SET_NAME = "point_set"
DEFAULT_LINE_NAME = "line"
DEFAULT_SURFACE_NAME = "surface"
DEFAULT_GRID_NAME = "grid"

# Characters which will be removed from names.
# This list is based on the characters which cannot be used in file names.
FORBIDDEN_CHARACTERS = ("<", ">", ":", "\"", "/", "\\", "|", "?", "*")

class CannotOverwriteError(Exception):
  """Exception raised if an object cannot be overwritten.

  This should never be raised if --overwrite was passed on the command
  line.

  """

class CannotReadOMFFile(Exception):
  """Exception raised when an OMF file cannot be read."""

class ImportConfiguration:
  """Class which holds import configuration.

  This class also contains two sets which are used to keep track of
  files and objects which have already been imported.

  Parameters
  ----------
  vulcan_project_directory : str
    Path to the Vulcan Project directory to place imported files in.
  dgd_name : str
    Name of the dgd isis database to place imported files in.
  overwrite : bool
    If the import should allow overwriting.

  """
  def __init__(self, vulcan_project_directory, dgd_name, overwrite):
    # Dictionary where the key is the name of an object which has already
    # been imported and the value is the numeric postfix which should be
    # given to the next imported object with that name.
    self.imported_dgd_object_names = {}

    # Dictionary where the key is the name of a file which has already
    # been imported and the value is a numeric postfix which should be
    # given to the next imported file with that name.
    self.imported_file_names = {}

    self.project_directory = vulcan_project_directory
    self.dgd_path = self.unique_name_for_file(dgd_name, ".dgd.isis")
    self.overwrite = overwrite

    # Dictionary of OMF types to the functions used to import them.
    self.type_to_converter = {
      omf.SurfaceElement : omf_to_vulcan_surface,
      omf.PointSetElement : omf_to_vulcan_point_set,
      omf.LineSetElement : omf_to_vulcan_line_set,
      omf.VolumeElement : omf_to_vulcan_block_model,
    }

    # Variable which tracks the open isis design database. This allows
    # multiple objects to be imported without closing and opening the database
    # between imports. This greatly speeds up the import because opening and
    # closing the design database is expensive.
    self.__opened_dgd = None

    # Dictionary of open layer objects. The key is the name and the value
    # is a tuple containing the layer object and a bool which is True
    # for new layers and False for existing layers.
    self.__layers = {}

  def get_dgd(self):
    """Returns the dgd isis database objects should be imported into.

    This is the isis design database at dgd_path. The database will be created
    if necessary.

    Returns
    -------
    vulcan.dgd
      dgd object representing the database at dgd_path.
    """
    if self.__opened_dgd is None:
      dgd_path = self.dgd_path
      mode = 'a' if os.path.exists(dgd_path) else 'create'
      self.__opened_dgd = vulcan.dgd(dgd_path, mode)
    return self.__opened_dgd

  def get_layer(self, name):
    """Returns the specified layer in the dgd isis as dgd_path.

    This handles creating the layer if it does not exist and caching
    layers.

    Returns
    -------
    vulcan.layer
      The layer with the specified name.

    Notes
    -----
    The layer is not saved or added to the isis design database until
    save_dgd() is called.
    """
    # If the layer is cached, return the cached value.
    if name in self.__layers:
      return self.__layers[name][0]

    dgd = self.get_dgd()
    try:
      layer = dgd.get_layer(name)
      if self.overwrite:
        layer.clear_objects()
      else:
        raise CannotOverwriteError(
          f"Cannot overwrite layer: '{name}' in design database.")
      self.__layers[name] = (layer, False)
    except ValueError:
      layer = vulcan.layer(name)
      self.__layers[name] = (layer, True)
    return layer

  def save_dgd(self):
    """Saves changes to the isis design database.

    This does nothing if no objects were written to the database.
    close_dgd should be called after calling this function.
    """
    if self.__opened_dgd is None:
      return
    dgd = self.get_dgd()
    for layer, is_new in self.__layers.values():
      if is_new:
        dgd.append(layer)
      else:
        dgd.save_layer(layer)

  def close_dgd(self):
    """Closes the isis design database opened by the import.

    This does nothing if the import did not open the database. Make sure
    to save the changes with save_dgd() before calling this function,
    otherwise the changes will be lost.
    """
    if self.__opened_dgd is None:
      return
    dgd = self.get_dgd()
    dgd.close()

  def unique_name_for_dgd(self, name):
    """Returns a unique name before it is used in an isis design database.

    Note that this does not guarantee that the name will not clash with
    any existing object in a isis design database, only that the name will not
    clash with any object imported using this instance of ImportConfiguration.

    Parameters
    ----------
    name : str
      The name to check.

    Returns
    -------
    str
      The name truncated to 34 characters and made unique via a 5 letter
      suffix if required.

    Warnings
    --------
    This function is not thread safe on a single instance of ImportConfiguration.
    """
    # Truncate the name to 34 characters. The maximum allowed length
    # in a dgd isis database is 40 so this leaves 6 characters for the
    # suffix.
    original_name = name[:34]

    final_name = self._add_unique_suffix_to_file_name(
      original_name, self.imported_dgd_object_names)

    return final_name

  def unique_name_for_file(self, name, extension):
    """Returns a unique name before it is used in a isis design database.

    This removes any invalid characters and prevents the name from being
    a reserved windows file name.
    Note that this does not guarantee that the name will not clash with
    any existing file in a Vulcan Project, only that the name will not
    clash with any file imported using this instance of ImportConfiguration.

    Parameters
    ----------
    name : str
      The name to check without any file extensions.
    extension : str
      The file extension the file should have.

    Returns
    -------
    str
      The name made unique.

    Warnings
    --------
    This function is not thread safe on a single instance of ImportConfiguration.

    Notes
    -----
    The functions unique_name_for_dgd() and unique_name_for_object() are
    independent.
    """
    suffix_to_type = {
      '.00t': 'tri',
      '.00g': 'grid',
      '.srg': 'grid',
      '.sfg': 'grid',
      '.tpg': 'grid',
      '.isis': 'db',
    }

    if pathlib.Path(name.strip()).is_reserved():
      suffix = suffix_to_type[extension]
      if not suffix:
        raise ValueError(
          f"Unable to create a file called {name} because it contains a word "
          "reserved by Microsoft Windows.")
      name = f"{name}_{suffix}"

    final_name = self._add_unique_suffix_to_file_name(
      name, self.imported_file_names, extension)
    return os.path.join(self.project_directory, final_name)

  def _add_unique_suffix_to_file_name(self, name, name_dictionary, extension=""):
    """Returns a unique name and updates the name dictionary.

    Parameters
    ----------
    name : str
      The name to make unique.
    name_dictionary : dict
      Dictionary where the keys are names which have already been used
      and the values are the next numerical suffix which is expected
      to be unused. The dictionary will be updated based on the return
      value.
    extension : str
      File extension to add to the end of the name. If omitted, defaults
      to the empty string.

    Returns
    -------
    str
      name if it is not in name_dictionary, otherwise name with the
      smallest numeric suffix required so that it does not colide with
      a name in name_dictionary. Forbidden characters will be replaced
      with an underscore.
    """
    # Replace forbidden characters with underscores.
    for character in FORBIDDEN_CHARACTERS:
      name = name.replace(character, "_")

    # The current name. When using it as a key to the dictionary, casefold
    # it so that "cube", "Cube" and "cUBE" are all considered the same name.
    current_name = f"{name}{extension}"
    key = current_name.casefold()
    original_key = key

    if key in name_dictionary:
      base_name = f"{name} %d{extension}"
      # Start iterating at the value in the dictionary. This is one more
      # than the last prefix given to an object with this name.
      start_index = name_dictionary[key]

      # Usually this while loop will only run once.
      # This handles a case with objects:
      # "cube 1", "cube 1 1", "cube 1"
      # 1: "cube 1" would be imported to "cube 1".
      # 2: "cube 1 1" would be imported to "cube 1 1"
      # 3: The first iteration of this loop would give "cube 1 1"
      #    which was already imported due to step 2. Thus a second iteration
      #    is required to name the third object "cube 1 2".
      for index in range(start_index, MAXIMUM_NUMERICAL_SUFFIX):
        current_name = base_name % index
        key = current_name.casefold()
        if key not in name_dictionary:
          name_dictionary[original_key] = index
          break
      else:
        raise RuntimeError(
            f"The file contains more than {MAXIMUM_NUMERICAL_SUFFIX} "
            "objects with the same name.")

    name_dictionary[key] = 1
    return current_name

def texture_to_file(texture_element: omf.ImageTexture,
                    configuration: ImportConfiguration):
  """Write out the given texture to a PNG file.

  Parameters
  ----------
  texture_element : omf.ImageTexture
    Texture element to write out.
  configuration : ImportConfiguration
    Configuration to use for the import.

  Returns
  -------
  ImportResult
    ImportResult representing the import of the texture.
  """
  name = (texture_element.name or texture_element.image.name or
          str(texture_element.uid))

  image_path = configuration.unique_name_for_file(
    name, '' if name.endswith('.png') else '.png')

  with open(image_path, 'wb') as writer:
    shutil.copyfileobj(texture_element.image, writer)

  return ImportResult(
            Outcome.SUCCESS,
            name,
            destination_path=image_path)


def omf_to_vulcan_surface(surface_element: omf.SurfaceElement,
                          configuration: ImportConfiguration):
  """Convert a surface element in OMF to a Vulcan surface.

  Parameters
  ----------
  surface_element : omf.SurfaceElement
    The surface element to import. This function supports surface elements
    with both omf.SurfaceGeometry and omf.SurfaceGridGeometry.
  configuration : ImportConfiguration
    Configuration to use for the import.

  Returns
  -------
  ImportResult or list
    An import result representing a successful import or a list of
    import results. The first item in the list will be the
    import of a surface and the others will be imports of textures.

  Raises
  ------
  CannotOverwriteError
    If overwrite is false and a file would be overwritten by the import.
  ValueError
    If the surface contains attributes with an unsupported location
  TypeError
    If the surface element's geometry is not SurfaceGeometry or
    SurfaceGridGeometry.
  RuntimeError
    If an unknown error occurs.
  """
  if isinstance(surface_element.geometry,
                omf.surface.SurfaceGeometry):
    results = []
    surface_path = _omf_to_vulcan_triangulation(
      surface_element, configuration)
    results.append(ImportResult(
      Outcome.SUCCESS,
      surface_element.name,
      destination_path=surface_path))

    # :TODO: SDK-532 Properly support texturing.
    if surface_element.textures:
      for texture in surface_element.textures:
        try:
          image_result = texture_to_file(
            texture, configuration)
          results.append(image_result)
          message = ("Imported texture to '%s'. "
                     "Note: Generating an ireg file is not yet implemented. "
                     "The texture was not associated with '%s'.")
          LOGGER.warning(message, image_result.destination_path, surface_path)
        except Exception as error:
          results.append(ImportResult(
            Outcome.ERROR,
            texture.name,
            error=error))

    return results
  elif isinstance(surface_element.geometry,
                  omf.surface.SurfaceGridGeometry):
    grid_path = _omf_to_vulcan_grid(
      surface_element, configuration)

    if surface_element.textures:
      texture_count = len(surface_element.textures)
      LOGGER.info(f'Ignoring {texture_count} textures on grid')

    return ImportResult(
      Outcome.SUCCESS,
      surface_element.name,
      destination_path=grid_path)
  else:
    raise TypeError('Surface contains an unrecognised geometry type.')


def omf_to_vulcan_point_set(point_set_element: omf.PointSetElement,
                            configuration: ImportConfiguration):
  """Convert a point set element in OMF to a Vulcan point list.

  Parameters
  ----------
  point_set_element : omf.PointSetElement
    The point set element to import.
  configuration : ImportConfiguration
    Configuration to use for the import.

  Returns
  -------
  ImportResult
    Import result representing a successful import.

  Raises
  ------
  CannotOverwriteError
    If overwrite is False and the import would overwrite an existing object.
  RuntimeError
    If an unknown error occurs.
  """
  geometry  = point_set_element.geometry
  points = geometry.vertices + geometry.origin
  # Point sets don't have edges.
  edges = []

  return _omf_to_vulcan_polyline(
    point_set_element,
    point_set_element.name or DEFAULT_POINT_SET_NAME,
    points,
    edges,
    configuration)


def omf_to_vulcan_line_set(line_set_element: omf.LineSetElement,
                           configuration: ImportConfiguration):
  """Convert a line set element in OMF to a Vulcan polyline.

  Parameters
  ----------
  line_set_element : omf.LineSetElement
    The line set element to import.
  configuration : ImportConfiguration
    Configuration to use for the import.

  Returns
  -------
  ImportResult
    Import result representing a successful import.

  Raises
  ------
  ValueError
    If the line set cannot be represented in Vulcan.
  CannotOverwriteError
    If overwrite is False and the import would overwrite an existing object.
  RuntimeError
    If an unknown error occurs.
  """
  geometry  = line_set_element.geometry
  points = geometry.vertices + geometry.origin
  edges = geometry.segments

  return _omf_to_vulcan_polyline(
    line_set_element,
    line_set_element.name or DEFAULT_LINE_NAME,
    points,
    edges,
    configuration)


def omf_to_vulcan_block_model(volume_element: omf.VolumeElement,
                              configuration: ImportConfiguration):
  """Import a block model from an omf file.

  Warnings
  --------
  This function is not implemented.

  Parameters
  ----------
  volume_element : omf.VolumeElement
    The volume element to import as a block model.
  configuration : ImportConfiguration
    Configuration to use for the import.

  Returns
  -------
  ImportResult
    Import result representing a skipped import.

  """
  LOGGER.info('Project contains an block model (called {0}) which are not yet '
              'implemented.',
              volume_element.name)
  return ImportResult(
    Outcome.SKIPPED,
    volume_element.name,
    error=NotImplementedError("Importing volume elements is not implemented."))

def omf_to_vulcan_project(omf_project, vulcan_project_directory, *,
                          overwrite):
  """Convert all supported elements in an OMF project to a Vulcan project.

  Parameters
  ----------
  omf_project: omf.base.Project or str
    The OMF project or path to an OMF file.

  vulcan_project_directory : str
    The path to where to write out a Vulcan project containing the objects
    in the OMF project.

  overwrite : bool
    If False the import will stop if it would overwrite an
    existing object. Note that this can result in partially imported files.
    If True, existing objects may be overwritten by the import operation.

  Returns
  -------
  list
    ImportSummary object summarising the import.
  """
  if not isinstance(omf_project, omf.base.Project):
    # Assume that it is a path.
    # Use the file name (without the extension) as the name for the
    # dgd isis.
    try:
      dgd_name = os.path.splitext(os.path.basename(omf_project))[0]
      omf_reader = omf.OMFReader(omf_project)
      omf_project = omf_reader.get_project()
    except FileNotFoundError:
      raise
    except Exception as error:
      raise CannotReadOMFFile(
        f"Cannot read the OMF file at the path: '{omf_project}'. "
        "It likely does not conform to the OMF specification."
      ) from error
  else:
    dgd_name = "omf"

  os.makedirs(vulcan_project_directory, exist_ok=True)

  results = ImportSummary()

  configuration = ImportConfiguration(
    vulcan_project_directory, dgd_name, overwrite)

  # TODO: Consider writing a Workbench Project file to the directory.
  # TODO: Consider writing a Vulcan dg1 project file to the directory.

  try:
    for element in omf_project.elements:
      result = _import_omf_element(element, configuration)
      results.add_results(result)
      # If the results object has detected a fatal error, stop the
      # import here.
      if results.fatal_error:
        break
    configuration.save_dgd()
  finally:
    configuration.close_dgd()

  return results

def _import_omf_element(element, configuration):
  """Imports an OMF element using the passed configuration.

  Parameters
  ----------
  element : omf.base.ProjectElementData
    OMF element to import.
  configuration : ImportConfiguration
    Configuration to use for the import.

  Returns
  -------
  ImportResult or list of ImportResult
    The results of the import.
  """
  try:
    converter = configuration.type_to_converter[type(element)]
    import_results = converter(
      element,
      configuration)
    return import_results
  except IndexError:
    LOGGER.info('Project contains an unsupported element type called %s: %s',
                element.name,
                type(element).__name__)

    # :TODO: Make this a NotSupportedError instead of a ValueError?
    return ImportResult(
      Outcome.SKIPPED,
      element.name,
      error=ValueError(
        f"{element.name} is of type: {type(element).__name__} which is "
        "not supported."))
  except CannotOverwriteError as error:
    # An object would have been overwritten by the import. This is
    # considered a fatal error.
    return ImportResult(
      Outcome.FATAL,
      element.name,
      error=error)
  except Exception as error:
    # Other errors indicate the object could not be represented in
    # Vulcan for some reason and are treated as non-fatal.
    # Skip the object rather than stopping the import.
    return ImportResult(
      Outcome.ERROR,
      element.name,
      error=error)

def _edges_to_connectedness(edges, point_count):
  """Calculate the connectedness of a polyline based on edges.

  Parameters
  ----------
  edges : array_like
    Two dimensional array_like of shape (X, 2) where X is the number of
    edges. Each row is of the form [start, end] where start is the index
    of the start point and end is the index of the end point.
  point_count : int
    The number of points in the polyline.

  Returns
  -------
  list
    List containing point_count elements. The ith element of i is
    0 if point i is not connected to the previous point and 1 if
    it is connected to the previous point.
  bool
    True if the polyline should be closed, False otherwise.

  Raises
  ------
  ValueError
    If the edges array indicate one point is connected to more than two
    other points, or if an edge connects points with non-adjacent indices.

  Notes
  -----
  This handles duplicate edges.

  """
  connected = np.zeros(point_count, int)
  closed = False
  for start, end in edges:
    if start == end:
      LOGGER.info("Ignoring degenerate edge: (%s, %s)", start, end)
      continue
    if start > end:
      start, end = end, start
    # If there is an edge going from the start to the end, the
    # polyline should be closed.
    if start == 0 and end == point_count - 1:
      closed = True
      continue
    if start + 1 != end:
      # Assuming there are no forks in the line, such a line could be
      # imported by reordering the points. But that is too much effort,
      # so raise an error instead.
      raise ValueError("Edges between non-adjacent point indices are not "
                       f"supported. Unsupported edge: ({start},{end})")
    connected[end] = 1

  return connected, closed


def _omf_to_vulcan_polyline(omf_element: omf.base.ProjectElementData,
                            original_name,
                            vertices,
                            edges,
                            configuration: ImportConfiguration):
  """Creates a Vulcan Polyline using an omf element and the geometry.

  Parameters
  ----------
  omf_element : omf.base.ProjectElementData
    OMF element to use to populate the metadata of the polyline.
  original_name : str
    The name to give the new polyline.
  vertices : array_like
    Array like of shape (N, 3) of 64 bit floats where N is the point count.
  edges : array_like
    Array of shape (M, 2) where M is the edge count. Each edge is of the
    form (start, end) where start < N and end < N.
  configuration : ImportConfiguration
    Import configuration used to configure the import.
  """
  point_count = vertices.shape[0]
  r, g, b = omf_element.color
  uniform_colour = '0x{:02X}{:02X}{:02X}'.format(r, g, b)
  layer_name = "CAD_OMF"
  description = omf_element.description
  metadata = vulcan.metadata()
  metadata.set_field("OMF UID", str(omf_element.uid))
  metadata.set_field("Date Created", str(omf_element.date_created))
  metadata.set_field("Date Modified", str(omf_element.date_modified))
  metadata.set_field("OMF subtype", omf_element.subtype)

  dgd_path = configuration.dgd_path
  unique_name = configuration.unique_name_for_dgd(original_name)

  per_point_colours = None
  # Process remaining attributes.
  for datum in omf_element.data:
    if datum.location == "vertices":
      if isinstance(datum, omf.ColorData) and datum.name == "point colours":
        per_point_colours = []
        for r, g, b in datum.array:
          per_point_colours.append('0x{:02X}{:02X}{:02X}'.format(r, g, b))
      else:
        LOGGER.info(f"Ignoring per-vertex attribute: {datum.name}")
    elif datum.location == "segments":
      LOGGER.info(f'Ignoring per-edge attribute: {datum.name}')

  actual_colours = per_point_colours or itertools.repeat(uniform_colour,
                                                         point_count)

  # Convert the edges to an array indicating which points are connected
  # to the previous points.
  connected, closed = _edges_to_connectedness(edges, point_count)

  # Get the layer from the configuration. This will handle creating the
  # isis design database and the layer if required.
  layer = configuration.get_layer(layer_name)

  polyline = vulcan.polyline()
  polyline.name = unique_name
  polyline.description = description
  # This feature indicates that the names of the points are their
  # colour as a hexadecimal string.
  polyline.feature = "COLRGBPTS"
  polyline.set_metadata(metadata)
  if closed:
    polyline.set_closed()

  points = []
  for (x, y, z), connected, colour in zip(
      vertices, connected, actual_colours):
    # Arguments are: x, y, z, w, t, name
    # Name is set to the colour as a hexadecimal string.
    # t indicates if the point is connected to the previous one.
    # 1 indicates connected, 0 indicates not connected.
    points.append(vulcan.point(x, y, z, 0, int(connected), colour))
  polyline.set_coordinates(points)

  layer.append(polyline)

  return ImportResult(
    Outcome.SUCCESS,
    omf_element.name,
    destination_path=dgd_path,
    layer_name=layer_name,
    object_name=unique_name)


def _omf_to_vulcan_triangulation(
    surface_element: omf.SurfaceElement, configuration: ImportConfiguration):
  """Converts an OMF surface element to a Vulcan 00t file.

  Parameters
  ----------
  surface_element : omf.SurfaceElement
    The surface element to import. This should have geometry as a
    SurfaceGeometry.
  configuration : ImportConfiguration
    Configuration to use for the import.

  Returns
  -------
  str
    The path to the imported triangulation.

  Raises
  ------
  CannotOverwriteError
    If overwrite is false and the import would overwrite an existing file.
  ValueError
    If the triangulation has data not associated with vertices or faces.
  RuntimeError
    If an unknown error occurs.
  """
  name = surface_element.name.strip() or DEFAULT_SURFACE_NAME
  triangulation_path = configuration.unique_name_for_file(
    name, '.00t')

  # vulcan.triangulation fails if the path contains greater than
  # 255 characters. This failure seems to only be detectable because save()
  # will return false and the 00t will not be created.
  # Names this long aren't expected to be common so raise an error.
  path_length = len(triangulation_path)
  if path_length > 255:
    raise RuntimeError("Cannot import to the following path because the "
                       f"file name is too long ({path_length} characters): "
                       f"'{triangulation_path}'")

  if not configuration.overwrite and os.path.exists(triangulation_path):
    message = (f"Cannot overwrite file '{triangulation_path}'.")
    raise CannotOverwriteError(message)

  points = surface_element.geometry.vertices.array

  # Apply the origin transformation to the points.
  points += surface_element.geometry.origin
  facets = surface_element.geometry.triangles.array

  triangulation = vulcan.triangulation(triangulation_path, 'w')
  # Clear the triangulation. This should have already raised
  # an error if overwriting is not allowed. This should be a
  # safe way to overwrite an existing triangulation.
  triangulation.clear()
  triangulation.set_colour(list(surface_element.color))

  triangulation.put_vertices(points)
  triangulation.put_faces(facets)

  success = triangulation.save()
  if not success:
    raise RuntimeError("Unknown error when saving triangulation "
                       f"to: {triangulation_path}")

  # Populate the attributes on the triangulation
  attributes = vulcan.tri_attributes(triangulation_path)
  assert attributes.is_ok()
  attributes.put('OMF UID', str(surface_element.uid), 'String')
  attributes.put('Description', surface_element.description, 'String')

  attributes.put(
    'Date Created',
    surface_element.date_created.strftime(r"%Y/%m/%d"), 'Date.YMD')
  attributes.put(
    'Date Modified',
    surface_element.date_modified.strftime(r"%Y/%m/%d"), 'Date.YMD')
  attributes.save()

  # Process remaining attributes.
  for datum in surface_element.data:
    if datum.location == 'vertices':
      LOGGER.info('Ignoring per-vertex attribute')
    elif datum.location == 'faces':
      LOGGER.info('Ignoring per-facets/faces attribute')
    else:
      raise ValueError(f'Unexpected location for data: {datum.location}')

  return triangulation_path

def _omf_to_vulcan_grid(surface_element: omf.SurfaceElement,
                        configuration: ImportConfiguration):
  """Import a OMF grid to a Vulcan grid file.

  Parameters
  ----------
  surface_element : omf.SurfaceElement
    The surface element to import. This should have geometry as a
    SurfaceGridGeometry.
  configuration : ImportConfiguration
    Configuration to use for the import.

  Returns
  -------
  str
    The path to the imported grid.

  Raises
  ------
  CannotOverwriteError
    If overwrite is false and the import would overwrite an existing file.
  ValueError
    If the triangulation has data not associated with vertices or faces.
  RuntimeError
    If an unknown error occurs.
  """
  name = surface_element.name.strip() or DEFAULT_GRID_NAME
  # The surface is represented as a 2D grid.
  # tpg = ToPography Grid
  # sfg = Structural Floor Grid
  # srg = Structural Roof Grid
  # We're using tpg because we don't know if it is the roof or the floor.
  grid_path = configuration.unique_name_for_file(name, '.tpg')

  # If the path is longer than this it will be truncated (likely losing
  # the file extension).
  # Names this long aren't expected to be common so raise an error.
  path_length = len(grid_path)
  if path_length > 255:
    raise RuntimeError("Cannot import to the following path because the "
                       f"file name is too long ({path_length} characters): "
                       f"'{grid_path}'")

  if not configuration.overwrite and os.path.exists(grid_path):
    message = (f"Cannot overwrite file '{grid_path}'.")
    raise CannotOverwriteError(message)

  grid_geometry = surface_element.geometry
  grid_geometry: omf.surface.SurfaceGridGeometry

  # Tensors representing the widths of the rows and columns.
  tensor_u = grid_geometry.tensor_u
  tensor_v = grid_geometry.tensor_v

  # The counts of the tensors. They are 1 dimensional arrays.
  # Each tensor corresponds to the height/width of one cell.
  size_u = tensor_u.shape[0]
  size_v = tensor_v.shape[0]

  # Supporting zero-size grids doesn't seem useful.
  if size_u == 0 or size_v == 0:
    raise ValueError("Grids with zero rows or columns are not supported."
                      f"Shape: ({size_u}, {size_v})")

  if not np.array_equal(grid_geometry.axis_u, [1, 0, 0]):
    raise ValueError("Grid surfaces with tensor u not corresponding "
                      "To the x-axis are not supported.")
  if not np.array_equal(grid_geometry.axis_v, [0, 1, 0]):
    raise ValueError("Grid surfaces with tensor v not corresponding "
                      "To the y-axis are not supported.")

  origin = grid_geometry.origin

  # The vertical offsets. These can be omitted. The OMF documentation
  # is not clear what it means for them to be omitted. We assume
  # that omitting them is the same as setting them to zero for
  # each point.
  offset_w = grid_geometry.offset_w
  if offset_w:
    # Get the w values from the file and reshape them to be the correct
    # shape. Then transpose them because Vulcan and OMFs representations
    # of grids are transposed relative to each other.
    offset_w = np.array(grid_geometry.offset_w, dtype=np.float32)
    offset_w.reshape(size_u + 1, size_v + 1)
    offset_w = offset_w.T
  else:
    offset_w = np.zeros(((size_u + 1) * (size_v + 1)), dtype=np.float32)
  # Apply z coordinate of the origin to the vertical offsets.
  offset_w += origin[2]

  if not (np.allclose(tensor_u, tensor_u[0])):
    raise ValueError("Grid surfaces with non-uniform tensors are not supported.")
  if not (np.allclose(tensor_v, tensor_v[0])):
    raise ValueError("Grid surfaces with non-uniform tensors are not supported.")

  # :TODO: This gives an operation not permitted error if the file
  # doesn't already exist.
  # The version of the Vulcan Python SDK used by this importer does not
  # support creating grids - it is actually a bug that this call
  # creates the grid file.
  # For now exploit the bug. If a constructor is added to the vulcan sdk
  # this should try to use that constructor, and if that fails
  # default to the buggy behaviour.
  vulcan_grid = vulcan.grid(grid_path)

  # Add one to each size to get the number of points (rather than the
  # number of cells) in each direction.
  vulcan_grid.set_size(size_u + 1, size_v + 1)

  # Set the size of each cell.
  vulcan_grid.set_dx(tensor_u[0])
  vulcan_grid.set_dy(tensor_v[0])

  # Set the x and y component of the origin.
  vulcan_grid.set_x0(origin[0])
  vulcan_grid.set_y0(origin[1])

  # Set the elevation values. The z component of the origin was added above.
  vulcan_grid.put_grid(offset_w)
  # The mask is all ones. OMF does not support holes in the grid geometry.
  vulcan_grid.put_grid_mask(np.ones_like(offset_w, dtype=np.int64))

  LOGGER.info("Ignoring attribute: OMF UID")
  LOGGER.info("Ignoring attribute: Description")
  LOGGER.info("Ignoring attribute: Date Created")
  LOGGER.info("Ignoring attribute: Date Modified")

  # Process remaining attributes.
  for datum in surface_element.data:
    if datum.location == 'vertices':
      if datum.name == "visibility":
        mask = np.array(datum.array)
        dtype = mask.dtype
        if dtype == np.int64:
          mask = mask.reshape(size_u + 1, size_v + 1).T
          vulcan_grid.put_grid_mask(mask)
        else:
          LOGGER.warning(
            "Found per-vertex 'visibility' attribute, but it was the wrong "
            f"type. Given: {dtype}, expected numpy.uint64.")
      else:
        LOGGER.info(f'Ignoring per-vertex attribute: {datum.name}')
    elif datum.location == 'cells':
      LOGGER.info(f'Ignoring per-cell attribute: {datum.name}')
    else:
      raise ValueError(f'Unexpected location for data: {datum.location}')

  if not vulcan_grid.ok:
    raise RuntimeError("Unknown error when importing grid.")
  result = vulcan_grid.save(grid_path)

  if result != 0:
    raise RuntimeError("Unknown error when importing grid.")

  return grid_path
