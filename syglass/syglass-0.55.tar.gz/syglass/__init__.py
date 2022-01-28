from enum import Enum
from typing import List, Iterable, Mapping, Dict, Tuple
from functools import wraps
import csv
import math
import numpy as np
import os
from . import pyglass


class Block:
    """
    Instances of this class represent blocks of volumetric image data. These
    blocks can be retrieved from ``Project`` objects using a number of
    functions such as ``get_block()`` and ``get_block_by_point().``

    ``Block`` objects have two fields: ``data`` and ``offset``. The ``data``
    field contains a 4D numpy array whose dimensions represent z, y, x, and
    channel respectively. The ``offset`` field is a 1D numpy array of length
    3 whose values represent the offset in voxels between the origin of the
    entire image volume and the origin of the block, where the origin is the
    bottom-left corner in either case.
    """

    def __init__(self, data, offset):
        self.data = data
        self.offset = offset


# A function decorator for making sure impl is not None
def _closed_project_decorator(func):
    @wraps(func)
    def project_checker(self, *args, **kwargs):
        if self.impl is None:
            raise ValueError("Project operation on a closed project.")
        return func(self, *args, **kwargs)
    return project_checker


class ProjectDataType(Enum):
    """
    Enum of the data types supported by syGlass. Calling `get_data_type()` on
    a `Project` will return one of these variants.
    """
    UINT8 = pyglass.UINT8
    UINT16 = pyglass.UINT16
    UINT32 = pyglass.UINT32
    FLOAT = pyglass.FLOAT
    HALF_FLOAT = pyglass.HALF_FLOAT


