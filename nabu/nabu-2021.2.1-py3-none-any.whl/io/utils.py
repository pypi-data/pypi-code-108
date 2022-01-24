import warnings
import numpy as np
from silx.io.url import DataUrl
from tomoscan.io import HDF5File
# won't be necessary once h5py >= 3.0 required
from h5py import version as h5py_version
from packaging.version import parse as parse_version
#


# This function might be moved elsewhere
def get_compacted_dataslices(urls, subsampling=None):
    """
    Regroup urls to get the data more efficiently.
    Build a structure mapping files indices to information on
    how to load the data: `{indices_set: data_location}`
    where `data_location` contains contiguous indices.

    Parameters
    -----------
    urls: dict
        Dictionary where the key is an integer and the value is a silx `DataUrl`.
    subsampling: int, optional
        Subsampling factor when reading the frames. If an integer `n` is provided,
        then one frame out of `n` will be read.

    Returns
    --------
    merged_urls: dict
        Dictionary with the same keys as the `urls` parameter, and where the
        values are the corresponding `silx.io.url.DataUrl` with merged data_slice.
    """
    def _convert_to_slice(idx):
        if np.isscalar(idx):
            return slice(idx, idx+1)
        # otherwise, assume already slice object
        return idx

    def is_contiguous_slice(slice1, slice2):
        if np.isscalar(slice1):
            slice1 = slice(slice1, slice1+1)
        if np.isscalar(slice2):
            slice2 = slice(slice2, slice2+1)
        return slice2.start == slice1.stop

    def merge_slices(slice1, slice2):
        return slice(slice1.start, slice2.stop)

    if len(urls) == 0:
        return urls

    sorted_files_indices = sorted(urls.keys())
    idx0 = sorted_files_indices[0]
    first_url = urls[idx0]

    merged_indices = [
        [idx0]
    ]
    data_location = [
        [
            first_url.file_path(),
            first_url.data_path(),
            _convert_to_slice(first_url.data_slice())
        ]
    ]
    pos = 0
    curr_fp, curr_dp, curr_slice = data_location[pos]
    for idx in sorted_files_indices[1:]:
        url = urls[idx]
        next_slice = _convert_to_slice(url.data_slice())
        if (url.file_path() == curr_fp) and (url.data_path() == curr_dp) and is_contiguous_slice(curr_slice, next_slice):
            merged_indices[pos].append(idx)
            merged_slices = merge_slices(curr_slice, next_slice)
            data_location[pos][-1] = merged_slices
            curr_slice = merged_slices
        else: # "jump"
            pos += 1
            merged_indices.append([idx])
            data_location.append([
                url.file_path(), url.data_path(), _convert_to_slice(url.data_slice())
            ])
            curr_fp, curr_dp, curr_slice = data_location[pos]

    # Format result
    res = {}
    for ind, dl in zip(merged_indices, data_location):
        # res[tuple(ind)] = DataUrl(file_path=dl[0], data_path=dl[1], data_slice=dl[2])
        res.update(
            dict.fromkeys(ind, DataUrl(file_path=dl[0], data_path=dl[1], data_slice=dl[2]))
        )

    if subsampling is None or subsampling <= 1:
        return res

    # Subsample
    next_pos = 0
    for idx in sorted_files_indices:
        url = res[idx]
        url_str = str(url)
        ds = url.data_slice()
        res[idx] = DataUrl(
            file_path=url.file_path(), data_path=url.data_path(),
            data_slice=slice(next_pos + ds.start, ds.stop, subsampling)
        )
        n_imgs = ds.stop - (ds.start + next_pos)
        next_pos = abs(-n_imgs % subsampling)

    return res


def get_first_hdf5_entry(fname):
    with HDF5File(fname, "r") as fid:
        entry = list(fid.keys())[0]
    return entry


def hdf5_entry_exists(fname, entry):
    with HDF5File(fname, "r") as fid:
        res = fid.get(entry, None) is not None
    return res

def get_h5_value(fname, h5_path, default_ret=None):
    with HDF5File(fname, "r") as fid:
        try:
            val_ptr = fid[h5_path][()]
        except KeyError:
            val_ptr = default_ret
    return val_ptr


def get_h5_str_value(dataset_ptr):
    """
    Get a HDF5 field which can be bytes or str (depending on h5py version !).
    """
    data = dataset_ptr[()]
    if isinstance(data, str):
        return data
    else:
        return bytes.decode(data)


# won't be necessary once h5py >= 3.0 required
def check_h5py_version(logger=None):
    """
    (h5py, hdf5) < (3.0, 1.10.6) have many issues. For example:
       - https://github.com/silx-kit/silx/issues/3277
       - overwrite data using (2.10, 1.10.4) while the data was written with (3.0, 1.12)
    """
    recommendations = [
        ("h5py", h5py_version.version, "3.0"),
        ("libhdf5", h5py_version.hdf5_version, "1.10.6")
    ]
    for what, current_version, recommended_version in recommendations:
        msg = str("You are using %s %s. Unexpected behaviors can be experienced. Bugs were fixed in more recent versions. Please consider upgrading to %s >= %s. The h5py wheels (.whl files) contain the hdf5 library (libhdf5), so you don't need administrator privileges or another python environment."
            % (what, current_version, what, recommended_version)
        )
        if parse_version(current_version) < parse_version(recommended_version):
            warnings.warn(msg)
            if logger is not None:
                logger.warning(msg)


def create_dict_of_indices(images_stack, images_indices):
    """
    From an image stack with the images indices, create a dictionary where
    each index is the image index, and the value is the corresponding image.

    Parameters
    ----------
    images_stack: numpy.ndarray
        A 3D numpy array in the layout (n_images, n_y, n_x)
    images_indices: array or list of int
        Array containing the indices of images in the stack

    Examples
    --------
    Given a simple array stack:

    >>> images_stack = np.arange(3*4*5).reshape((3,4,5))
    ... images_indices = [2, 7, 1]
    ... create_dict_of_indices(images_stack, images_indices)
    ... # returns {2: array1, 7: array2, 1: array3}
    """
    if images_stack.ndim != 3:
        raise ValueError("Expected a 3D array")
    if len(images_indices) != images_stack.shape[0]:
        raise ValueError("images_stack must have as many images as the length of images_indices")
    res = {}
    for i in range(len(images_indices)):
        res[images_indices[i]] = images_stack[i]
    return res


def convert_dict_values(dic, val_replacements, bytes_tostring=False):
    """
    Modify a dictionary to be able to export it with silx.io.dicttoh5
    """
    modified_dic = {}
    for key, value in dic.items():
        if isinstance(key, int): # np.isscalar ?
            key = str(key)
        if isinstance(value, bytes) and bytes_tostring:
            value = bytes.decode(value.tostring())
        if isinstance(value, dict):
            value = convert_dict_values(value, val_replacements, bytes_tostring=bytes_tostring)
        else:
            if isinstance(value, DataUrl):
                value = value.path()
            elif value.__hash__ is not None and value in val_replacements:
                value = val_replacements[value]
        modified_dic[key] = value
    return modified_dic
