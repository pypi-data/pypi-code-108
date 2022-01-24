"""
Convert from OMF to Vulcan types and converts from Maptek types to OMF types.

TODO: Currently the OMF UID is a user visible object attribute. Reconsider if
this is suitable and make it a hidden attribute instead.
"""
###############################################################################
#
# (C) Copyright 2021, Maptek Pty Ltd. All rights reserved.
#
###############################################################################

import dataclasses
import datetime
import itertools
import logging
import typing

from mapteksdk.project import Project
from mapteksdk.data import (EdgeNetwork, NumericColourMap, PointSet,
                            Raster, RasterRegistrationTwoPoint,
                            StringColourMap, Surface, GridSurface, ObjectID)

from PIL import Image
import numpy as np

import omf

LOGGER = logging.getLogger('maptekomf')


@dataclasses.dataclass
class ImportResult:
    """Represents the result of the import of a single object from an OMF file.
    """

    source_name: str
    """The name of the object from the OMF project."""

    destination: typing.Optional[ObjectID] = None
    """The object ID of the imported object.
    This will be None if the import was unsuccessful.
    """

    destination_path: typing.Optional[str] = None
    """Path the object was imported to in the Project.
    This will be None if the import was unsuccessful.
    """

    error: typing.Optional[Exception] = None
    """The error which caused the import of this object to fail.
    This will be None if the import was a success.
    """

    fatal: bool = False
    """If the error was considered fatal and stopped the import.

    Otherwise if there was an error the object was skipped. There should only
    be one fatal error.
    """

    @property
    def success(self):
        """Was import of the object successful?"""
        assert bool(self.destination) == bool(self.destination_path)
        assert bool(self.destination) != bool(self.error)
        if self.fatal:
            assert not bool(self.destination), "It couldn't be fatal if it " \
                "was able ot import it"

        return bool(self.destination)


def santise_name(name):
    """Ensure a name is suitable to be a object name."""
    return name.replace('/', '_').replace('\\', '_').strip()


def omf_to_block_model(volume_element: omf.VolumeElement,
                       project: Project):
    """Convert a volume set element in OMF to a BlockModel."""
    LOGGER.debug('Importing block model %s', volume_element.name)

    LOGGER.info('Project contains an volume (called %s) which are not yet '
                'implemented.',
                volume_element.name)

    return volume_element.name, None


def omf_to_edge_network(line_set_element: omf.LineSetElement,
                        project: Project):
    """Convert a line set element in OMF to a EdgeNetwork."""
    LOGGER.debug('Importing edge network %s (sub type: %s)',
                 line_set_element.name, line_set_element.subtype)

    assert isinstance(line_set_element.geometry, omf.lineset.LineSetGeometry)
    points = line_set_element.geometry.vertices.array

    # Apply the origin transformation to the points.
    points += line_set_element.geometry.origin

    with project.new(None, EdgeNetwork) as edge_network:
        edge_network: EdgeNetwork
        edge_network.points = points
        edge_network.edges = line_set_element.geometry.segments.array

        red, green, blue = line_set_element.color
        edge_network.point_colours[:] = (red, green, blue, 255)

        # Handle object attributes.
        edge_network.set_attribute('OMF UID', str, str(line_set_element.uid))
        edge_network.set_attribute('OMF Date Created', datetime.datetime,
                                   line_set_element.date_created)
        edge_network.set_attribute('OMF Last Date Modified', datetime.datetime,
                                   line_set_element.date_modified)

        # Handle any point and edge attributes.
        for datum in line_set_element.data:
            if datum.location in ('vertices', 'segments'):
                _handle_attribute_in_omf(
                    datum, project, line_set_element.name, edge_network)
            else:
                # Edge networks sets only have vertices and segments.
                raise ValueError(
                    f'Unexpected location for data: {datum.location}')

    return line_set_element.name, edge_network.id


