"""
Export OMF objects from a Maptek project. This converts the Maptek objects to
the corresponding to its OMF type.
"""

###############################################################################
#
# (C) Copyright 2021, Maptek Pty Ltd. All rights reserved.
#
###############################################################################
#
# Development notes
# -----------------
#
# Opened objects VS Object IDs
# The functions for converting from an MDF object to OMF element takes opened
# for read objects rather than an ObjectID. As overall its more beneficial to
# let the calling code open the object so it can then dispatch based on the
# type of the opened object as project.read() will have to do a type look-up
# anyway. It also means the caller is then repsonsible for dealing with if the
# object doesn't exist (because they are repsonsbile for starting the read).
#
# Origin
# The origin of the data to date is always (0, 0, 0).
# TODO: It has not been decided yet how to handle the origin property.
#
###############################################################################

import dataclasses
import logging
import os
import typing

from mapteksdk.data.colourmaps import NumericColourMap, StringColourMap

from mapteksdk.project import Project
from mapteksdk.data import (EdgeNetwork, PointSet, Polygon, Polyline, ObjectID,
                            Surface, GridSurface, VisualContainer)
from mapteksdk.data.edges import Edge
from mapteksdk.data.images import (Raster, RasterRegistrationMultiPoint,
                                   RasterRegistrationNone,
                                   RasterRegistrationTwoPoint)
from mapteksdk.data.primitives.primitive_attributes import (
    PrimitiveAttributes, PrimitiveType)

import numpy as np
import omf
import png


LOGGER = logging.getLogger('maptekomf')

# As a fallback when the MDF object has no colour the following colour is used.
DEFAULT_COLOUR = (0, 255, 0)


@dataclasses.dataclass
class ExportResult:
    """Represents the result of exporting an object to an OMF file.

    Containers will not be represented as their own export result.
    """

    source: ObjectID
    """The object that was to be exported to OMF."""

    source_path: str
    """The path of the object to be exported to OMF."""

    error: typing.Optional[Exception] = None
    """The error which caused the import of this object to fail.
    This will be None if the import was successfully.
    """

    # This could include either the OMF ID or the name in the resulting
    # OMF file (assuming we don't just use name from source_path). This really
    # depends on how we want to support containers.

    @property
    def success(self):
        """Was the export of the object successful?"""
        return not self.error


class UnsupportedByOpenMiningFormat(ValueError):
    """Raised when attempting to export an object which cannot be represented
    in OMF.

    This error will not be raised if only part of an object can't be exported,
    for example if the colours are translucent.
    """


def edge_network_to_omf(project: Project,
                        edge_network: EdgeNetwork) -> omf.LineSetElement:
    """Convert an edge network to a line set element in OMF.

    Raises
    ------
    UnsupportedByOpenMiningFormat
        If the edge network has no edges.
    """
    LOGGER.debug('Exporting edge network %s', edge_network.id)

    if edge_network.edge_count == 0:
        raise UnsupportedByOpenMiningFormat(
            f'Unable to export an edge network {edge_network.id.name} '
            'because OMF requires line sets to contain at least one edge.')

    element = omf.LineSetElement()
    element.name = edge_network.id.name
    element.subtype = 'line'

    # OMF doesn't allow us to set these properties. So for it to be date
    # modified to really work well, we would need to make it so exporting to
    # an existing project actually modifies the object.
    #
    # element.date_created = polygon.created_date
    # element.date_modified = polygon.modified_date

    # TODO: Consider producing an origin for the data that isn't (0, 0 ,0).
    element.geometry = omf.LineSetGeometry()
    element.geometry.vertices = edge_network.points
    element.geometry.segments = edge_network.edges

    # No special handling for the fact it loops is required as edges already
    # contains the edge going from the last point to first and OMF doesn't
    # have any property to confirm its intended as a polygon.

    _handle_point_colour_to_omf(edge_network, element)
    _handle_edge_colour_to_omf(edge_network, element)

    # Handle point and edge attributes
    element.data.extend(
        _attributes_to_omf(project, edge_network.point_attributes))
    element.data.extend(
        _attributes_to_omf(project, edge_network.edge_attributes))

    # TODO: Confirm that OMF doesn't support attributes per-object (i.e single
    # values, not per-vertice or segment etc)

    return element


