from functools import partial
from typing import Iterable
from typing import Iterator
from typing import Tuple
from typing import Union

import numpy as np
from skimage import transform as skit


def affine_transform_arrays(
    arrays: Union[Iterable[np.ndarray], np.ndarray],
    matrix: np.ndarray = None,
    scale: Union[Tuple[float, float], np.ndarray, float] = None,
    translation: Union[Tuple[float, float], np.ndarray, float] = None,
    rotation: float = None,
    shear: Union[Tuple[float, float], np.ndarray, float] = None,
    **kwargs,
) -> Iterator[np.ndarray]:
    """
    Transform an iterable of input arrays using a generalized affine transform operator.
    A transform matrix may be specified or separate parameters for scale, translation,
    rotation and shear may be specified instead. This method abstracts the use of the
    scikit-image affine transform, which may easily be replaced with one from scipy or
    another origin. If transform parameters are specified, they are applied in this order:
    shear, scale, rotation, translation

    Parameters
    ----------
    arrays
        The array(s) to be transformed

    matrix
        The transformation matrix to be used for the transform. If specified, none of
        [translation, rotation, or shear] may be used. Optional.

    Optional arguments
        If matrix is not specified, at least one of the following must be used:

            scale
                The scale factor to be applied in the transform: (Sx, Sy). If a scalar is used, the same
                value is applied to each axis.

            translation
                The translation to be applied in the transform: (Tx, Ty) in pixel units.

            rotation
                The rotation angle, in radians, to be applied to the transformation.
                A positive angle is counter-clockwise in a right handed coordinate system

            shear:
                The shear factor to be applied in the transform: (Shx, Shy). If a scalar is used, the same
                value is applied to each axis.

            **kwargs
                Optional arguments to be passed on to skimage.transform.warp() if desired. See
                https://scikit-image.org/docs/stable/api/skimage.transform.html#skimage.transform.warp
                for more details.

    Returns
    -------
    The transformed array(s)

    """
    tform = None
    any_param_set = any(param is not None for param in [scale, translation, rotation, shear])

    # We do our own pre-checks here so that we're not totally tied to use scikit-image in the future
    #
    if not any_param_set and matrix is None:
        raise ValueError(
            "You must specify matrix or at least one of scale, rotate, shear, or shift."
        )

    elif any_param_set and matrix is not None:
        raise ValueError(
            "You cannot specify both matrix and any of scale, rotate, shear, or shift."
        )

    elif matrix is not None:
        if matrix.shape != (3, 3):
            raise ValueError(f"Invalid shape of transformation matrix: {matrix.shape}")
        tform = skit.AffineTransform(matrix=matrix)

    elif any_param_set:
        # Construct the matrix from parameters
        if scale is None:
            scale = (1.0, 1.0)
        elif np.isscalar(scale):
            scale = (scale, scale)

        if translation is None:
            translation = (0.0, 0.0)
        elif np.isscalar(translation):
            translation = (translation, translation)

        if rotation is None:
            rotation = 0.0

        if shear is None:
            shear = (0.0, 0.0)

        translation = translation[::-1]  # Because skimage and numpy have different axes ordering
        shear_mat = shear_matrix(shear)
        temp_tform = skit.AffineTransform(scale=scale, translation=translation, rotation=rotation)
        tform_mat = temp_tform.params @ shear_mat
        tform = skit.AffineTransform(matrix=tform_mat)

    arrays = [arrays] if isinstance(arrays, np.ndarray) else arrays
    partial_warp = partial(skit.warp, inverse_map=tform.inverse, **kwargs)
    return map(partial_warp, arrays)