def omf_to_point_set(point_set_element: omf.PointSetElement, project: Project):
    """Convert a point set element in OMF to a PointSet object.

    Returns
    -------
    (str, ObjectId)
      The name of the object and its object ID.
      The resulting object does not have a path.
    """
    LOGGER.debug('Importing point set %s', point_set_element.name)

    assert isinstance(point_set_element.geometry,
                      omf.pointset.PointSetGeometry)
    points = point_set_element.geometry.vertices.array

    # Apply the origin transformation to the points.
    points += point_set_element.geometry.origin

    with project.new(None, PointSet) as point_set:
        point_set: PointSet
        point_set.points = points

        # Handle any point attributes.
        for datum in point_set_element.data:
            if datum.location == 'vertices':
                _handle_attribute_in_omf(
                    datum, project, point_set_element.name, point_set)
            else:
                # Point sets only have vertices no segments, faces or cells.
                raise ValueError(
                    f'Unexpected location for data: {datum.location}')

        # Handle object attributes.
        point_set.set_attribute('OMF UID', str, str(point_set_element.uid))
        point_set.set_attribute('OMF Date Created', datetime.datetime,
                                point_set_element.date_created)
        point_set.set_attribute('OMF Last Date Modified', datetime.datetime,
                                point_set_element.date_modified)

        # The description seems to to be typically left blank in OMF files.
        if point_set_element.description:
            point_set.set_attribute('Description', str,
                                    point_set_element.description)

        if point_set_element.subtype != 'point':
            point_set.set_attribute(
                'OMF Sub Type', str, point_set_element.subtype)

    return point_set_element.name, point_set.id


def omf_to_surface(surface_element: omf.SurfaceElement,
                   project: Project):
    """Convert a line set element in OMF to a Surface or GridSurface."""

    LOGGER.debug('Importing surface %s', surface_element.name)

    if isinstance(surface_element.geometry, omf.surface.SurfaceGridGeometry):
        return omf_to_grid_surface(surface_element, project)

    assert isinstance(surface_element.geometry, omf.surface.SurfaceGeometry)

    facets = surface_element.geometry.triangles.array
    points = surface_element.geometry.vertices.array

    # Apply the origin transformation to the points.
    points += surface_element.geometry.origin

    with project.new(None, Surface) as surface:
        surface: PointSet
        surface.points = points
        surface.facets = facets

        red, green, blue = surface_element.color
        surface.point_colours[:] = (red, green, blue, 255)

        # Handle object attributes.
        surface.set_attribute('OMF UID', str, str(surface_element.uid))
        surface.set_attribute('OMF Date Created', datetime.datetime,
                              surface_element.date_created)
        surface.set_attribute('OMF Last Date Modified', datetime.datetime,
                              surface_element.date_modified)

        # Handle textures.
        for texture in surface_element.textures:
            _handle_texture(texture, project, surface)

        # If there are any segment attributes the surface needs to be saved
        # first to generate the edges (segments).
        if any(datum.location == 'segments' for datum in surface_element.data):
            surface.save()

        # Handle primitive attributes.
        #
        # TODO: Warn if there there is more than one set of colour data for a
        # given location, as both can't be stored.
        for datum in surface_element.data:
            if datum.location in ('vertices', 'segments', 'faces'):
                _handle_attribute_in_omf(
                    datum, project, surface_element.name, surface)
            else:
                # Point sets only have vertices no segments, faces or cells.
                raise ValueError(
                    f'Unexpected location for data: {datum.location}')

    return surface_element.name, surface.id


