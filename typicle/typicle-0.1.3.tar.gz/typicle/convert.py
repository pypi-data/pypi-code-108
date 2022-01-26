import numpy as np
import numpy.typing as npt


# TODO: add reverse from structured to unstructured
def cast_array(
    in_array: np.ndarray,
    cast_type: npt.DTypeLike,
) -> np.ndarray:
    """Returns a copy of the passed array in the desired type.
    """
    cast_type = np.dtype(cast_type)
    if in_array.dtype == cast_type:
        cast_array = in_array
    else:
        multi_dim = in_array.ndim > 1
        input_col_num = in_array.shape[-1]
        if cast_type.fields is None:
            target_col_num = 1
        else:
            target_col_num = len(cast_type.fields)
        if multi_dim and input_col_num != target_col_num:
            raise ValueError(
                    f'Casting to {cast_type} requires in_array with '
                    + f'{target_col_num} columns, but you passed an '
                    + f'array with shape {in_array.shape}.'
                    )
        cast_array = in_array.astype(cast_type.descr[0][1])
        cast_array = cast_array.copy()
        cast_array = cast_array.view(dtype=cast_type, type=np.ndarray)
        cast_array = cast_array.squeeze()
    return cast_array