def rotate_arrays_about_point(
    arrays: Union[Iterable[np.ndarray], np.ndarray],
    angle: float = 0.0,
    point: Union[Tuple[float, float], np.ndarray] = None,
    **kwargs,
) -> Iterator[np.ndarray]:
    """
    Rotate an iterable of arrays about a specified point

    Parameters
    ----------
    arrays
        The array(s) to be rotated

    angle
        The angle, in radians, for the rotation to be applied, optional. Default is zero
        A positive angle is counter-clockwise in a right handed coordinate system and
        clockwise in a left-handed coordinate system

    point
        The point, in pixel coordinates (x, y) about which to rotate. Optional. Default is None,
        meaning the center of the array will be used. Note that the origin pixel is centered at
        (0, 0) and has extent: [-0.5: 0.5, -0.5: 0.5]

    kwargs
        Any arguments to be passed to skimage.transform.rotate. See
        https://scikit-image.org/docs/stable/api/skimage.transform.html#skimage.transform.rotate
        for more details.

    Returns
    -------
    An Iterator yielding the rotated arrays.

    """
    arrays = [arrays] if isinstance(arrays, np.ndarray) else arrays
    partial_rotate = partial(skit.rotate, angle=np.degrees(angle), center=point, **kwargs)
    return map(partial_rotate, arrays)


def translate_arrays(
    arrays: Union[Iterable[np.ndarray], np.ndarray],
    translation: Union[Tuple[float, float], np.ndarray] = (0.0, 0.0),
    **kwargs,
) -> Iterator[np.ndarray]:
    """
    Translate an iterable of arrays by a specified vector

    Parameters
    ----------
    arrays
        The array(s) to be translated

    translation
        The translation to be applied in the transform: (Tx, Ty) in pixel units. Optional.

    **kwargs
        Optional arguments to be passed on to skimage.transform.warp() if desired. See
        https://scikit-image.org/docs/stable/api/skimage.transform.html#skimage.transform.warp
        for more details.

    Returns
    -------
    np.ndarray
        The translated array

    """
    arrays = [arrays] if isinstance(arrays, np.ndarray) else arrays
    return affine_transform_arrays(arrays, translation=translation, **kwargs)


def scale_matrix(scale_factors: Union[Tuple[float, float], float] = (1.0, 1.0)) -> np.ndarray:
    """
    Create an Affine Transform matrix for a scale operation

    Parameters
    ----------
    scale_factors
        The scale factors to use in scaling the array. If a scalar is passed, it
        is applied to both axes.

    Returns
    -------
    A 3x3 homogeneous transform matrix implementing the scaling
    """
    return skit.AffineTransform(scale=scale_factors).params


def rotation_matrix(angle: float = 0.0) -> np.ndarray:
    """
    Create an Affine Transform matrix for a rotation operation
    This assumes the rotation is about (0, 0) and it is up to the user
    to calculate the appropriate translation offset to be applied in the
    skimage.warp() method to achieve rotation about an arbitrary point

    Parameters
    ----------
    angle
        The angle of rotation in radians. This represents counter-clockwise rotation
        in a right-handed coordinate system and clockwise rotation in a left-handed
        system

    Returns
    -------
    A 3x3 homogeneous transform matrix implementing the rotation
    """
    return skit.AffineTransform(rotation=angle).params


def shear_matrix(shear_factors: Union[Tuple[float, float], float] = (1.0, 1.0)) -> np.ndarray:
    """
    Create an Affine Transform matrix for a shear operation

    Parameters
    ----------
    shear_factors
        The shear scaling factors.

    Returns
    -------
    A 3x3 homogeneous transform matrix implementing the shear
    """
    if isinstance(shear_factors, float):
        shear_factors = shear_factors, shear_factors
    shear_mat = np.eye(3, 3)
    shear_mat[0, 1] = shear_factors[0]
    shear_mat[1, 0] = shear_factors[1]
    return shear_mat


def translation_matrix(offsets: Union[Tuple[float, float], float] = (1.0, 1.0)) -> np.ndarray:
    """
    Create an Affine Transform matrix for a translation operation

    Parameters
    ----------
    offsets
        The translation ofsets.

    Returns
    -------
    A 3x3 homogeneous transform matrix implementing the translation
    """
    if isinstance(offsets, float):
        offsets = offsets, offsets
    trans_mat = np.eye(3, 3)
    trans_mat[0, 2] = offsets[1]
    trans_mat[1, 2] = offsets[0]
    return trans_mat