def omf_to_grid_surface(surface_element: omf.SurfaceElement,
                        project: Project):
    """Convert a line set element in OMF to a Surface or GridSurface."""
    assert isinstance(surface_element.geometry,
                      omf.surface.SurfaceGridGeometry)

    major_dimension_count = len(surface_element.geometry.tensor_v) + 1
    minor_dimension_count = len(surface_element.geometry.tensor_u) + 1

    # The origin is applied later.
    x_coordinates = np.cumsum(surface_element.geometry.tensor_u)
    y_coordinates = np.cumsum(surface_element.geometry.tensor_v)
    x_coordinates = np.insert(x_coordinates, 0, 0)
    y_coordinates = np.insert(y_coordinates, 0, 0)

    x_coordinates_2d, y_coordinates_2d = np.meshgrid(
        x_coordinates, y_coordinates)

    rotation_matrix = np.array([
        surface_element.geometry.axis_u,
        surface_element.geometry.axis_v,
        np.cross(surface_element.geometry.axis_u,
                 surface_element.geometry.axis_v)])

    with project.new(None,
                     GridSurface(major_dimension_count=major_dimension_count,
                                 minor_dimension_count=minor_dimension_count)
                     ) as surface:
        surface: GridSurface
        surface.points[:, 0] = x_coordinates_2d.ravel()
        surface.points[:, 1] = y_coordinates_2d.ravel()
        surface.points[:, 2] = surface_element.geometry.offset_w

        # Apply the rotation.
        surface.points = surface.points.dot(rotation_matrix)

        # Apply the origin transformation to the points.
        surface.points += surface_element.geometry.origin

        red, green, blue = surface_element.color
        surface.point_colours[:] = (red, green, blue, 255)

        # Handle object attributes.
        surface.set_attribute('OMF UID', str, str(surface_element.uid))
        surface.set_attribute('OMF Date Created', datetime.datetime,
                              surface_element.date_created)
        surface.set_attribute('OMF Last Date Modified', datetime.datetime,
                              surface_element.date_modified)

        # Handle primitive attributes.
        #
        # TODO: Warn if there there is more than one set of colour data for a
        # given location, as both can't be stored.
        for datum in surface_element.data:
            # If the datum is faces then remap that to cells as the 'cells' in
            # a grid surface are still consided faces.
            if datum.location == 'faces':
                datum.location = 'cells'

            if datum.location == 'vertices' and datum.name == 'visibility':
                # Handle point visibility.
                mask = np.array(datum.array)
                if np.issubdtype(mask.dtype, np.integer):
                    surface.point_visibility = mask
                else:
                    LOGGER.warning(
                        "Found per-vertex 'visibility' attribute, but it was "
                        f"the wrong type. Given: {mask.dtype}, expected an "
                        "integer type such as numpy.int64.")
            elif datum.location in ('vertices', 'cells'):
                _handle_attribute_in_omf(
                    datum, project, surface_element.name, surface)
            else:
                # Point sets only have vertices no segments, faces or cells.
                raise ValueError(
                    f'Unexpected location for data: {datum.location}')

    LOGGER.info('Project contains an gridded surface (called %s) which are '
                'not yet implemented.',
                surface_element.name)

    return surface_element.name, surface.id