def point_set_to_omf(project: Project,
                     point_set: PointSet) -> omf.PointSetElement:
    """Convert a point set to a point set element in OMF."""
    LOGGER.debug('Exporting point set %s', point_set.id)

    element = omf.PointSetElement()
    element.name = point_set.id.name
    element.subtype = 'point'

    # TODO: Consider producing an origin for the data that isn't (0, 0 ,0).
    element.geometry = omf.PointSetGeometry()
    element.geometry.vertices = point_set.points

    _handle_point_colour_to_omf(point_set, element)

    element.data.extend(
        _attributes_to_omf(project, point_set.point_attributes))

    # TODO: Confirm that OMF doesn't support attributes per-object (i.e single
    # values, not per-vertice or segment etc)

    return element


def polygon_to_omf(project: Project,
                   polygon: Polygon) -> omf.LineSetElement:
    """Convert a polygon (edge loop) to a line set element22 in OMF."""
    LOGGER.debug('Exporting polygon %s', polygon.id)

    element = omf.LineSetElement()
    element.name = polygon.id.name
    element.subtype = 'line'

    # OMF doesn't allow us to set these properties. So for it to be date
    # modified to really work well, we would need to make it so exporting to
    # an existing project actually modifies the object.
    #
    # element.date_created = polygon.created_date
    # element.date_modified = polygon.modified_date

    # TODO: Consider producing an origin for the data that isn't (0, 0 ,0).
    element.geometry = omf.LineSetGeometry()
    element.geometry.vertices = polygon.points
    element.geometry.segments = polygon.edges

    # No special handling for the fact it loops is required as edges already
    # contains the edge going from the last point to first and OMF doesn't
    # have any property to confirm its intended as a polygon.

    _handle_point_colour_to_omf(polygon, element)
    _handle_edge_colour_to_omf(polygon, element)

    # Handle point and edge attributes
    element.data.extend(_attributes_to_omf(project, polygon.point_attributes))
    element.data.extend(_attributes_to_omf(project, polygon.edge_attributes))

    # TODO: Confirm that OMF doesn't support attributes per-object (i.e single
    # values, not per-vertice or segment etc)

    return element


def polyline_to_omf(project: Project,
                    polyline: Polyline) -> omf.LineSetElement:
    """Convert a polyline (edge chain) to a line set element in OMF."""
    LOGGER.debug('Exporting polyline %s', polyline.id)

    element = omf.LineSetElement()
    element.name = polyline.id.name
    element.subtype = 'line'

    # OMF doesn't allow us to set these properties. So for it to be date
    # modified to really work well, we would need to make it so exporting to
    # an existing project actually modifies the object.
    #
    # element.date_created = polyline.created_date
    # element.date_modified = polyline.modified_date

    # TODO: Consider producing an origin for the data that isn't (0, 0 ,0).
    element.geometry = omf.LineSetGeometry()
    element.geometry.vertices = polyline.points
    element.geometry.segments = polyline.edges

    _handle_point_colour_to_omf(polyline, element)
    _handle_edge_colour_to_omf(polyline, element)

    # Handle point and edge attributes
    element.data.extend(_attributes_to_omf(project, polyline.point_attributes))
    element.data.extend(_attributes_to_omf(project, polyline.edge_attributes))

    # TODO: Confirm that OMF doesn't support attributes per-object (i.e single
    # values, not per-vertice or segment etc)

    return element


