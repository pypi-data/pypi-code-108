import json
import pathlib
from typing import List, Tuple

try:
    import numpy as np
    NUMPY_LIB = True
except ModuleNotFoundError:
    NUMPY_LIB = False
try:
    import pandas as pd
    PANDAS_LIB = True
except ModuleNotFoundError:
    PANDAS_LIB = False
try:
    import h5py
    H5PY_LIB = True
except ModuleNotFoundError:
    H5PY_LIB = False


NUMPY_NOT_FOUND_ERRROR_MSG = 'The library was not able to successfully import "numpy" package, check your Python ' \
                             'environment'
H5PY_LIB = 'The library was not able to successfully import "h5py" package, check your Python environment'


def coerce_data_as_numpy_array(data):
    """Validates that data can be coerced into a numpy array

    Args:
        data (Union[np.ndarray, pd.DataFrame, List]): The data to be transformed.

    Raises:
        TypeError: If data is wrong type.

    Returns:
        np.ndarray: A numpy array of data.
    """
    allowed_input = False
    if not NUMPY_LIB:
        raise ModuleNotFoundError(NUMPY_NOT_FOUND_ERRROR_MSG)
    elif NUMPY_LIB and isinstance(data, np.ndarray):
        allowed_input = True
    elif PANDAS_LIB and isinstance(data, pd.DataFrame):
        allowed_input = True
    elif isinstance(data, list):
        allowed_input = True
    if not allowed_input:
        raise TypeError(f'Data must be one of type [np.ndarray, pd.DataFrame, list], got {type(data)}')
    return np.array(data)


def coerce_input_to_json(inputs, metadata=None) -> Tuple[List, List]:
    """Takes supported inputs and coerces them into JSON

    Args:
        inputs: The data representing one or more inputs to call the model with.
                Accepted types are: list, pandas.DataFrame, and numpy.ndarray
            metadata (Union[pd.DataFrame, List[Dict]]): Metadata key/value pairs (e.g. name, url), one for each input.

    Raises:
        TypeError: If data is wrong type.

    Returns:
        Tuple[List, List] - the representation as JSON serializable lists
    """

    if PANDAS_LIB and isinstance(inputs, pd.DataFrame):
        inputs_list = inputs.to_dict('records')
    elif NUMPY_LIB and isinstance(inputs, np.ndarray):
        inputs_np_array = np.array(inputs)
        inputs_list = inputs_np_array.tolist()
    elif not isinstance(inputs, list):
        raise TypeError('predict can be called with either a list, a pandas DataFrame, or a numpy array.')
    else:
        inputs_list = inputs

    if PANDAS_LIB and isinstance(metadata, pd.DataFrame):
        metadata = metadata.to_dict(orient='records')
    return inputs_list, metadata


def build_h5_data_object(feature_data, target_data, metadata, data_temp_directory) -> str:
    """Creates an h5 file from the data object

    Args:
        feature_data (Union[np.ndarray, pd.DataFrame, List[List]]): The feature data to upload.
        target_data (Union[np.ndarray, pd.DataFrame, List[List]]): The target data to upload.
        metadata (List[Dict]): Metadata key/value pairs for the dataset.
        data_temp_directory (str): Folder name of a temporary directory to write `tmp.h5` to

        Returns:
            A filepath to the local h5 object
     """
    if not H5PY_LIB:
        raise ModuleNotFoundError(H5PY_LIB)
    if not NUMPY_LIB:
        raise ModuleNotFoundError(NUMPY_NOT_FOUND_ERRROR_MSG)
    data_temp_file = pathlib.PurePath(data_temp_directory, 'tmp.h5')
    feature_data_np = coerce_data_as_numpy_array(feature_data)
    data = {'features': feature_data_np}
    if np.any(target_data):
        data['targets'] = coerce_data_as_numpy_array(target_data)
    if np.any(metadata):
        data['metadata'] = json.dumps(metadata)

    h5_data = h5py.File(data_temp_file, mode='w')
    h5_sample_data_group = h5_data.create_group('sample_data')
    for key, np_obj in data.items():
        if key == 'metadata':
            dt = h5py.string_dtype(encoding='utf-8')
            h5_sample_data_group.create_dataset(key, data=np_obj, dtype=dt)
        else:
            h5_sample_data_group.create_dataset(key, data=np_obj)
    h5_data.close()
    return data_temp_file