def omf_to_project(omf_project, project: Project, base_path: str,
                   overwrite: bool = False):
    """Convert all supported elements in an OMF project to a Maptek project.

    This will perform a best-effort approach to importing the project.
    If there is a type of element in the OMF project that is not supported it
    will be skipped.

    Parameters
    ----------
    omf_project:
      The OMF project or path to an OMF file.

    project
      The project where to write the objects out to.

    base_path
      The path in the project under which to add the objects to.

    overwrite
      If True, then any objects already in the Maptek project where the
      objects from the OMF project are to be imported to will be overwritten.
      If False then when there is already an object at its destination this
      function will stop and return with the last import result containing
      the details about it being overwritten.

    Raises
    ------
    ValueError
        If omf_project or project is None.
    ValueError:
        If there were violations of the OMF specification.
        For example, a point set which has attributes for faces (facets) which
        it can't have because it doesn't have faces to begin with.

    Returns
    -------
    list
        A list of ImportResult objects which state if there was a problem
        importing the object otherwise where the object was imported to.
        The ImportResult does not contain information about individual parts
        of the object that weren't handled.
    """

    if not omf_project:
        raise ValueError('No OMF project given.')

    if not project:
        raise ValueError('No Maptek project given.')

    if not isinstance(omf_project, omf.base.Project):
        # Assume that it is a path
        LOGGER.debug('Importing project from path %s', omf_project)

        omf_reader = omf.OMFReader(omf_project)
        omf_project = omf_reader.get_project()
    else:
        if omf_project.name:
            LOGGER.debug('Importing from project %s', omf_project.name)

    type_and_converter = [
        (omf.SurfaceElement, omf_to_surface),
        (omf.PointSetElement, omf_to_point_set),
        (omf.LineSetElement, omf_to_edge_network),
        (omf.VolumeElement, omf_to_block_model),
    ]

    def _find_converter(element):
        """Return none if it can't find a converter, that is to say element is
        not a supported type."""
        return next(
            (converter for element_type, converter in type_and_converter
             if isinstance(element, element_type)),
            None)

    # The name of objects in an OMF project are not required to be unique.
    # The names of objects in a given container in a Maptek project must be
    # unique.
    #
    # As a result during import if a duplicate name is detected an numerical
    # suffix will be added. This new name won't be the same as any other object
    # in the OMF project even if that object is not imported.

    # The set of all names of elements in the OMF project including names
    # of elements that won't be import into the project (lets consider those
    # as being reserved).
    all_names = set(santise_name(element.name)
                    for element in omf_project.elements)

    # Keep track of the names used so far with a mapping to next potential
    # suffix. This avoids having to test all numbers from 2 to last used
    # number each time.
    base_name_to_next_suffix = {}

    def determine_suitable_name(sanitised_name):
        """If the name has already been used a new name will be chosen to make
        it unique.

        The new name will not be the same as another element in the OMF project
        regardless of if it will be imported.
        """

        start_suffix = base_name_to_next_suffix.get(sanitised_name, None)
        if start_suffix is None:
            # The name has never been seen before.
            base_name_to_next_suffix[sanitised_name] = 2
        else:
            # Pick a new name.
            template = f'{sanitised_name} %d'
            for i in itertools.count(start_suffix):
                new_name = template % i
                if new_name not in all_names:
                    base_name_to_next_suffix[sanitised_name] = i + 1
                    return new_name

        return sanitised_name

    def unsupported_type_result(element):
        """Return an ImportResult that represents an unsupported type."""
        return ImportResult(
            source_name=element.name,
            error=NotImplementedError(
                f'OMF elements of type {type(element).__qualname__} are not '
                'supported. Please contact Maptek and provide the OMF file.'),
                )

    results = []

    for element in omf_project.elements:
        converter = _find_converter(element)

        if converter:
            try:
                name, object_id = converter(element, project)
            except NotImplementedError as error:
                results.append(ImportResult(source_name=element.name,
                                            error=error))

                # Still determine a suitable name so the name is reserved and
                # won't be used if there is a duplicate (within the OMF
                # project). This may leave gaps in the names.
                determine_suitable_name(santise_name(name))
                continue

            # There is no catch for ValueError because it is used to signify a
            # fatal error such as violations of OMF specification.

            name = determine_suitable_name(santise_name(name))
            if object_id:
                if base_path.endswith('/'):
                    destination_path = base_path + name
                else:
                    destination_path = base_path + '/' + name

                try:
                    project.add_object(destination_path, object_id,
                                       overwrite=overwrite)
                except ValueError as error:
                    results.append(ImportResult(source_name=name, error=error,
                                                fatal=True))

                    # An object would have been overwritten by the import. This
                    # is considered a fatal error, so it will stop processing
                    # other elements/objects.
                    #
                    # This will also apply if the base_path is invalid such as
                    # if attempting to import to a hidden containers.
                    return results

                results.append(ImportResult(
                    source_name=element.name,
                    destination=object_id,
                    destination_path=destination_path,
                ))
            else:
                results.append(unsupported_type_result(element))
        else:
            results.append(unsupported_type_result(element))
            LOGGER.info(
                'Project contains an unsupported element type called %s: %s',
                element.name,
                type(element).__qualname__)

    return results