def surface_to_omf(project: Project, surface: Surface) -> omf.SurfaceElement:
    """Convert a surface (triangulation) to a surface element in OMF."""
    LOGGER.debug('Exporting surface %s', surface.id)

    element = omf.SurfaceElement()
    element.name = surface.id.name
    element.subtype = 'surface'

    element.geometry = omf.SurfaceGeometry()
    element.geometry.vertices = surface.points
    element.geometry.triangles = surface.facets

    _handle_point_colour_to_omf(surface, element)
    # BUG: The edge colours are seemingly returning uninitialised values. This
    # is being tracked by the Maptek development team in issue SDK-558.
    # _handle_edge_colour_to_omf(surface, element)
    _handle_facet_colour_to_omf(surface, element)

    # Handle point and edge attributes
    element.data.extend(_attributes_to_omf(project, surface.point_attributes))
    element.data.extend(_attributes_to_omf(project, surface.edge_attributes))
    element.data.extend(_attributes_to_omf(project, surface.facet_attributes))

    # Handle applying textures to the surface element from the rasters
    # associated with the surface.
    if surface.rasters:
        textures = []
        for raster in surface.rasters.values():
            with project.read(raster) as raster_reader:
                texture = _raster_to_omf(raster_reader)
                if texture:
                    textures.append(texture)
        element.textures = textures

    # TODO: Confirm that OMF doesn't support attributes per-object (i.e single
    # values, not per-vertice or segment etc)

    return element


def grid_surface_to_omf(project: Project,
                        surface: GridSurface) -> omf.SurfaceElement:
    """Convert a grid surface to a surface element in OMF.

    There will be limitations as a grid in OMF is not as general as a
    GridSurface in a Maptek project.

    Raises
    ------
    UnsupportedByOpenMiningFormat
        If the GridSurface has spacing that does not form a general
        rectilinear grid.
    """
    LOGGER.debug('Exporting grid surface %s', surface.id)

    if surface.major_dimension_count == 0 or \
            surface.minor_dimension_count == 0:

        raise ValueError('Can not export given GridSurface because it is '
                         'empty.')

    def compute_spacing(points):
        spacing = np.diff(points[:, :2], axis=0)
        return np.linalg.norm(spacing, axis=1)

    # Determine the spacing between columns.
    spacing_major = compute_spacing(surface.cell_points[0])

    # Every subsequent row must contain the same spacing between points as the
    # the first row.
    if not all(
            np.allclose(compute_spacing(surface.cell_points[row]),
                        spacing_major)
            for row in range(1, surface.major_dimension_count)):
        raise UnsupportedByOpenMiningFormat(
            'GridSurface can\'t be exported to OMF. The spacing between '
            'points on different rows is different.')

    # Determine spacing between row.
    spacing_minor = compute_spacing(surface.cell_points[:, 0])

    # Every subsequent row must contain the same spacing between points as the
    # the first row.
    if not all(
            np.allclose(compute_spacing(surface.cell_points[:, column]),
                        spacing_minor)
            for column in range(1, surface.minor_dimension_count)):
        raise UnsupportedByOpenMiningFormat(
            'GridSurface can\'t be exported to OMF. The spacing between '
            'points on different columns is different.')

    element = omf.SurfaceElement()
    element.name = surface.id.name
    element.subtype = 'surface'

    element.geometry = omf.SurfaceGridGeometry()
    element.geometry.tensor_u = spacing_major
    element.geometry.tensor_v = spacing_minor
    element.geometry.offset_w = surface.point_z

    origin_x, origin_y, _ = surface.cell_points[0][0]
    element.geometry.origin = (origin_x, origin_y, 0.0)

    # Account for the different orientation of the grid surface.
    #
    # This only accounts for the surface being rotated in the XY plane which
    # is also a limitation of the spacing calculations above.
    axis_u_2d = surface.cell_points[0][1][:2] - surface.cell_points[0][0][:2]
    axis_v_2d = surface.cell_points[1][0][:2] - surface.cell_points[0][0][:2]
    element.geometry.axis_u = (axis_u_2d[0], axis_u_2d[1], 0.0)
    element.geometry.axis_v = (axis_v_2d[0], axis_v_2d[1], 0.0)

    _handle_point_colour_to_omf(surface, element)

    # If some of the points are not visible, output an array to that effect.
    if np.count_nonzero(surface.point_visibility) != surface.point_count:
        visibility_data = omf.ScalarData(
            name="visibility",
            description="1 indicates point is visible, 0 indicates invisible",
            location="vertices",
            array=surface.point_visibility.astype(np.int64),
        )
        element.data.append(visibility_data)

    # Cell colour is not exposed from maptekomf.

    # Handle point attributes.
    element.data.extend(_attributes_to_omf(project, surface.point_attributes))

    # Surfaces in OMF can not have attributes for edges (known as segments in
    # OMF).

    # Handle cell attributes which will be reported to OMF as faces rather
    # than cells as 'cells' is not a valid location for data on surfaces in
    # OMF.
    def cell_to_facet(attribute):
        """Converts the given attribute from 'cells' to 'faces'."""
        if attribute.location == 'cells':
            attribute.location = 'faces'
        return attribute

    element.data.extend(
        cell_to_facet(attribute)
        for attribute in _attributes_to_omf(project, surface.cell_attributes))

    # At the time of writing GridSurface can't have rasters (textures) applied
    # to them.

    # TODO: Confirm that OMF doesn't support attributes per-object (i.e single
    # values, not per-vertice or segment etc)

    return element