class Project:
    """
    Instances of this class represent syGlass projects. Instances can be
    created by calling ``syglass.get_project()`` with the string path to the
    project's ``.syg`` file.
    """

    def __init__(self, project_impl):
        self.impl = project_impl

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.impl = None
        return

    @_closed_project_decorator
    def get_name(self) -> str:
        """
        Returns the string name of the project.

        :return: the name of the project as a string
        """
        return self.impl.GetProjectName()

    @_closed_project_decorator
    def get_channel_count(self) -> int:
        """
        Returns the integer number of channels the project's volumetric data
        contains. The result can be assumed to be in the range [0, 4], as
        syGlass projects support at most 4 channels.

        :return: the integer number of channels in the project's volumetric
                 data
        """
        return self.impl.GetChannelCount()

    @_closed_project_decorator
    def get_data_type(self) -> ProjectDataType:
        """
        Returns a variant of the ProjectDataType enum describing the type of
        the project's volumetric data.

        :return: a ProjectDataType variant describing the type of the
                 project's volumetric data
        """
        return ProjectDataType(self.impl.GetDataType())

    @_closed_project_decorator
    def get_is_signed(self) -> bool:
        """
        Returns ``True`` if the project is signed, and ``False`` otherwise.
        Signed projects are immutable because they have been designated as
        read-only. Changes made to metadata and annotations of signed projects
        are reverted automatically when the last reference to the project is
        destroyed.

        :return: a boolean indicating whether the project is signed
        """
        return pyglass.IsProjectSigned(self.impl.GetPathToSygFile())

    @_closed_project_decorator
    def get_timepoint_count(self) -> int:
        """
        Returns the integer number of timepoints or frames in the project's
        volumetric data. For static volumes, this is always 1. For time-series
        data, it is always > 1.

        :return: the integer number of timepoints in the project's volumetric
                 data
        """
        return self.impl.GetFrameCount()

    @_closed_project_decorator
    def get_voxel_dimensions(self) -> np.ndarray:
        """
        Returns the physical dimensions of the voxels in the project's
        volumetric data as a numpy array. The returned array has length 3,
        with each element describing the z-, y-, and x-dimension respectively.
        The unit associated with these dimensions can be retrieved using
        ``get_voxel_unit()``.

        :return: the physical dimensions of the voxels in the project's
                 volumetric data
        """
        dimensions = self.impl.GetVoxelSize()
        return np.array([dimensions.z, dimensions.y, dimensions.x])

    @_closed_project_decorator
    def set_voxel_dimensions(self, voxel_dimensions: np.ndarray) -> None:
        """
        Sets the physical dimensions of the voxels in the project's volumetric
        data. A numpy array of length 3 should be passed to this function,
        with each element representing the z-, y-, and x-dimension
        respectively.

        :param voxel_dimensions: the new physical dimensions for the voxels in
                                 the project's volumetric data
        """
        voxel_dimensions = np.array([voxel_dimensions[2], voxel_dimensions[1], voxel_dimensions[0]])
        voxel_size = pyglass.vec3(*voxel_dimensions)
        self.impl.SetVoxelSize(voxel_size)

    @_closed_project_decorator
    def get_voxel_unit(self) -> str:
        """
        Gets a string describing the unit of the project's voxel dimensions,
        e.g. ``"nm"``.

        :return: a string describing the unit of the project's voxel dimensions
        """
        voxel_unit = self.impl.GetVoxelUnit()
        if voxel_unit == "??":
            return ""
        else:
            return voxel_unit

    @_closed_project_decorator
    def set_voxel_unit(self, voxel_unit: str) -> None:
        """
        Set the string description for the unit of the project's voxel
        dimensions, e.g. ``"nm"``.

        :param voxel_unit: a string description for the unit of the project's
                           voxel dimensions
        """
        self.impl.SetVoxelUnit(voxel_unit)

    @_closed_project_decorator
    def get_block_size(self) -> np.ndarray:
        """
        Returns the dimensions in voxels of one block of the project's
        volumetric data. The returned array has length 3, with each
        element describing the z-, y-, and x-dimension respectively.

        :return: the dimensions in voxels of one block of the project's
                 volumetric data
        """
        block_size = self.impl.GetBlockSize()
        return np.array([block_size.z, block_size.y, block_size.x])

    @_closed_project_decorator
    def get_mask(self, roi_index: int, experiment: str = "default") -> Block:
        """
        Returns a given mask of the project's volumetric data as a ``Block`` object.
        Currently does not support time series data and only supports 8 bit and 16 bit data types for now.

        :parameter roi_index: the index of which roi mask to be retreived 
        :parameter experiment: the name of the current experiment
        :return: the mask of the project's
                 volumetric data stored in a ``Block`` object
        """
        if roi_index < 0:
            raise ValueError(
                "ROI index " + str(roi_index) + " is not a valid ROI index."
            )

        roi_dims = self.get_roi_dimensions(roi_index, experiment)
        raster = self.impl.GetMaskRaster(experiment, pyglass.ivec3(int(roi_dims[2]), int(roi_dims[1]), int(roi_dims[0])), roi_index)
        offset = self.get_roi_offset(roi_index, experiment)
        return Block(pyglass.GetRasterAsNumpyArray(raster), offset)

    @_closed_project_decorator
    def import_mask(self, mask: np.ndarray, roi_index: int, experiment: str = "default") -> None:
        """
        Imports a mask containing less than 255 labels to apply to an ROI. 
        
        :parameter mask: a numpy array containing the mask labels for an ROI [z,y,x,channel count]
        :parameter roi_index: the index of which roi mask to be set
        :parameter experiment: the name of the current experiment
        """
        if roi_index < 0:
            raise ValueError(
                "ROI index " + str(roi_index) + " is not a valid ROI index."
            )

        if (mask.dtype != np.uint8 and mask.dtype != np.uint16 and mask.dtype != np.uint32 and
                mask.dtype != np.float32 and mask.dtype != np.float64):
            raise ValueError(
                "ROI data type " + str(mask.dtype) + " is not a valid ROI data type."
            )

        if mask.ndim != 4:
            raise ValueError(
                "The number of dimensions " + str(mask.ndim) + " is not valid. The mask dimensions must be (z,y,x,channel count)."
            )
        
        if mask.shape[3] > 4 or mask.shape[3] < 1:
            raise ValueError(
                "The number of channels " + str(mask.shape[3]) + " is not valid. The number of channels must be in the range (1, 4)."
            )

        raster = pyglass.GetRasterFromNumpyArray(mask)
        raster = self.impl.SetMaskRaster(raster, roi_index, experiment)

    @_closed_project_decorator
    def get_min_roi_point(self, roi_index: int, experiment: str = "default") -> np.ndarray:
        """
        Returns the minimum point of an ROI given its index. The coordinates of these 
        points are in voxels and their origin is with respect to the center of the volume. 
        
        :parameter roi_index: the index of which roi to be retreived 
        :parameter experiment: the name of the current experiment
        :return: the minimum point of the ROI as a numpy array [z,y,x]
        """
        if roi_index < 0:
            raise ValueError(
                "ROI Index " + str(roi_index) + " is not a valid ROI index."
            )

        pt = self.impl.GetMinROIPoint(experiment, roi_index)
        point = np.array([pt.z, pt.y, pt.x])
        return point 

    @_closed_project_decorator
    def get_max_roi_point(self, roi_index: int, experiment: str = "default") -> np.ndarray:
        """
        Returns the max point of an ROI given its index. The coordinates of these 
        points are in voxels and their origin is with respect to the center of the volume. 
        
        :parameter roi_index: the index of which roi to be retreived 
        :parameter experiment: the name of the current experiment
        :return: the max point of the ROI as a numpy array [z,y,x]
        """
        if roi_index < 0:
            raise ValueError(
                "ROI Index " + str(roi_index) + " is not a valid ROI index."
            )

        pt = self.impl.GetMaxROIPoint(experiment, roi_index)
        point = np.array([pt.z, pt.y, pt.x])
        return point 

    @_closed_project_decorator
    def get_roi_offset(self, roi_index: int, experiment: str = "default") -> np.ndarray:
        """
        Returns the offset in voxels of a ROI given its index. The ROI offset 
        is the distance from the bottom-left corner of the volume to 
        the bottom-left corner of the ROI.
        
        :parameter roi_index: the index of which ROI to be retreived 
        :parameter experiment: the name of the current experiment
        :return: the offset of the ROI as a numpy array [z,y,x]
        """
        if roi_index < 0:
            raise ValueError(
                "ROI Index " + str(roi_index) + " is not a valid ROI index."
            )

        dims = self.impl.GetProjectDimensions()
        volume = np.array([dims.z, dims.y, dims.x])
        volume /= self.get_voxel_dimensions()
        min_roi = self.get_min_roi_point(roi_index, experiment)
        roi_offset = min_roi.astype(int) + volume / 2
        return roi_offset

    @_closed_project_decorator
    def get_roi_dimensions(self, roi_index: int, experiment: str = "default") -> np.ndarray:
        """
        Returns the dimensions of an ROI given its index. 
        
        :parameter roi_index: the index of which roi to be retreived 
        :parameter experiment: the name of the current experiment
        :return: the dimensions of the ROI as a numpy array [z,y,x]
        """
        if roi_index < 0:
            raise ValueError(
                "ROI Index " + str(roi_index) + " is not a valid ROI index."
            )

        min_roi = self.get_min_roi_point(roi_index, experiment)
        max_roi = self.get_max_roi_point(roi_index, experiment)
        dims = self.impl.GetProjectDimensions()
        volume = np.array([dims.z, dims.y, dims.x])
        volume /= self.get_voxel_dimensions()
        min_off = min_roi.astype(int) + volume / 2 
        max_off = max_roi.astype(int) + volume / 2 
        roi_dimensions = np.array([int(abs(max_off[0] - min_off[0])), int(abs(max_off[1] - min_off[1])), int(abs(max_off[2] - min_off[2]))])
        return roi_dimensions

    @_closed_project_decorator
    def get_roi_data(self, roi_index: int, experiment: str = "default") -> Block:
        """
        Returns a given ROI of the project's volumetric data as a ``Block`` object.
        
        :parameter roi_index: the index of which ROI to be retreived 
        :parameter experiment: the name of the current experiment
        :return: the volumetric data of the ROI as a ``Block`` object
        """
        if roi_index < 0:
            raise ValueError(
                "ROI Index " + str(roi_index) + " is not a valid ROI index."
            )

        roi_offset = self.get_roi_offset(roi_index, experiment)
        roi_resolution = len(self.get_resolution_map()) - 1
        roi_dimensions = self.get_roi_dimensions(roi_index, experiment)
        roi_block = self.get_custom_block(0, roi_resolution, roi_offset, roi_dimensions)
        return roi_block

    @_closed_project_decorator
    def get_size(self, resolution_level: int) -> np.ndarray:
        """
        Returns the dimensions in voxels of the project's volumetric data at
        the given resolution. The returned array has length 3, with each
        element describing the z-, y-, and x-dimension respectively. To get
        the size of the smallest resolution level of the volume, pass 0 to
        this function. Larger values will query higher resolution levels. The
        highest resolution level in a project can be found by taking
        ``len(project.get_resolution_map()) - 1``.

        :parameter resolution_level: the target resolution level as an integer
        :return: the dimensions in voxels of the project's volumetric data at
                 the given resolution
        """
        tree_k = self.impl.GetTreeK()
        block_size = self.get_block_size()
        size = block_size * (2**resolution_level)
        
        if tree_k == 4:
            size[0] = block_size[0]
        return size

    @_closed_project_decorator
    def get_resolution_map(self) -> np.ndarray:
        """
        Returns a list of resolution levels and the number of blocks within
        each. The length of the returned list is the number of resolution
        levels in the project. The value at each resolution level is the
        number of blocks that resolution level contains.

        :return: a list of resolution levels and the number of blocks within
                 each
        """
        resolution_map = []
        tree_k = self.impl.GetTreeK()
        for level in range(self.impl.GetPyramidHeight() + 1):
            resolution_map.append(pow(tree_k, level))
        return np.asarray(resolution_map)

    @_closed_project_decorator
    def get_block_by_point(
        self, timepoint: int, resolution_level: int, point: np.ndarray
    ) -> Block:
        """
        Returns the block of the project's volumetric data that contains the
        given point as a ``Block`` object. The point passed to this function
        should be a numpy array of length three with elements representing
        the z, y, and x coordinates respectively. When using this function to
        query blocks containing annotation points from syGlass, always use
        the highest resolution level; the coordinates of these points are
        recorded with respect to the full resolution.

        :param timepoint: the timepoint from which to retrieve a block (0 for
                          static volumes)
        :param resolution_level: the resolution level from which to retrieve a
                                 block
        :param point: a numpy array of length 3 representing the target point
        :return: the block of the project's volumetric data that contains the
                 given point as a ``Block`` object
        """
        timepoint_count = self.get_timepoint_count()
        if timepoint > timepoint_count:
            raise ValueError(
                "Timepoint " + str(timepoint) + " greater than max timepoint."
            )

        pyramid_height = self.impl.GetPyramidHeight()
        if resolution_level > pyramid_height:
            raise ValueError(
                "Resolution level " + str(resolution_level) + " greater than max "
                "resolution level."
            )
        project_size = self.get_size(resolution_level)
        block_size = self.get_block_size()
        tree_k = self.impl.GetTreeK()
        log_tree_k = int(math.log(tree_k, 2))

        for i in range(3):
            if point[i] > project_size[i] or \
                    tree_k == 4 and point[i] > block_size[i]:
                raise ValueError("Point " + str(point) + " was outside of volume.")

        block_index_per_dimension = np.zeros(3)
        for i in range(3):
            block_index_per_dimension[i] = math.floor(
                point[i] / block_size[[i]])

        blocks_per_dimension = 2 ** resolution_level
        total_blocks_per_dimension = np.repeat(blocks_per_dimension, 3)
        if tree_k == 4:
            total_blocks_per_dimension[2] = 1

        index = 0
        for i in range(resolution_level - 1, -1, -1):
            for j in range(log_tree_k):
                half_max_index = total_blocks_per_dimension[j] / 2
                bit_mask = (tree_k ** i) * (2 ** (log_tree_k - 1 - j))
                if block_index_per_dimension[j] >= half_max_index:
                    block_index_per_dimension[j] -= half_max_index
                    index += bit_mask
                total_blocks_per_dimension[j] /= 2
        return self.get_block(timepoint, resolution_level, index)

    @_closed_project_decorator
    def get_custom_block(
        self,
        timepoint: int,
        resolution_level: int,
        offset: np.ndarray,
        dimensions: np.ndarray
    ) -> Block:
        """
        Returns a ``Block`` object of custom offset and dimensions.
        Rather than pulling a block directly from the syGlass project, this
        pulls as many blocks as necessary and stitches them together into a
        block fitting the given description. The offset and dimensions
        arguments should be 1D numpy arrays of length 3, with each element
        representing z, y, and x respectively.

        :param timepoint: the timepoint from which to retrieve a block (0 for
                          static volumes)
        :param resolution_level: the resolution level from which to retrieve a
                                 block
        :param offset: the distance from the bottom-left corner of the volume
                       to the bottom-left corner of the block
        :param dimensions: the desired dimensions for the block
        :return: a ``Block`` object of custom offset and dimensions
        """
        # TODO: handle (32bit float, float, half-float) data types
        custom_block_shape = (dimensions[0], dimensions[1], dimensions[2], self.get_channel_count())

        if self.get_data_type() == ProjectDataType.UINT16:
            custom_block = Block(
                np.zeros(custom_block_shape, dtype=np.uint16), offset)
        else:
            custom_block = Block(
                np.zeros(custom_block_shape, dtype=np.uint8), offset)

        block_size = self.get_block_size()

        z_range = int(math.floor(dimensions[0] / block_size[0])) + 2
        x_range = int(math.floor(dimensions[1] / block_size[1])) + 2
        y_range = int(math.floor(dimensions[2] / block_size[2])) + 2
        
        for z in range(z_range):
            for y in range(y_range):
                for x in range(x_range):
                    current_offset = np.copy(offset)
                    current_offset[0] += block_size[0] * z
                    current_offset[1] += block_size[1] * y
                    current_offset[2] += block_size[2] * x
                    
                    project_size = self.get_size(resolution_level)
                    if np.any(np.greater(current_offset, project_size)):
                        continue
                    
                    block = self.get_block_by_point(
                        timepoint, resolution_level, current_offset)
                    if np.shape(block.data) == (1, 1, 1):
                        continue

                    local_min = np.maximum(
                        (offset - block.offset).astype(int), np.zeros(3)
                    ).astype(int)

                    local_max = np.maximum(
                        np.minimum(
                            block_size,
                            offset + dimensions - block.offset
                        ),
                        np.zeros(3),
                    ).astype(int)

                    block_chunk = block.data[
                        local_min[0]: local_max[0],
                        local_min[1]: local_max[1],
                        local_min[2]: local_max[2], :]

                    block_shape = np.shape(block_chunk)

                    if block_chunk.size > 0:
                        place_min = np.maximum(
                            block.offset - offset, np.zeros(3)).astype(int)
                        custom_block.data[
                            place_min[0]:  place_min[0] + block_shape[0],
                            place_min[1]:  place_min[1] + block_shape[1],
                            place_min[2]:  place_min[2] + block_shape[2],
                            :] = block_chunk

        return custom_block

    @_closed_project_decorator
    def get_block(
        self, timepoint: int, resolution_level: int, index: int
    ) -> Block:
        """
        Returns a block of the project's volumetric data as a ``Block`` object.
        To ensure that the block index you pass to this function is valid, you
        may use the function ``get_resoultion_map()`` to get a list containing
        the number of blocks at each resolution level.

        :param timepoint: the timepoint from which to retrieve a block (0 for
                          static volumes)
        :param resolution_level: the resolution level from which to retrieve a
                                 block
        :param index: the index of the target block within the given
                      resolution level
        :return: a block of the project's volumetric data as a `Block` object
        """
        timepoint_count = self.get_timepoint_count()
        if timepoint > timepoint_count:
            raise ValueError(
                "Timepoint " + str(timepoint) + " greater than max timepoint."
            )

        pyramid_height = self.impl.GetPyramidHeight()
        if resolution_level > pyramid_height:
            raise ValueError(
                "Resolution level " + str(resolution_level) + " greater than max "
                "resolution level."
            )

        tree_k = self.impl.GetTreeK()
        if index >= tree_k ** pyramid_height:
            raise ValueError("Block index " + str(index) + " greater than max index.")

        index_offset = 0
        if resolution_level != 0:
            index_offset = (tree_k ** resolution_level - 1) // (tree_k - 1)
        final_index = index + index_offset

        raster = self.impl.GetBlock(timepoint, final_index, True)
        while not raster.Valid():
            raster = self.impl.GetBlock(timepoint, final_index, False)

        block_size = self.get_block_size()
        offset = np.zeros(3)
        for i in range(1, resolution_level + 1):
            resolutions_left = resolution_level - i

            offset_x_mask = 2 ** (resolutions_left * int(math.log(tree_k, 2)))
            if index & offset_x_mask == offset_x_mask:
                offset[2] += block_size[2] * 2 ** resolutions_left

            offset_y_mask = 2 * offset_x_mask
            if index & offset_y_mask == offset_y_mask:
                offset[1] += block_size[1] * 2 ** resolutions_left

            if tree_k == 8:
                offset_z_mask = 2 * offset_y_mask
                if index & offset_z_mask == offset_z_mask:
                    offset[0] += block_size[0] * 2 ** resolutions_left

        return Block(pyglass.GetRasterAsNumpyArray(raster), offset)

    @_closed_project_decorator
    def get_counting_points(
        self, experiment: str = "default"
    ) -> Dict[str, np.ndarray]:
        """
        Returns a dictionary containing all of the counting points associated
        with the given experiment. If no experiment is given, the default
        experiment is assumed. The dictionary has keys ``"Red"``, ``"Orange"``,
        ``"Yellow"``, ``"Green"``, ``"Cyan"``, ``"Blue"``, and ``"Violet"``,
        which map to numpy arrays containing zyx points. The coordinates of
        these points are in voxels and are relative to the highest resolution
        level.

        :param experiment: the name of the experiment from which to retrieve
                           counting points
        :return: a dictionary containing all of the experiment's counting
                 points, their locations, and their colors
        """
        count_map = {
            "Red": np.empty((0, 3)),
            "Orange": np.empty((0, 3)),
            "Yellow": np.empty((0, 3)),
            "Green": np.empty((0, 3)),
            "Cyan": np.empty((0, 3)),
            "Blue": np.empty((0, 3)),
            "Violet": np.empty((0, 3)),
        }
        blocks_per_dimension = math.pow(
            self.get_resolution_map()[self.impl.GetPyramidHeight()],
            1.0 / math.log(self.impl.GetTreeK(), 2.0)
        )

        self.impl.ExportCountCSV(experiment, "temp.csv")
        with open("temp.csv") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)  # Consume the header line
            for row in csv_reader:
                point = np.array([float(row[3]), float(row[2]), float(row[1])])
                point /= self.get_voxel_dimensions()
                point += self.get_block_size() * blocks_per_dimension / 2.0
                count_map[row[0]] = np.append(
                    count_map[row[0]], [point], axis=0
                )
        os.remove("temp.csv")
        return count_map

    @_closed_project_decorator
    def set_counting_points(
        self,
        counting_points: Mapping[str, np.ndarray],
        experiment: str = "default"
    ) -> None:
        """
        Takes a dictionary containing all of the counting points to be
        associated with the given experiment. If no experiment is given, the
        default experiment is assumed. The dictionary should have keys
        ``"Red"``, ``"Orange"``, ``"Yellow"``, ``"Green"``, ``"Cyan"``,
        ``"Blue"``, and ``"Violet"``, which map to numpy arrays containing zyx
        points. The coordinates of these points should be in voxels, relative
        to the highest resolution level.

        :param counting_points: a dictionary containing the location and color
                                of each counting point
        :param experiment: the name of the experiment from which to retrieve
                           counting points
        """
        blocks_per_dimension = math.pow(
            self.get_resolution_map()[self.impl.GetPyramidHeight()],
            1.0 / math.log(self.impl.GetTreeK(), 2.0)
        )

        with open("temp.csv", "w") as file:
            file.write("color,x,y,z\n")
            for color in counting_points:
                for point in counting_points[color]:
                    point -= self.get_block_size() * blocks_per_dimension / 2.0
                    point *= self.get_voxel_dimensions()
                    file.write("{},{x},{y},{z}\n".format(
                        color, x=point[2], y=point[1], z=point[0]
                    ))
        self.impl.ImportCountCSV(experiment, "temp.csv")
        os.remove("temp.csv")

    @_closed_project_decorator
    def get_distance_measurements(
        self, experiment: str = "default"
    ) -> np.array:
        """
        Returns a numpy array containing all distance measurements associated with the 
        given experiment. Each measurement is represented as a list of points. If no 
        experiment is given, the default experiment is assumed. The coordinates of these 
        points are in voxels and are relative to the highest resolution level.

        :param experiment: the name of the experiment from which to retrieve
                           counting points
        :return: a numpy array containing all of the experiment's lists of measurement
                 points
        """
        
        blocks_per_dimension = math.pow(
            self.get_resolution_map()[self.impl.GetPyramidHeight()],
            1.0 / math.log(self.impl.GetTreeK(), 2.0)
        )

        measurements = []
        self.impl.ExportMeasurementCSV(experiment, "temp.csv")
        with open("temp.csv") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)  # Consume the header line
            rowIndex = 0
            for row in csv_reader:
                row.remove(row[len(row)-1])
                rowlist = []
                for startIndex in range(int(len(row) / 3)):
                    tmpPoint = np.array([float(row[3*startIndex]), float(row[3*startIndex + 1]), float(row[3*startIndex + 2])])
                    tmpPoint /= self.get_voxel_dimensions()
                    tmpPoint += self.get_block_size() * blocks_per_dimension / 2.0
                    point = np.array([tmpPoint[2], tmpPoint[1], tmpPoint[0]])
                    rowlist.append(point)
                measurements.append(rowlist)
                rowIndex += 1
        os.remove("temp.csv")
        return np.array(measurements)

    @_closed_project_decorator
    def set_distance_measurements(
        self,
        measurement_points: np.ndarray,
        experiment: str = "default"
    ) -> None:
        """
        Takes a numpy array containing lists of points to be added to the project
        as measurements in the given experiment. Each list of points will define a
        distance measurement inside of syGlass. If no experiment is given, 
        the default experiment is assumed.

        :param measurement_points: a numpy array containing lists of x,y,z locations 
                                   for each measurement.
        :param experiment: the name of the experiment to associate measurement points with. 
        """

        blocks_per_dimension = math.pow(
            self.get_resolution_map()[self.impl.GetPyramidHeight()],
            1.0 / math.log(self.impl.GetTreeK(), 2.0)
        )

        with open("temp.csv", "w") as file:
            file.write("x1,y1,z1,...,xn,yn,zn\n")
            i_Outer = 0
            for measurement in measurement_points:
                i_Inner = 0
                for point in measurement:
                    point -= self.get_block_size() * blocks_per_dimension / 2.0
                    point *= self.get_voxel_dimensions()
                    if i_Inner == len(measurement) - 1 and i_Outer == len(measurement_points) - 1:
                        file.write("{x},{y},{z}".format(
                            x=point[2], y=point[1], z=point[0]
                        ))
                    elif i_Inner == len(measurement) - 1:
                        file.write("{x},{y},{z}\n".format(
                            x=point[2], y=point[1], z=point[0]
                        ))
                    else:
                        file.write("{x},{y},{z},".format(
                            x=point[2], y=point[1], z=point[0]
                        ))
                    i_Inner += 1
                i_Outer += 1
        
        self.impl.ImportMeasurementCSV(experiment, "temp.csv")
        os.remove("temp.csv")

    @_closed_project_decorator
    def get_multitracking_points(self, experiment: str = "default") -> Dict[str, list]:
        """
        Returns a dictionary containing all of the multi tracking points associated
        with the given experiment. If no experiment is given, the default
        experiment is assumed. The dictionary has keys ``"Red"``, ``"Orange"``,
        ``"Yellow"``, ``"Green"``, ``"Cyan"``, ``"Blue"``, and ``"Violet"``,
        The color keys map to lists containing [zyx points,frame number,series number]. The 
        coordinates of these points are in voxels and are relative to the highest 
        resolution level.

        :param experiment: the name of the experiment from which to retrieve
                           counting points
        :return: a dictionary containing all of the experiment's multi tracking
                 zyx points, their colors, their frame numbers, and 
                 their series number
        """
        blocks_per_dimension = math.pow(
            self.get_resolution_map()[self.impl.GetPyramidHeight()],
            1.0 / math.log(self.impl.GetTreeK(), 2.0)
        )

        count_map = {
            "Red": [],
            "Orange": [],
            "Yellow": [],
            "Green": [],
            "Cyan": [],
            "Blue": [],
            "Violet": [],
        }
        
        self.impl.ExportOnionSeriesCSV(experiment, "temp.csv")
        with open("temp.csv") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)  # Consume the header line
            for row in csv_reader:
                series = row[0]
                color = row[1]
                timepoint = row[2]
                point = np.array([float(row[5]), float(row[4]), float(row[3])])
                point /= self.get_voxel_dimensions()
                point += self.get_block_size() * blocks_per_dimension / 2.0

                count_map[color].append(np.array([point, int(timepoint), int(series)]))
        os.remove("temp.csv")
        return count_map

    @_closed_project_decorator
    def set_multitracking_points(
        self,
        multi_points: Mapping[str, list],
        experiment: str = "default"
    ) -> None:
        """
        Takes a dictionary containing all of the multitracking points to be
        associated with the given experiment. If no experiment is given, the
        default experiment is assumed. The dictionary should have keys
        ``"Red"``, ``"Orange"``, ``"Yellow"``, ``"Green"``, ``"Cyan"``,
        ``"Blue"``, and ``"Violet"``, which map to lists containing 
        [zyx points,frame number,series number].The coordinates of these points 
        should be in voxels, relative to the highest resolution level.

        :param multi_points: a dictionary containing zyx point, timepoint, 
                            series number and color of each multitracking point
        :param experiment: the name of the experiment from which to retrieve
                           multitracking points
        """
        blocks_per_dimension = math.pow(
            self.get_resolution_map()[self.impl.GetPyramidHeight()],
            1.0 / math.log(self.impl.GetTreeK(), 2.0)
        )

        with open("temp.csv", "w") as file:
            file.write("SERIES,COLOR,FRAME,X,Y,Z\n")
            for color in multi_points:
                for arr in multi_points[color]:
                    timepoint = arr[1]
                    series = arr[2]
                    point = arr[0]
                    point -= self.get_block_size() * blocks_per_dimension / 2.0
                    point *= self.get_voxel_dimensions()

                    file.write("{},{},{},{x},{y},{z}\n".format(
                        series, color, timepoint, x=point[2], y=point[1], z=point[0]
                    ))
        self.impl.ImportOnionSeriesCSV(experiment, "temp.csv")
        os.remove("temp.csv")

    @_closed_project_decorator
    def import_meshes(
        self, 
        list_of_OBJ_paths: List[str],
        experiment: str = "default"
    ) -> None:
        """
        Imports a collection of OBJ files into a project. 
        :param list_of_OBJ_paths: list of file paths, one for each OBJ file to import
        """
        l = [pyglass.path(strs.replace('\\','/')) for strs in list_of_OBJ_paths]
        return self.impl.ImportMeshOBJsSync(experiment, pyglass.PathList(l))

    @_closed_project_decorator
    def import_swcs(
        self,
        list_of_SWC_paths: List[str],
        experiment: str = "default"
    ) -> None:
        """
        Imports a collection of SWC files into a project. 
        :param list_of_SWC_paths: list of file paths, one for each SWC file to import
        """
        l = [strs.replace('\\','/') for strs in list_of_SWC_paths]
        return self.impl.ImportSkeletonSWC(experiment, pyglass.StringList(l))
        
    @_closed_project_decorator
    def save_tracings(
        self,
        experiment: str = "default",
        directory: str = "./",
        base_name: str = "output.swc"
    ) -> None:
        """
        Saves all of the tracings, in the SWC file format, to a directory.
        Read more about the SWC format here:
        http://research.mssm.edu/cnic/swc.html

        :param experiment: the name of the experiment from which to retrieve
                           counting points
        :param directory: path where the tracing files will be saved
        :return: a dictionary containing all of the experiment's counting
                 points, their locations, and their colors
        """
        self.impl.ExportSkeletonSWC(experiment, directory + base_name)

    @_closed_project_decorator
    def get_path_to_syg_file(self) -> str:
        """
        Returns the full path to the syg file of the current project.

        :return: the full path to the syg file
        """
        return self.impl.GetPathToSygFile()

    # Experiments
    @_closed_project_decorator
    def get_experiments(self) -> List[str]:
        """
        Returns a list of all the experiments in the current project.

        :return: a list containing all experiment names in the project
        """
        # TODO: Save the db in a variable?
        db = self.impl.GetDBAccessor()
        return list(db.GetDirectories())

    @_closed_project_decorator
    def get_current_experiment(self) -> str:
        """
        Gets the current active experiment.

        :return: the current experiment name
        """
        return self.impl.GetCurrentExperiment()

    @_closed_project_decorator
    def set_current_experiment(self, experiment: str = "default") -> None:
        """
        Sets the current active experiment.

        :param experiment: the name of the experiment to make active
        """
        if experiment not in self.get_experiments():
            raise ValueError("Experiment " + str(experiment) + " does not exist.")

        # TODO: change c++ so that this returns false if it didnt exist
        self.impl.SetExperiment(experiment)

    @_closed_project_decorator
    def add_new_experiment(self, experiment: str = "default") -> None:
        """
        Creates a new, empty experiment.

        :param experiment: the name of the newly made experiment
        """
        # TODO: Check for duplicates on c++ side
        self.impl.AddExperiment(experiment)

    @_closed_project_decorator
    def delete_experiment(self, experiment: str = "default") -> None:
        """
        Deletes the selected experiment.

        :param experiment: the name of the experiment to be deleted
        """
        # TODO: Move regenerating 'default' experiment to c++ side, or here
        self.impl.DeleteExperiment(experiment)

    @_closed_project_decorator
    def copy_experiment(self, source: str, destination: str) -> None:
        """
        Creates a copy of an existing experiment.

        :param source: the name of experiment to make a copy of
        :param destination: the name of the newly copied experiment
        """
        # TODO: Verify the names dont already exist on C++
        # and create the experiment on C++ or fix it so we dont need to create
        self.add_new_experiment(destination)
        # TODO: Raise errors when copy experiment returns false
        self.impl.CopyExperiment(source, destination)

    # Surface labels
    @_closed_project_decorator
    def get_labels(self, experiment: str = "default") -> List[str]:
        """
        Returns all the labels that exist in the given experiment

        :param experiment: the experiment from which to get the labels from
        :return: a list containing all labels in the experiment
        """
        return list(self.impl.GetTags(experiment))

    @_closed_project_decorator
    def create_label(
        self, label_name: str, experiment: str = "default"
    ) -> None:
        """
        Create a new label to apply to surfaces.

        :param label_name: the name of the new label
        :param experiment: the experiment in which to add the label to
        """
        self.impl.CreateTag(experiment, label_name)

    @_closed_project_decorator
    def delete_label(
        self, label_name: str, experiment: str = "default"
    ) -> None:
        """
        Delete a label, removing it from all surfaces that have it

        :param label_name: the name of the label to delete
        :param experiment: the experiment in which to delete the label from
        """
        # TODO: either iterate over the meshes and remove the label from them
        # here or do it on C++
        self.impl.DeleteTag(experiment, label_name)

    @_closed_project_decorator
    def add_label_to_surface(
        self, label_name: str, surface_name: str, experiment: str = "default"
    ) -> None:
        """
        Add a label to a surface.

        :param label_name: the name of the label to apply
        :param surface_name: the name of the surface to apply to label to
        :param experiment: the name of the experiment in which to apply the
                           label
        """
        self.impl.AddTagToMesh(experiment, label_name, surface_name)

    @_closed_project_decorator
    def remove_label_from_surface(
        self, label_name: str, surface_name: str, experiment: str = "default"
    ) -> None:
        """
        Remove a label from a surface

        :param label_name: the name of the label to remove
        :param surface_name: the name of the surface to remove to label from
        :param experiment: the name of the experiment in which to remove the
                           label
        """
        self.impl.RemoveTagFromMesh(experiment, label_name, surface_name)

    @_closed_project_decorator
    def get_surface_labels(
        self, surface_name: str, experiment: str = "default"
    ) -> List[str]:
        """
        Returns a list of all labels currently applied on a surface.

        :param surface_name: the name of the surface to get the labels of
        :param experiment: the name of the experiment in which the labels exist
        :return: a list containing all labels applied on the surface in the
                 experiment
        """
        return list(self.impl.GetMeshTags(experiment, surface_name))

    # Surfaces
    @_closed_project_decorator
    def get_surface_names_and_sizes(
        self, experiment: str = "default"
    ) -> Dict[str, Tuple[int, int]]:
        """
        Returns a dict of all the surface names mapping to their size. The size
        is represented as a tuple of two ints. The two ints are their vertices
        and faces respectively.

        :param experiment: the name of the experiment where the surfaces exist
        :return: a dict of surface names to vertices and faces count
        """
        return self.impl.GetMeshNamesAndSizes(experiment).asdict()

    @_closed_project_decorator
    def delete_surface(
        self, surface_name: str, experiment: str = "default"
    ) -> None:
        """
        Deletes a surface from an experiment

        :param surface_name: the name of the surface to delete
        :param experiment: the name of the experiment where the surface is
        """

        # TODO: check if it doesn't exist and maybe raise an error?
        self.impl.DeleteMeshByName(experiment, surface_name)

    @_closed_project_decorator
    def delete_all_surfaces(self, experiment: str = "default") -> None:
        """
        Deletes all surfaces in an experiment

        :param experiment: the experiment to delete all surfaces from
        """
        self.impl.DeleteAllMeshes(experiment)

    @_closed_project_decorator
    def set_surface_color(
        self,
        surface_name: str,
        color: Tuple[int, int, int, int],
        experiment: str = "default"
    ) -> None:
        """
        Sets the color of a surface.

        :param surface_name: the name of the surface to set the color of
        :param color: the color to set the surface represented as a 4-sized
                      tuple where the elements range from 0-255 and follow the
                      order r,g,b,a
        :param experiment: the name of the experiment where the surface is
        """
        color_argb = color[3] << 24  # a
        color_argb |= color[0] << 16  # r
        color_argb |= color[1] << 8   # g
        color_argb |= color[2] << 0   # b

        self.impl.SetMeshColor(experiment, surface_name, color_argb)

    @_closed_project_decorator
    def get_mesh_colors(
        self, experiment: str = "default"
    ) -> Dict[str, Tuple[int, int, int, int]]:
        """
        Returns a dict of all the surface names mapping to their colors. The
        colors are formatted as a 4 element tuple containing R,G,B,A values
        ranging from 0-255.

        :param experiment: the name of the experiment where the surfaces exist
        :return: a dict of surface names to rgba color values
        """
        mesh_colors = self.impl.GetMeshColors(experiment).asdict()
        for (name, color_argb) in mesh_colors.items():
            color_a = (color_argb & 0xff000000) >> 24
            color_r = (color_argb & 0x00ff0000) >> 16
            color_g = (color_argb & 0x0000ff00) >> 8
            color_b = (color_argb & 0x000000ff) >> 0
            mesh_colors[name] = (color_r, color_g, color_b, color_a)
        return mesh_colors

    @_closed_project_decorator
    def get_citation(self) -> str:
        """
        Get the stored citation for the project.

        :return: the stored citation as a string
        """
        return self.impl.GetCitation()

    @_closed_project_decorator
    def set_citation(self, citation: str) -> None:
        """
        Set the stored citation for the project.

        :param citation: the citation to store as a string
        """
        self.impl.SetCitation(citation)

    @_closed_project_decorator
    def copy_shader_settings_from_project(self, source: 'Project') -> None:
        """
        Copy the shader settings from one project to another.

        :param source: the project from which to copy the settings from
        """
        self.impl.CopyShaderSettingsFromProject(source.impl)


