"""Convert Vulcan types into an OMF file."""
###############################################################################
#
# (C) Copyright 2021, Maptek Pty Ltd. All rights reserved.
#
###############################################################################

import logging
import numpy as np
import omf
import os
import pathlib

from .internal.util import setup_vulcan_environment

setup_vulcan_environment()
from maptek import vulcan

LOGGER = logging.getLogger('vulcanomf.export')

# These lists are based on the default extensions enabled for these
# formats in the Vulcan preferences. If customers need additional formats
# it may be preferable to add functions for adding other formats to these
# lists or to read the extensions from their Vulcan preferences.
grid_file_extensions = [".00g", ".sfg", ".srg", ".cfg", ".msg", ".tpg"]
triangulation_file_extensions = [".00t", ".hgt"]

def grid_to_omf(grid_path):
  """Converts a Vulcan grid file (00g) into an OMF element.

  Parameters
  ----------
  grid_path : str
    Path to the Vulcan grid file to export.

  Returns
  -------
  list
    List of omf.SurfaceElement containing a single item representing
    the exported grid.
  """
  grid = vulcan.grid(grid_path)
  name = pathlib.Path(grid_path).stem

  # get_nx and get_ny return the count of rows and columns of points.
  # SurfaceGridGeometry wants the count of rows and columns of cells.
  # Subtract one from both counts to convert to the counts OMF wants.
  x_count = grid.get_nx() - 1
  y_count = grid.get_ny() - 1

  # All of the rows/columns of a Vulcan grid are equally spaced therefore
  # all values in the tensor arrays are the same.
  dx = grid.get_dx()
  dy = grid.get_dy()

  axis_u = [1, 0, 0]
  axis_v = [0, 1, 0]

  # The origin of the grid. Vulcan grid files only have an x and y
  # for the origin so treat the z as zero.
  x0 = grid.get_x0()
  y0 = grid.get_y0()
  z0 = 0

  grid_z = grid.get_grid().T
  mask = grid.get_grid_mask().T

  # Negative dx/dy values cannot be handled through negative tensor values
  # because grids in OMF 2.0 grids correctly do not support that.
  # Setting the axes to be negative is also problematic because it inverts the
  # z values in that direction.
  # Instead, translate the grid and flip the z values and mask values on that
  # axis.
  # For example given:
  # 1: The x axis points up.
  # 2: The y axis points to the right.
  # 3: * represents the point (x0, y0).
  # 4: Arrows represent the tensors defining the grid.
  # Then the following grid (dx=-1, dy=-1):
  # <-<-<-<-*
  #         |
  #         v
  #         |
  #         v
  #
  # Is instead represented as:
  # ^
  # |
  # ^
  # |
  # *->->->->
  if dx < 0:
    dx = abs(dx)
    x0 -= dx * x_count
    grid_z = np.flip(grid_z, axis=1)
    mask = np.flip(mask, axis=1)
  if dy < 0:
    dy = abs(dy)
    y0 -= dy * y_count
    grid_z = np.flip(grid_z, axis=0)
    mask = np.flip(mask, axis=0)

  tensor_x = np.full((x_count,), dx)
  tensor_y = np.full((y_count,), dy)

  elevation = grid_z.flatten()

  # Export the grid mask as the visibility project.
  visibility_data = omf.ScalarData(
    name="visibility",
    description="1 indicates point is visible, 0 indicates invisible",
    location="vertices",
    array=mask.flatten())

  geometry = omf.SurfaceGridGeometry(
    axis_u=axis_u,
    axis_v=axis_v,
    origin=[x0, y0, z0],
    tensor_u=tensor_x,
    tensor_v=tensor_y,
    offset_w=elevation,
  )

  grid_element = omf.SurfaceElement(
    name=name,
    description="",
    geometry=geometry,
    data=[visibility_data])

  return [grid_element]


def surface_to_omf(surface_path):
  """Converts a Vulcan triangulation file (00t) into an OMF element.

  Parameters
  ----------
  surface_path : str
    Path to the Vulcan triangulation file to export.

  Returns
  -------
  list
    List of omf.SurfaceElement containing a single item representing
    the exported triangulation.
  """
  surface = vulcan.triangulation(surface_path, "r")
  points = surface.get_vertices()
  facets = surface.get_faces()

  surface_geometry = omf.SurfaceGeometry(
    vertices=points,
    triangles=facets)

  name = pathlib.Path(surface_path).stem

  colour = "random"
  # If the surface uses RGB colours then use that colour.
  # If the surface uses a colour index in a scd file, the colour
  # is set randomly.
  if surface.is_rgb():
    colour = surface.get_rgb()
  else:
    print("Warning: Failed to set colour. Colours defined in scd files are "
          "not supported.")

  surface_element = omf.SurfaceElement(
    name=name,
    description="",
    geometry=surface_geometry,
    color=colour,
  )

  return [surface_element]