def object_to_omf(project: Project,
                  object_to_convert: ObjectID) -> omf.base.ProjectElement:
    """Convert the given object as specified by the ID to a project element in
    in OMF."""

    # This handles the polymorphism of reading an object to match it to the
    # corresponding conversion function.

    types_and_functions = [
        (EdgeNetwork, edge_network_to_omf),
        (PointSet, point_set_to_omf),
        (Polyline, polyline_to_omf),
        (Polygon, polygon_to_omf),
        (Surface, surface_to_omf),
        (GridSurface, grid_surface_to_omf),
    ]

    with project.read(object_to_convert) as maptek_object:
        for object_type, function in types_and_functions:
            if isinstance(maptek_object, object_type):
                return function(project, maptek_object)

        raise NotImplementedError(
            'This type (%s) of object is not yet supported' %
            object_to_convert.type_name)


def objects_to_omf(project: Project, objects: list, omf_path: str):
    """Converts the objects in the project to an OMF project at omf_path.

    Parameters
    ----------
    project:
        The Maptek project that contains the given objects.

    objects
        The list of object IDs or paths to export. Providing the path to a
        container will not export all the objects in that container.

    omf_path
        The path to write out the resulting OMF project file.

    Raises
    ------
    ValueError
        If project is None, even if objects is empty.

    Returns
    -------
    list
        A list of ExportResult objects which state if there was a problem
        exporting it. The ExportResult does not contain information about
        individual parts of the object which weren't handled (like visibility
        or selection).
    """
    LOGGER.debug('Exporting objects: %r to %s', objects, omf_path)

    if not project:
        raise ValueError('No project was provided.')

    def resolve_to_object_id(value):
        if isinstance(value, ObjectID):
            return value

        return project.find_object(value)

    objects_to_export = [resolve_to_object_id(obj) for obj in objects]

    results = []

    # At this time, if an invalid path is given then the object is simply
    # ignored and the rest of them will be exported. Useability wise it would
    # make it harder if it was simply a typo of the path as all the other
    # objects would have been exported.

    invalid_paths = [
        source
        for source, object_id in zip(objects, objects_to_export)
        if not object_id
    ]

    if invalid_paths:
        for path in invalid_paths:
            results.append(ExportResult(
                None, path,
                ValueError('There is no object at this path.')))

        # Remove the invalid objects from the list to export.
        objects_to_export = [obj for obj in objects_to_export if obj]

    if not objects_to_export:
        return results

    omf_project = omf.Project(
        name=os.path.splitext(os.path.basename(omf_path))[0],
        description='This project was exported from data in a Maptek '
        'application.'
    )

    results.extend(
        _add_objects_to_omf_project(project, objects_to_export, omf_project))

    omf_project.validate()

    omf.OMFWriter(omf_project, omf_path)

    return results