class ProjectCreationSettings:
    """
    Instances of this class represent configurations of project creation
    settings.

    TODO: Document each of these attributes here. Note that if
    ``target_data_type`` is changed, ``downsample_range`` must be changed
    accordingly. See ``Project.get_data_type()`` for examples of valid data
    type strings.
    """

    def __init__(self):
        self.is_timeseries = False
        self.voxel_dimensions = (1, 1, 1)
        self.voxel_unit = ""
        self.included_channels = ()
        self.key_position_indices = (0, 0, 0, 0)
        self.target_data_type = ProjectDataType.UINT8
        self.downsample_range = (0, 255)


def is_project(path: str) -> bool:
    """
    Given a string path, returns ``True`` if that path points to a valid
    syGlass project and ``False`` otherwise.

    :param path: a string path to a file
    :return: a boolean indicating whether the path points to a valid syGlass
             project
    """
    return pyglass.IsAProjectFile(pyglass.path(path))


def get_project(path: str) -> Project:
    """
    Given a string path to a valid ``.syg`` file, returns a ``Project`` object
    that represents that syGlass project.

    :param path: the string path to the project's ``.syg`` file
    :return: a ``Project`` object representing the given syGlass project
    """
    if pyglass.IsAProjectFile(pyglass.path(path)):
        project = Project(pyglass.OpenProject(pyglass.path(path)))
    else:
        raise NameError("Project at location {} not found!".format(path))
    return project