def _handle_texture(texture: omf.texture.ImageTexture, project: Project,
                    surface: Surface):
    """Creates a raster object created from the texture and associates it with
    the surface."""

    name = (texture.name or texture.image.name or str(texture.uid))

    # Given a rectangular PNG image:
    # * The origin is the bottom left
    # * origin + axis_u is the bottom right
    # * origin + axis_v is the top left.

    LOGGER.info('Associating texture %s', name)
    with Image.open(texture.image) as image:

        image = image.convert("RGBA")

        # Flip the image, otherwise what should be the top of the image ends up
        # as the bottom.
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

        with project.new(None,
                         Raster(width=image.width,
                                height=image.height)) as raster:

            raster.pixels_2d = np.array(image)
            raster.title = name

            registration = RasterRegistrationTwoPoint()

            # The origin represents the bottom left of the image.
            # The image point for the bottom left of the image is (0, 0).

            registration.image_points = [(0, 0), (image.width, image.height)]
            registration.world_points = [
                texture.origin,
                texture.origin + texture.axis_u + texture.axis_v]
            registration.orientation = [0, 0, 1]

            surface.associate_raster(raster, registration)

    return raster.id


def _handle_mapped_data_in_omf(datum: omf.data.MappedData, project: Project,
                               object_name: str, maptek_object):
    """Handles MappedData in an OMF file and applies it to a Maptek object.

    Parameters
    ----------
    datum:
      The mapped data object from OMF.

    project:
      The Maptek project where the object is.

    object_name:
      The name of the object that the datum is from.

    maptek_object:
      The object in a Maptek project that has been open for edit.
    """

    # TODO: Santise this name to make sure its suitable for an attribute
    # name.
    attribute_name = datum.name or datum.description

    logger = LOGGER.getChild('attribute')
    logger.debug('Importing %s attributes of mapped data called %s on %s',
                 datum.location, attribute_name, object_name)

    # Maptek data format don't have a general facility for storing
    # indices (numbers) on a point and have it index into another thing
    # by-default. Technically, its doable but it will limit its use
    # without our applications.

    # Identify patterns in the data to translate it to our data.
    #
    # The first such pattern is if there are strings and colours then
    # that can be represented as a string colour map and the attribute
    # can be stored as strings.
    if (len(datum.legends) == 2 and
            isinstance(datum.legends[0].values, omf.data.StringArray) and
            isinstance(datum.legends[1].values, omf.data.ColorArray)):

        if (not datum.legends[0].values.array and
                not datum.legends[1].values.array):
            logger.warning(
                'Imported object %s had edge attributes called %s with a '
                'string colour map that has no values in it.', object_name,
                attribute_name)
            # This could still save the array of indices if needed, except they
            # might be all -1 in this case.
            return

        # Use a string colour map.
        legend_name = santise_name(datum.legends[0].name)
        with project.new(f'/legends/omf/{object_name}_{legend_name}',
                         StringColourMap,
                         overwrite=True) as string_colour_map:
            string_colour_map.legend = datum.legends[0].values.array
            string_colour_map.colours = datum.legends[1].values.array

        expanded_values = [
            datum.legends[0].values[index] for index in datum.array.array
        ]

        # Add the string values to the object and associate the colour map.
        if datum.location == 'vertices':
            maptek_object: PointSet
            maptek_object.point_attributes[attribute_name] = expanded_values
            maptek_object.point_attributes.set_colour_map(attribute_name,
                                                          string_colour_map.id)
        elif datum.location == 'segments':
            maptek_object.edge_attributes[attribute_name] = expanded_values
            # TODO: The following is not supported in the Python SDK.
            # maptek_object.edge_attributes.set_colour_map(
            #     attribute_name, string_colour_map.id)
            logger.warning(
                'Imported object %s had edge attributes called %s with a '
                'string colour map which cannot be set', object_name,
                attribute_name)
        elif datum.location == 'cells':
            maptek_object.cell_attributes[attribute_name] = expanded_values
            # TODO: The following is not supported in the Python SDK.
            # maptek_object.cell_attributes.set_colour_map(
            #     attribute_name, string_colour_map.id)
            logger.warning(
                'Imported object %s had cell attributes called %s with a '
                'string colour map which cannot be set', object_name,
                attribute_name)
        elif datum.location == 'faces':
            maptek_object.facet_attributes[attribute_name] = expanded_values
            # TODO: The following is not supported in the Python SDK.
            # maptek_object.facet_attributes.set_colour_map(
            #     attribute_name, string_colour_map.id)
            logger.warning(
                'Imported object %s had facet attributes called %s with a '
                'string colour map which cannot be set', object_name,
                attribute_name)
        else:
            raise NotImplementedError(
                f'Unsupported location: {datum.location} for {attribute_name} '
                f'on {object_name}')
    else:
        # In this situation we don't know what to expect and we haven't
        # attempted to try to guess or implement a very generic importer here.
        #
        # For example, it is possible this could handle mapped data that has
        # any number of string and scalar arrays.
        legend_types = [
          type(legend.values).__qualname__ for legend in datum.legends
        ]
        raise NotImplementedError(
          f'The object "{object_name}" has an attribute called '
          f'{attribute_name} on {datum.location} which is unrecognised by this '
          f'importer.\nIt is mapped data that consistents of {legend_types}.'
          'Please contact Maptek and provide the OMF file.')