def _add_objects_to_omf_project(project: Project,
                                objects: list,  # Of object IDS
                                omf_project: omf.Project):
    """Converts the objects in the project to the OMF equivalent and add them
    to the given OMF Project.

    Returns
    -------
    list
        A list of ExportResult objects which state if there was a problem
        exporting it. The ExportResult does not contain information about
        individual parts of the object which weren't handled (like visibility
        or selection).
    """

    results = []

    for object_to_convert in objects:
        if object_to_convert.is_a(VisualContainer):
            results.extend(_add_objects_to_omf_project(
                project,
                project.get_children(object_to_convert).ids(),
                omf_project))
        else:
            object_path = object_to_convert.path

            try:
                element = object_to_omf(project, object_to_convert)
                omf_project.elements.append(element)
                results.append(ExportResult(source=object_to_convert,
                                            source_path=object_path))
            except UnsupportedByOpenMiningFormat as error:
                results.append(ExportResult(
                    source=object_to_convert,
                    source_path=object_path,
                    error=error))
            except NotImplementedError as error:
                results.append(ExportResult(
                    source=object_to_convert,
                    source_path=object_path,
                    error=error))

    return results


def _attributes_to_omf(project: Project,
                       primitive_attributes: PrimitiveAttributes):
    """Converts the primitive attributes from an object in a Maptek project to
    attributes in OMF.

    The location of the attributes in OMF is derived from primitive the
    attributes is from.
    """

    primitive_type_to_location = {
        PrimitiveType.POINT: 'vertices',
        PrimitiveType.EDGE: 'segments',
        PrimitiveType.FACET: 'faces',
        PrimitiveType.CELL: 'cells',
    }

    def string_colour_map_to_omf(project: Project,
                                 colour_map_id,
                                 attribute_name):
        """Convert a string colour map from a Maptek project to the nearest
        equivalent in OMF, which is two legends of string and colours.

        This can be used with MappedData to provide a mapping of indices
        to the strings/colours.
        """
        if not colour_map_id.is_a(StringColourMap):
            raise TypeError('Expected colour map to be a string colour map.')

        strings = omf.StringArray()
        colours = omf.ColorArray()

        with project.read(colour_map_id) as colour_map:
            colour_map: StringColourMap

            if np.any(colour_map.colours[:, 3] != 255):
                LOGGER.warning('The alpha for the colours for attribute %s '
                               'will be lost. OMF only supports RGB.',
                               attribute_name)

            strings.array[:] = colour_map.legend
            colours.array = colour_map.colours[:, :3].tolist()

        # String colour maps end up being represented as a list of strings
        # and a list of colours, each list is called a legend.
        omf_legends = [omf.Legend(), omf.Legend()]
        omf_legends[0].values = strings
        omf_legends[1].values = colours
        return omf_legends

    def attribute_to_omf(attribute_name, attribute_values, location,
                         colour_map_id):
        # Per-primitive attributes in a Maptek project can not be datetime
        # 3D-vector, 2D-vector or a pair of integers, as of August 2021.
        if np.issubdtype(attribute_values.dtype, str):
            if colour_map_id:
                omf_attribute = omf.MappedData()
                omf_attribute.legends = string_colour_map_to_omf(
                    project, colour_map_id, attribute_name)

                # The array will be the indices of the string in the
                # colour map legend.
                string_keys = omf_attribute.legends[0].values.array

                omf_attribute.array = [
                    string_keys.index(value) for value in attribute_values
                ]
            else:
                omf_attribute = omf.StringData()
                # OMF's string array doesn't accept a numpy array of strings.
                attribute_values = list(attribute_values)
        else:
            omf_attribute = omf.ScalarData()

        omf_attribute.name = attribute_name
        omf_attribute.description = ''
        omf_attribute.location = location

        if not omf_attribute.array:
            omf_attribute.array = attribute_values

        return omf_attribute

    location = primitive_type_to_location[primitive_attributes.primitive_type]

    attribute_with_colour_map = primitive_attributes.colour_map_attribute \
        if primitive_attributes.colour_map else ''

    omf_attributes = []
    for attribute_name in primitive_attributes.names:
        attribute_values = primitive_attributes[attribute_name]

        attribute_colour_map = primitive_attributes.colour_map \
            if attribute_name and attribute_name == attribute_with_colour_map \
            else None

        omf_attributes.append(
            attribute_to_omf(attribute_name, attribute_values, location,
                             attribute_colour_map))

    return omf_attributes