def _polyline_to_omf(polyline: vulcan.polyline):
  """Converts a Vulcan polyline into an OMF element.

  A vulcan Polyline can either be "unconnected" to represent
  a point set or "connected" to represent a line set.

  Parameters
  ----------
  polyline : vulcan.Polyline
    The Vulcan polyline to convert to an OMF element.

  Returns
  -------
  omf.LineSetElement or omf.PointSetElement
    The polyline converted a LineSetElement if the polyline is connected,
    otherwise the polyline converted to a PointSetElement.
  """
  # The edges of the polyline. If it is a pointset, this will remain empty.
  edges = []

  # If the polyline has per-point colours.
  has_per_point_colours = polyline.feature == "COLRGBPTS"
  # The extracted per-point colours. If the polyline has per-point colours,
  # this will be a list of (R, G, B) colour tuples.
  per_point_colours = []

  # Dictionary of parameters to pass to the OMF element.
  geometry_parameters = {
    "vertices" : polyline.get_coordinates()
  }

  # Dictionary of parameters to pass to the OMF element.
  element_parameters = {
    "name" : polyline.name,
    "description" : polyline.description,
    "data" : []
  }

  for i in range(polyline.num_points()):
    point = polyline.get_point(i)
    # A non-zero value for t indicates this point is connected to the
    # previous one. Skip i == 0 because the first point's t value has no
    # effect on the resulting line.
    if point.t and i > 0:
      edges.append([i - 1, i])
    if has_per_point_colours:
      colour_string = point.name
      try:
        colour = (
          int(colour_string[2:4], 16),
          int(colour_string[4:6], 16),
          int(colour_string[6:8], 16),
        )
        per_point_colours.append(colour)
      except (ValueError, IndexError):
        # If any per-point colour was invalid, log a warning and continue
        # as if there were no per-point colours.
        LOGGER.warning(
          f"Invalid colour string: '{colour_string}'. Ignoring per-point colours "
          f"for polyline: '{polyline.name}'")
        has_per_point_colours = False

  # Add the per-point colours if they were extracted.
  if has_per_point_colours:
    colour_data = omf.ColorData(
      name="point colours",
      location="vertices",
      array=per_point_colours,
    )
    element_parameters["data"].append(colour_data)

  # If the polyline is closed, the last point is connected to the first.
  if polyline.closed:
    edges.append([polyline.num_points() - 1, 0])

  # If there are edges, create a LineSetElement. Otherwise created a
  # PointSetElement.
  if edges:
    geometry_parameters["segments"] = edges
    line_geometry = omf.LineSetGeometry(**geometry_parameters)
    element_parameters["geometry"] = line_geometry
    omf_object = omf.LineSetElement(**element_parameters)
  else:
    point_geometry = omf.PointSetGeometry(**geometry_parameters)
    element_parameters["geometry"] = point_geometry
    omf_object = omf.PointSetElement(**element_parameters)

  return omf_object


def dgd_database_to_omf(dgd_path):
  """Converts all objects in a .dgd.isis file to OMF elements.

  Parameters
  ----------
  dgd_path : str
    Path to the dgd.isis database to export to OMF.

  Returns
  -------
  list of omf.LineSetElement or omf.PointSetElement
    List of all polylines in the dgd isis database converted to
    omf LineSetElement or PointSetElement.
  """
  results = []
  with vulcan.dgd(dgd_path, "r") as dgd:
    for layer_name in dgd.list_layers():
      layer = dgd.get_layer(layer_name)
      # This uses get_objects() instead of get_objects_enumerate() because
      # we do not need the index in the layer.
      # This call to get_objects is filtering the layer down to polylines.
      # It will skip vulcan.text, vulcan.text3d and other objects which can
      # be stored in a dgd database. Current these have no representation
      # in OMF, however in the future this may need to be expanded.
      for polyline in layer.get_objects((vulcan.polyline, )):
        pointset = _polyline_to_omf(polyline)
        results.append(pointset)
  return results


def vulcan_project_to_omf(project_path):
  """Converts all supported files in a directory to OMF elements.

  Note that a single file may result in multiple objects exported to the OMF
  file.

  Parameters
  ----------
  project_path : str
    Path to the Vulcan project directory to export to OMF or
    path to a dgd.isis, 00t or 00g file to export to OMF.

  Returns
  -------
  list
    List of OMF objects which were exported.

  Raises
  ------
  RuntimeError
    If project_path does not exist.
  """
  project = pathlib.Path(project_path)

  results = []

  # If the project path is a directory, iterate over all files in that
  # directory. Otherwise only use the specified file.
  if project.is_dir():
    items = project.iterdir()
  elif project.is_file():
    items = [project]
  else:
    raise RuntimeError(f"Failed to find file: {project_path}")

  for item in items:
    if item.suffix == ".isis":
      results.extend(dgd_database_to_omf(str(item)))
    elif item.suffix in triangulation_file_extensions:
      # Surfaces are 00t files, where the 0 can be any character.
      results.extend(surface_to_omf(str(item)))
    elif item.suffix in grid_file_extensions:
      # Grids are 00g files, where the 0 can be any character.
      results.extend(grid_to_omf(str(item)))
    else:
      # Unsupported file. Skip it.
      print(f"Skipping unsupported file: {item}")

  return results


def vulcan_files_to_omf_file(files, destination_path):
  """Exports the specified files to a single OMF file.

  This supports dgd.isis, 00t and 00g files. Other files are
  ignored.

  Unlike the other functions in this file, this exports the
  OMF objects to an OMF file.

  Parameters
  ----------
  files : list
    List of files to export to OMF.
  destination_path : str
    Path to the OMF file to export.

  Returns
  -------
  int
    The number of objects exported to the OMF file.

  """
  results = []
  for file in files:
    try:
      results.extend(vulcan_project_to_omf(file))
    except Exception as error:
      print(f"Failed to export '{file}' due to the following error: "
            f"'{error}'")

  destination_directory = os.path.dirname(destination_path)
  if destination_directory:
    os.makedirs(destination_directory, exist_ok=True)

  name = ""
  # If there is a single input file, the name is the filename with all
  # suffixes removed. This will loop twice in the case of dgd.isis databases
  # because they have two suffixes.
  if len(files) == 1:
    name = pathlib.Path(files[0])
    while name.suffix != "":
      name = pathlib.Path(name.stem)

  omf_project = omf.Project(
    name=str(name),
    description="This project was exported from data for Maptek Vulcan.")
  omf_project.elements = results
  omf_project.validate()
  omf.OMFWriter(omf_project, str(destination_path))

  return len(results)