def _handle_scalar_data_in_omf(datum: omf.data.ScalarData, project: Project,
                               object_name: str, maptek_object):
    """Handles ScalarData in an OMF file and applies it to a Maptek object.

    Parameters
    ----------
    datum:
      The mapped data object from OMF.

    project:
      The Maptek project where the object is.

    object_name:
      The name of the object that the datum is from.

    maptek_object:
      The object in a Maptek project that has been open for edit.

    Raises
    ------
    NotImplementedError
      If the datum has a colour map and it is not a ScalarColormap colour map.
    NotImplementedError
      If the datum is for a location that has not been handled.
    """

    # TODO: Santise this name to make sure its suitable for an attribute
    # name.
    attribute_name = datum.name or datum.description

    logger = LOGGER.getChild('attribute')
    logger.debug('Importing %s attributes of scalar data called %s on %s',
                 datum.location, attribute_name, object_name)

    maptek_colour_map = None

    if isinstance(datum.colormap, omf.data.ScalarColormap):
        minimum, maximum = datum.colormap.limits
        colour_count = len(datum.colormap.gradient)
        legend_name = santise_name(datum.colormap.name or datum.name)

        with project.new(f'/legends/omf/{object_name}_{legend_name}',
                         NumericColourMap,
                         overwrite=True) as numeric_colour_map:
            numeric_colour_map: NumericColourMap
            numeric_colour_map.ranges = np.linspace(minimum, maximum,
                                                    colour_count)
            numeric_colour_map.colours = datum.colormap.gradient.array
            maptek_colour_map = numeric_colour_map.id
    elif datum.colormap:
        raise NotImplementedError(
            'Scalar data with a colour map is not yet supported. Please '
            f'contact Maptek and provide the OMF file on {datum.location}.')

    if datum.location == 'vertices':
        maptek_object.point_attributes[attribute_name] = datum.array.array
        if maptek_colour_map:
            maptek_object.point_attributes.set_colour_map(attribute_name,
                                                          maptek_colour_map)
    elif datum.location == 'segments':
        maptek_object.edge_attributes[attribute_name] = datum.array.array
        if maptek_colour_map:
            # TODO: The following is not supported in the Python SDK.
            # maptek_object.edge_attributes.set_colour_map(attribute_name,
            #                                              maptek_colour_map)
            logger.warning('Imported object %s had edge attributes called %s '
                           'with a colour map', object_name, attribute_name)
    elif datum.location == 'faces':
        maptek_object.facet_attributes[attribute_name] = datum.array.array
        if maptek_colour_map:
            maptek_object.point_attributes.set_colour_map(attribute_name,
                                                          maptek_colour_map)
    elif datum.location == 'cells':
        maptek_object.cell_attributes[attribute_name] = datum.array.array
        if maptek_colour_map:
            logger.warning('Imported object %s had cell attributes called %s '
                           'with a colour map', object_name, attribute_name)
    else:
        raise NotImplementedError(
            f'Unsupported location: {datum.location} for {attribute_name} on '
            f'{object_name}')