def _colour_array_to_omf(colour_array,
                         location: str,
                         element_name: str) -> omf.ColorData:
    """Converts a 2D ndarray of RGBA colours to an OMF colour data array.

    The alpha will be ignored as OMF only supports RGB. A warning will be
    logged.
    """
    if np.any(colour_array[:, 3] != 255):
        LOGGER.warning('The alpha for the colour of %s will be lost. '
                       'OMF only supports RGB.', element_name)

    omf_attribute = omf.ColorData()
    assert isinstance(omf_attribute, omf.base.ProjectElementData)

    if location == 'vertices':
        omf_attribute.name = 'point colours'
    elif location == 'segments':
        omf_attribute.name = 'edge colours'
    elif location == 'faces':
        omf_attribute.name = 'facet colours'
    elif location == 'cells':
        omf_attribute.name = 'cell colours'

    omf_attribute.description = ''
    omf_attribute.location = location
    omf_attribute.array = colour_array[:, :3]
    return omf_attribute


def _raster_to_omf(raster: Raster) -> omf.ImageTexture:
    """Convert a raster to a image texture element in OMF."""

    if isinstance(raster.registration, RasterRegistrationTwoPoint):
        registration = raster.registration
        registration: RasterRegistrationTwoPoint

        texture = omf.ImageTexture()
        texture.name = raster.title

        # OMF doesn't support mapping  within the image onto an object. It may
        # be possible for us to re-compute the world points (and thus the
        # origin for OMF) to essentially compute where the corners of the
        # image would be in world space. Alternatively, it may be possible to
        # use UVMappedTexture (in OMF 2.0) but that has its own limitations.
        #
        # This means OMF requires registration.image_points to be
        # two of (0, 0), (width, 0), (0, height) or
        # (width, height).

        # TODO: Account for the orientation of the image points and
        # the world points.
        texture.origin = registration.world_points[0]
        if np.allclose(registration.orientation, (0, 0, 1)):
            # This is suitable for when the texture was imported
            # from OMF. Some of the conditions are not checked.
            difference = registration.world_points[1] - \
                registration.world_points[0]
            texture.axis_u = (difference[0], 0, 0)
            texture.axis_v = (0, difference[1], 0)
        else:
            texture.axis_u = (1.0, 0.0, 0.0)
            texture.axis_v = (0.0, 1.0, 0.0)
            raise NotImplementedError(
                'Unhandled orientation for image registration '
                f'{registration.orientation}')

        # Maptek stores the image bottom to top so it needs to
        # be flipped here.
        texture.image = png.from_array(
            raster.pixels_2d[::-1].ravel().reshape((-1, raster.width * 4)),
            mode='RGBA',
            info={
                'height': raster.height,
                'width': raster.width,
            })
        if raster.title.endswith('.png'):
            texture.image.filename = raster.title
        else:
            texture.image.filename = raster.title + '.png'

        return texture
    elif isinstance(raster.registration, RasterRegistrationMultiPoint):
        LOGGER.warning("OMF doesn't support the multi-point registration.")
    elif isinstance(raster.registration, RasterRegistrationNone):
        LOGGER.warning("mapteksdk doesn't support the kind of registration "
                       "applied. Skipping texture.")
    else:
        LOGGER.warning("Unsupported type of registration %s",
                       raster.registration.__class__.__qualname__)

    return None


