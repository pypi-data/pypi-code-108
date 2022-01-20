"""
Basic I/O functions for creating/loading .iau files and reading from 
various file types.
"""

# ----------------------------------------------------------------------------------

import ast
import h5py
import numpy as np
import os
from typing import List, Tuple
import vtk
from vtk.util import numpy_support as npSup # type: ignore
import xarray as xr

# ----------------------------------------------------------------------------------

__all__ = (
    "create_iau_file",
    "load_iau_file"
)

# ----------------------------------------------------------------------------------

def create_iau_file (
    data_source: str, 
    iau_file_path: str, 
    axis_labels: List[str] = None, 
    new_axis_values: List = None,
    metadata: dict = None
) -> None:
    """
    Creates .iau file from data source. Data source can either be a single file
    or a directory of multiple data source files.

    Parameters:
    data_source (str): File/directory path used to create .iau file from.
    iau_file_path (str): File path to save .iau file in.
    axis_labels (list[str]): Labels for each axis.
    new_axis_values (list): For .iau files created from multiple data source files
        stitched together. Defines values for new axis.
    metadata (dict): Metadata for .iau file.
    """

    # Data source validation
    if not os.path.exists(data_source):
        raise OSError(
            f"{data_source} is an invalid path."
        )

    # Load data and axes from data source
    data, axes = None, None
    
    # Data source as directory
    if os.path.isdir(data_source):
        file_list = os.listdir(data_source) # directory contents, sorted
        file_list.sort()
        data_list, axes_list = [], []

        for file in file_list:
            data, axes = _load_data_source(str(os.path.join(data_source, file)))
            data_list.append(data)
            axes_list.append(axes)
        data, axes = _stitch(data_list, axes_list)

        # Handles new axis values 
        if new_axis_values is None:
            new_axis_values = [i for i in range(data.shape[-1])]
        axes.append(new_axis_values)
    # Data source as file
    elif os.path.isfile(data_source):
        data, axes = _load_data_source(data_source)

    # Handles axis labels
    if axis_labels is None:
        axis_labels = [f"axis_{i}" for i in range(data.ndim)]
    elif len(axis_labels) != data.ndim:
        raise ValueError(
            f"Invalid number of axis labels. Expected # of labels: {data.ndim}"
        )

    # Creates .iau file
    with h5py.File(iau_file_path, 'a') as new_file:
        new_file.create_dataset("data", data=data)
        new_file.attrs["metadata"] = str(metadata)
        new_file.create_group("axes")

        for i in range(len(axes)):
            axis = np.array(axes[i])
            new_file.create_dataset(f"axes/axis_{i}", data=axis)
            new_file["data"].dims[i].label = axis_labels[i]
            new_file[f"axes/axis_{i}"].make_scale(axis_labels[i])
            new_file["data"].dims[i].attach_scale(new_file[f"axes/axis_{i}"])

# ----------------------------------------------------------------------------------

def load_iau_file(file: str) -> xr.DataArray:
    """
    Retrieves data, axis info, and metadata from .iau file in an xarray dataset.

    Parameters:
        file (str): .iau file to load.

    Returns:
        data_array (xr.DataArray): Dataset containing data, axis info, and metadata.
    """
    
    # Reads info from .iau file
    with h5py.File(file, 'r') as iau_file:
        data = iau_file["data"][...]
        axes = [iau_file["data"].dims[i][0][...] for i in range(data.ndim)]
        axis_labels = [iau_file["data"].dims[i].label for i in range(data.ndim)]
        metadata = ast.literal_eval(iau_file.attrs["metadata"])

    # Creates xarray DataArray from .iau info
    # Internal data structure for everything in image-analysis-util
    data_array = xr.DataArray(
        data=data, 
        coords=axes, 
        dims=axis_labels, 
        attrs=metadata
    )

    return data_array
    
# ----------------------------------------------------------------------------------

def _load_data_source(file: str) -> Tuple[np.ndarray, List[list]]:
    """
    Retrieves data and axis values from data source file.

    Parameters:
        file (str): Data source file to load.

    Returns:
        data (np.ndarray): Multi-dimensional NumPy array holding data.
        axes (list[list]): List of values for each axis.
    """
    
    file_ext = os.path.splitext(file)[1]
    data, axes = None, None

    if file_ext == ".vti":
        data, axes = _load_vti(file)

    return data, axes

# ----------------------------------------------------------------------------------

def _stitch(
    data_list: List[np.ndarray],
    axes_list: List[list]
) -> Tuple[np.ndarray, List[list]]:
    """
    _stitches data from multiple data source files. Also checks for inconsistencies 
    in axis values.

    Parameters:
        data_list (list[np.ndarray]): List of data from each data source file.
        axes_list (list[list]): List of axis values from each data source file.

    Returns:
        data (np.ndarray): Stacked data arrays; n + 1 dimensions.
        axes (list[list]): Axis values from each axis.
    """
    
    data, axes = None, None

    # Checks if axes stay consistent throughout data source files
    consistent_axes = axes_list.count(axes_list[0]) == len(axes_list)

    if consistent_axes:
        axes = axes_list[0]
    else:
        raise ValueError(
            "Inconsistent axes throughout data source files."
        )

    # Converts list of NumPy arrays (ndim = n) to one NumPy array (ndim = n + 1)
    data = np.stack(data_list, axis=-1)
    
    return data, axes

# ----------------------------------------------------------------------------------

def _load_vti(file: str) -> Tuple[np.ndarray, List[list]]:
    """
    Retrieves data, axis values from .vti (VTK XML image format) file.
    .vti files contain 2D or 3D datasets.

    Parameters:
        file (str): .vti file to load.

    Returns:
        data (np.ndarray): Multi-dimensional NumPy array holding data.
        axes (list[list]): List of values for each axis.
    """
    
    data_reader = vtk.vtkXMLImageDataReader()
    data_reader.SetFileName(file)
    data_reader.Update()

    raw_data = data_reader.GetOutput()
    dimensions = list(raw_data.GetDimensions())

    data = npSup.vtk_to_numpy(raw_data.GetPointData().GetArray('Scalars_'))
    data = data.reshape(dimensions)

    origin = raw_data.GetOrigin() # First point for each axis
    spacing = raw_data.GetSpacing() # Space between points for each axis
    extent = raw_data.GetExtent() # First and last index of each axis

    axis_0, axis_1, axis_2 = [], [], []

    # Adds values to each axis accordingly
    for point in range(extent[0], extent[1] + 1):
        axis_0.append(origin[0] + point * spacing[0])
    for point in range(extent[2], extent[3] + 1):
        axis_1.append(origin[1] + point * spacing[1])
    for point in range(extent[4], extent[5] + 1):
        axis_2.append(origin[2] + point * spacing[2])

    # A list of lists of varying lengths
    axes = [axis_0, axis_1, axis_2]

    return data, axes

# ----------------------------------------------------------------------------------

"""create_iau_file(
    data_source="./examples/example_files",
    iau_file_path="./examples/example_files/scans.iau",
    axis_labels=["H", "K", "L", "V"],
    metadata={"name": "scans"}
)"""

#load_iau_file("./examples/example_files/scans.iau")