def _handle_colour_data_in_omf(datum: omf.data.ColorData, project: Project,
                               object_name: str, maptek_object):
    """Handles ColorData in an OMF file and applies it to a Maptek object.

    If there is more than one set of colours for a given location then we can't
    have both as there is no where to put it. It would possibly need to be
    converted to a numerical attribute and a colour map.

    If there is more than one, it will currently use the last set of colours,
    with no warning.

    Parameters
    ----------
    datum:
      The mapped data object from OMF.

    project:
      The Maptek project where the object is.

    object_name:
      The name of the object that the datum is from.

    maptek_object:
      The object in a Maptek project that has been open for edit.

    Raises
    ------
    NotImplementedError
      If the datum is for a location that has not been handled.
    """

    # TODO: Santise this name to make sure its suitable for an attribute
    # name.
    attribute_name = datum.name or datum.description

    logger = LOGGER.getChild('attribute')
    logger.debug('Importing %s attributes of colour data called %s on %s',
                 datum.location, attribute_name, object_name)

    if datum.location == 'vertices':
        maptek_object.point_colours = datum.array.array
    elif datum.location == 'segments':
        maptek_object.edge_colours = datum.array.array
    elif datum.location == 'faces':
        maptek_object.facet_colours = datum.array.array
    else:
        raise NotImplementedError(
            f'Unsupported location: {datum.location} for {attribute_name} on '
            f'{object_name}')


def _handle_string_data_in_omf(datum: omf.data.StringData, project: Project,
                               object_name: str, maptek_object):
    """Handles StringData in an OMF file and applies it to a Maptek object.

    Parameters
    ----------
    datum:
      The mapped data object from OMF.

    project:
      The Maptek project where the object is.

    object_name:
      The name of the object that the datum is from.

    maptek_object:
      The object in a Maptek project that has been open for edit.

    Raises
    ------
    NotImplementedError
      If the datum is for a location that has not been handled.
    """

    # TODO: Santise this name to make sure its suitable for an attribute
    # name.
    attribute_name = datum.name or datum.description

    logger = LOGGER.getChild('attribute')
    logger.debug('Importing %s attributes of string data called %s on %s',
                 datum.location, attribute_name, object_name)

    if datum.location == 'vertices':
        maptek_object.point_attributes[attribute_name] = datum.array.array
    elif datum.location == 'segments':
        maptek_object.edge_attributes[attribute_name] = datum.array.array
    elif datum.location == 'faces':
        maptek_object.facet_attributes[attribute_name] = datum.array.array
    elif datum.location == 'cells':
        maptek_object.cell_attributes[attribute_name] = datum.array.array
    else:
        raise NotImplementedError(
            f'Unsupported location: {datum.location} for {attribute_name} on '
            f'{object_name}')


def _handle_attribute_in_omf(datum: omf.data.ProjectElementData,
                             project: Project, object_name: str,
                             maptek_object):
    """Handles converting the datum for an element in an OMF file to a
    correpsonding attribute in a a Maptek object.

    Parameters
    ----------
    datum:
      The data that represents an attribute for the object from OMF.

    project:
      The Maptek project where the object is.

    object_name:
      The name of the object that the datum is from.

    maptek_object:
      The object in a Maptek project that has been open for edit.


    Raises
    ------
    NotImplementedError
      If the datum is for a location that has not been handled.
    NotImplementedError
      If the datum has a colour map and it is not a ScalarColormap colour map.
    NotImplementedError
      If the datum is of a type that has not been handled.
    """

    if isinstance(datum, omf.data.MappedData):
        _handle_mapped_data_in_omf(datum, project, object_name, maptek_object)
    elif isinstance(datum, omf.data.ScalarData):
        _handle_scalar_data_in_omf(datum, project, object_name, maptek_object)
    elif isinstance(datum, omf.data.ColorData):
        _handle_colour_data_in_omf(datum, project, object_name, maptek_object)
    elif isinstance(datum, omf.data.StringData):
        _handle_string_data_in_omf(datum, project, object_name, maptek_object)
    else:
        location_to_primitive_type = {
            'vertices': 'point', 'segments': 'edge', 'faces': 'facet',
            'cells': 'cell',
        }
        primitive_type = location_to_primitive_type.get(
            datum.location, datum.location)
        raise NotImplementedError(
            f'Support for per-{primitive_type} attributes of type '
            f'{type(datum)} is not yet implemented. Please contact Maptek and '
            'provide the OMF file.')