def _handle_point_colour_to_omf(points_object,
                                omf_element: omf.base.ProjectElement):
    """Handle converting the point colours of an object to OMF.

    The rule applied are as follows:
    - If there are no points, a default colour will be set.
    - If all the points have the same colour, then this will set the
      'color' property of the element.
    - If the points have different colours then this will create an attribute
        on the OMF element called "point colours' of type ColorArray.
    - If the colours has translucency applied i.e the alpha is not 255 then it
      will be ignored, as colours in OMF are RGB and not RGBA.
    """

    if points_object.point_count == 0:
        omf_element.color = DEFAULT_COLOUR
    else:
        first_colour = points_object.point_colours[0]
        has_uniform_colour = np.all(points_object.point_colours ==
                                    first_colour)
        if has_uniform_colour:
            if first_colour[-1] != 255:
                LOGGER.warning('The alpha for the colour of %s will be lost. '
                               'OMF only supports RGB.', omf_element.name)
            omf_element.color = tuple(int(v) for v in first_colour[:-1])
        else:
            omf_array = _colour_array_to_omf(points_object.point_colours,
                                             'vertices', omf_element.name)
            omf_element.data.append(omf_array)


def _handle_edge_colour_to_omf(edge_object: Edge,
                               omf_element: omf.base.ProjectElement):
    """Handle converting the edge colours of an object to OMF.

    The rule applied are as follows:
    - If there are no edges, then nothing happens. This assumes that the
      colour of the object will be based on the point colours.
    - If all the edges have the same colour, then this will set the
      'color' property of the element.
    - If the points have different colours then this will create an attribute
        on the OMF element called "point colours' of type ColorArray.
    - If the colours has translucency applied i.e the alpha is not 255 then it
      will be ignored, as colours in OMF are RGB and not RGBA.
    """

    # This behaviour is an approximation. There will be some cases where
    # exporting an object created in the software will work different as Python
    # makes some

    # If the edge count is zero, do nothing. Assume point colours will handle
    # it.

    if edge_object.edge_count > 0:
        first_colour = edge_object.edge_colours[0]
        has_uniform_colour = np.all(edge_object.edge_colours == first_colour)
        if has_uniform_colour:
            if first_colour[-1] != 255:
                LOGGER.warning('The alpha for the colour of %s will be lost. '
                               'OMF only supports RGB.', omf_element.name)
            omf_element.color = tuple(int(v) for v in first_colour[:-1])
        else:
            omf_array = _colour_array_to_omf(edge_object.edge_colours,
                                             'segments', omf_element.name)
            omf_element.data.append(omf_array)


def _handle_facet_colour_to_omf(facet_object,
                                omf_element: omf.base.ProjectElement):
    """Handle converting the facet colours of an object to OMF.

    The rule applied are as follows:
    - If there are no facets, then nothing happens. This assumes that the
      colour of the object will be based on the point colours.
    - If all the facets have the same colour, then this will set the
      'color' property of the element unless its equal to the default.
      This ensures setting the point_colours but not the facet_colours will use
      the point colours.
    - If the points have different colours then this will create an attribute
        on the OMF element called "point colours' of type ColorArray.
    - If the colours has translucency applied i.e the alpha is not 255 then it
      will be ignored, as colours in OMF are RGB and not RGBA.
    """

    # This behaviour is an approximation. There will be some cases where
    # exporting an object created in the software will work different as Python
    # makes some

    # If the facet count is zero, do nothing. Assume point colours will handle
    # it.
    if facet_object.facet_count > 0:
        first_colour = facet_object.facet_colours[0]
        has_uniform_colour = np.all(facet_object.facet_colours == first_colour)
        if has_uniform_colour:
            if first_colour[-1] != 255:
                LOGGER.warning('The alpha for the colour of %s will be lost. '
                               'OMF only supports RGB.', omf_element.name)

            # Only set the element colour if its not the default value.
            if not np.array_equal(first_colour, (0, 220, 0, 255)):
                omf_element.color = tuple(int(v) for v in first_colour[:-1])
        else:
            omf_array = _colour_array_to_omf(facet_object.facet_colours,
                                             'faces', omf_element.name)
            omf_element.data.append(omf_array)