def create_project(
    reference_files: Iterable[str],
    destination: str,
    settings: ProjectCreationSettings
) -> Project:
    """
    :param reference_files: one file from each series containing the
                            volumetric image data, e.g. TIFF files
    :param destination: a string path where the project should be saved
    :param settings: an instance of ``ProjectCreationSettings`` configured
                     with the desired attributes
    :return: a ``Project`` object created from the given files
    """

    data_providers = []
    for index, reference_file in enumerate(reference_files):
        directory_description = pyglass.DirectoryDescription()
        directory_description.InspectByReferenceFile(reference_file)
        directory_description.SetKeyPos(settings.key_position_indices[index])

        new_data_provider = pyglass.DataProvider()
        file_type = directory_description.GetFileType()

        if file_type == pyglass.DirectoryDescription.Imaris:
            new_data_provider = pyglass.OpenHDF5(reference_file)

        elif file_type == pyglass.DirectoryDescription.DICOM:
            new_data_provider = pyglass.OpenDICOMs(
                directory_description.GetFileList())

        elif file_type == pyglass.DirectoryDescription.TIFF:
            new_data_provider = pyglass.OpenTIFFs(
                directory_description.GetFileList(), settings.is_timeseries)

        elif file_type == pyglass.DirectoryDescription.PNG:
            new_data_provider = pyglass.OpenPNGs(
                directory_description.GetFileList())

        elif file_type == pyglass.DirectoryDescription.JPEG:
            new_data_provider = pyglass.OpenJPEGs(
                directory_description.GetFileList())

        elif file_type == pyglass.DirectoryDescription.VSI or \
                file_type == pyglass.DirectoryDescription.OIR:
            new_data_provider = pyglass.OpenOlympus(reference_file)

        else:
            raise ValueError(
                "Reference file " + str(reference_file) + " is not a supported."
            )

        # TODO: validate, throw some more errors!

        data_providers.append(new_data_provider)

if __name__ == "__main__":
    print("TODO: some info here")
