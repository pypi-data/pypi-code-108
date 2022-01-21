'''conversion.py

This module is for converting between Pythonnet representations and mastapy
representations. Should only be used internally.
'''


from typing import List, Union, Sequence, Any
from datetime import datetime
from io import BytesIO
from collections import OrderedDict
from numpy import ndarray
from packaging.version import Version

from PIL import Image

from mastapy._internal.python_net import python_net_import
from mastapy._math.vector_2d import Vector2D
from mastapy._math.vector_3d import Vector3D
from mastapy._math.vector_4d import Vector4D
from mastapy._math.color import Color
from mastapy._math.matrix_4x4 import Matrix4x4
from mastapy._internal.tuple_with_name import TupleWithName

_SYSTEM = python_net_import('System')
_IO = python_net_import('System.IO')
_IMAGE = python_net_import('System.Drawing.Image')
_COLOR = python_net_import('System.Drawing', 'Color')
_LIST = python_net_import('System.Collections.Generic', 'List')
_DICTIONARY = python_net_import('System.Collections.Generic', 'Dictionary')
_VECTOR2D = python_net_import('SMT.MastaAPI.MathUtility', 'Vector2D')
_VECTOR3D = python_net_import('SMT.MastaAPI.MathUtility', 'Vector3D')


class ConversionException(Exception):
    pass


# -----------------------------------------------------------------------
# - Object conversions
# -----------------------------------------------------------------------


def pn_to_mp_objects_in_iterable(iterable_of_objects, wrapper=None):
    '''Wraps up all Pythonnet objects returned in an iterable in mastapy types

    Args:
        iterable_of_objects: Iterable of Pythonnet objects
        wrapper: the wrapping mastapy type

    Returns:
        Iterable[wrapper]
    '''
    if not wrapper:
        return iterable_of_objects

    if wrapper is Vector4D:
        wrapper = Vector4D.wrap
    elif wrapper is Vector3D:
        wrapper = Vector3D.wrap
    elif wrapper is Vector2D:
        wrapper = Vector2D.wrap

    return (wrapper(x) for x in iterable_of_objects)


def pn_to_mp_objects_in_list(list_of_objects, wrapper=None):
    '''Wraps up all Pythonnet objects returned in a list in mastapy types

    Args:
        list_of_objects: List of Pythonnet objects
        wrapper: the wrapping mastapy type

    Returns:
        List[wrapper]
    '''
    if wrapper:
        return list(pn_to_mp_objects_in_iterable(list_of_objects, wrapper))
    else:
        return list(pn_to_mp_objects_in_iterable(list_of_objects))


def pn_to_mp_objects_in_iterable_of_iterables(
        iterable_of_objects, wrapper=None):
    '''Wraps up all Pythonnet objects returned in an iterable of iterables.

    Args:
        iterable_of_objects: Iterable of iterables of Pythonnet objects
        wrapper: the wrapping mastapy type

    Returns:
        Iterable[Iterable[wrapper]]
    '''
    for iterable in iterable_of_objects:
        if wrapper:
            yield from pn_to_mp_objects_in_iterable(iterable, wrapper)
        else:
            yield from pn_to_mp_objects_in_iterable(iterable)


def pn_to_mp_objects_in_list_of_lists(list_of_objects, wrapper=None):
    '''Wraps up all Pythonnet objects returned in a list of lists.

    Args:
        list_of_objects: List of lists of Pythonnet objects
        wrapper: the wrapping mastapy type

    Returns:
        List[List[wrapper]]
    '''
    if wrapper:
        return [pn_to_mp_objects_in_list(x, wrapper) for x in list_of_objects]
    else:
        return [pn_to_mp_objects_in_list(x) for x in list_of_objects]


def mp_to_pn_objects_in_list(list_of_objects):
    '''Unwraps all mastapy objects to a list of pythonnet objects

    Args:
        list_of_objects: List of mastapy objects

    Returns:
        List[x._TYPE]
    '''

    return [x.wrapped for x in list_of_objects]


def pn_to_mp_complex(pn_complex):
    '''Converts Masta API complex types to Python complex types

    Args:
        pn_complex: Masta API complex object

    Returns:
        complex
    '''

    return complex(pn_complex.Real, pn_complex.Imaginary)


def pn_to_mp_complex_list(pn_complex_list):
    '''Converts Masta API complex types in a list to Python complex types
    in a list

    Args:
        pn_complex: List of Masta API complex objects

    Returns:
        List[complex]
    '''

    return [pn_to_mp_complex(x) for x in pn_complex_list]


def pn_to_mp_enum(pn_enum):
    '''Converts C# enum to int

    Args:
        pn_enum: C# enum

    Returns:
        int
    '''
    return int(pn_enum)


def mp_to_pn_enum(mp_enum):
    '''Converts Python enum to C# enum

    Args:
        mp_enum: Python enum

    Returns:
        int
    '''

    try:
        return mp_enum.value if mp_enum else 0
    except AttributeError:
        return int(mp_enum)


def pn_to_mp_vector2d(pn_vector2d) -> Vector2D:
    '''Converts C# Vector2D and friends to a mastapy Vector2D

    Args:
        pn_vector2d: C# Vector2D (or similar)

    Returns:
        Vector2D
    '''

    return Vector2D.wrap(pn_vector2d)


def mp_to_pn_vector2d(mp_vector2d):
    '''Converts Python tuple to C# Vector2D

    Args:
        mp_vector2d: tuple

    Returns:
        C# Vector2D
    '''

    if (not hasattr(mp_vector2d, '__iter__')
            or len(mp_vector2d) != 2):
        raise ConversionException((
            'Failed to convert object to a Vector2D. '
            'Make sure that the object is iterable and contains exactly 2 '
            'components.'))

    return _VECTOR2D(mp_vector2d[0], mp_vector2d[1])


def pn_to_mp_vector3d(pn_vector3d) -> Vector3D:
    '''Converts C# Vector3D and friends to a mastapy Vector3D

    Args:
        pn_vector3d: C# Vector3D (or similar)

    Returns:
        Vector3D
    '''

    return Vector3D.wrap(pn_vector3d)


def mp_to_pn_vector3d(mp_vector3d):
    '''Converts Python tuple to C# Vector3D

    Args:
        mp_vector3d: tuple

    Returns:
        C# Vector3D
    '''

    if (not hasattr(mp_vector3d, '__iter__')
            or len(mp_vector3d) != 3):
        raise ConversionException((
            'Failed to convert object to a Vector3D. '
            'Make sure that the object is iterable and contains exactly 3 '
            'components.'))

    return _VECTOR3D(mp_vector3d[0], mp_vector3d[1], mp_vector3d[2])


def pn_to_mp_color(pn_color) -> Color:
    '''Converts C# Color to a mastapy Color

    Args:
        pn_color: C# Color

    Returns:
        Color
    '''

    return Color.wrap(pn_color)


def mp_to_pn_color(mp_color):
    '''Converts Python tuple to C# Color

    Args:
        mp_color: tuple

    Returns:
        C# Color
    '''

    num_components = len(mp_color)

    if (not hasattr(mp_color, '__iter__')
            or num_components < 3 or num_components > 4):
        raise ConversionException((
            'Failed to convert object to a Color. '
            'Make sure that the object is iterable and contains exactly 3 or 4'
            ' components.'))

    if num_components < 4:
        mp_color = *mp_color, 255

    r, g, b, a = mp_color

    return _COLOR.FromArgb(a, r, g, b)


def pn_to_mp_matrix4x4(pn_matrix4x4) -> Matrix4x4:
    '''Converts C# TransformMatrix3D to a Matrix4x4

    Args:
        pn_matrix4x4: C# TransformMatrix3D

    Returns:
        Matrix4x4
    '''

    return Matrix4x4.wrap(pn_matrix4x4)


def mp_to_pn_matrix4x4(mp_matrix4x4) -> Matrix4x4:
    '''Converts Matrix4x4 to a C# TransformMatrix3D

    Args:
        mp_matrix4x4: Matrix4x4

    Returns:
        TransformMatrix3D
    '''

    message = ('Can only pass in Matrix4x4 that was first obtained from '
               'Masta. You cannot pass in a Matrix4x4 you have constructed '
               'yourself.')

    try:
        if not mp_matrix4x4.wrapped:
            raise ConversionException(message)

        return mp_matrix4x4.wrapped
    except AttributeError:
        raise ConversionException(message)


def pn_to_mp_tuple_with_name(pn_tuple_with_name, conversion_methods=None):
    '''Converts C# NamedTuple to Python TupleWithName

    Args:
        pn_tuple_with_name: C# NamedTuple
        conversion_methods (optional): conversion methods for items in tuple

    Returns:
        TupleWithName
    '''

    attrs = filter(None, map(
        lambda x: getattr(
            pn_tuple_with_name, 'Item' + str(x), None), range(1, 8)))
    converted = (
        map(
            lambda x: x[1](x[0]) if x[1] else x[0],
            zip(attrs, conversion_methods))
        if conversion_methods
        else attrs)
    return TupleWithName(*tuple(converted), name=pn_tuple_with_name.Name)


def pn_to_mp_datetime(pn_datetime):
    '''Converts C# System.DateTime struct to python datetime object

    Args:
        pn_datetime: C# System.DateTime struct

    Returns:
        datetime
    '''

    if not pn_datetime:
        return datetime.max

    year = pn_datetime.Year
    month = pn_datetime.Month
    day = pn_datetime.Day
    hour = pn_datetime.Hour
    minute = pn_datetime.Minute
    second = pn_datetime.Second
    microsecond = pn_datetime.Millisecond * 1000

    return datetime(year, month, day, hour, minute, second, microsecond)


def pn_to_mp_image(pn_image):
    '''Converts C# System.Drawing.Image to a PIL image

    Args:
        pn_image: C# System.Drawing.Image

    Returns:
        PIL.Image
    '''

    if not pn_image:
        return None

    image_format = python_net_import('System.Drawing.Imaging.ImageFormat')

    memory_stream = _IO.MemoryStream()
    pn_image.Save(memory_stream, image_format.Png)

    byte_data = bytes(memory_stream.ToArray())
    byte_stream = BytesIO(byte_data)
    image = Image.open(byte_stream)

    memory_stream.Dispose()

    return image


def mp_to_pn_image(mp_image):
    '''Converts PIL image to a C# System.Drawing.Image

    Args:
        mp_image: PIL image

    Returns:
        C# System.Drawing.Image
    '''

    if not mp_image:
        return None

    byte_stream = BytesIO()
    mp_image.save(byte_stream, format=mp_image.format)
    byte_data = byte_stream.getvalue()

    memory_stream = _IO.MemoryStream(byte_data)
    return _IMAGE.FromStream(memory_stream)


def pn_to_mp_smt_bitmap(pn_image):
    '''Converts C# SMTBitmap to a PIL image

    Args:
        pn_image: C# SMTBitmap

    Returns:
        PIL.Image
    '''
    if not pn_image:
        return None

    return pn_to_mp_image(pn_image.ToImage())


def mp_to_pn_smt_bitmap(mp_image):
    '''Converts PIL image to a C# SMTBitmap

    Args:
        mp_image: PIL image

    Returns:
        C# SMTBitmap
    '''
    if not mp_image:
        return None

    return mp_to_pn_image(mp_image.ToImage())


def pn_to_mp_version(pn_version):
    '''Converts C# Version to Python Version

    Args:
        pn_version: C# Version

    Returns:
        packaging.version.Version
    '''

    if not pn_version:
        return None

    return Version(pn_version.ToString())


def mp_to_pn_version(mp_version):
    '''Converts Python Version to C# Version

    Args:
        mp_version: Python Version

    Returns:
        System.Version
    '''

    if not mp_version:
        return None

    return _SYSTEM.Version(str(mp_version))


# -----------------------------------------------------------------------
# - Dictionary conversions
# -----------------------------------------------------------------------


def pn_to_mp_dict(pn_dict):
    '''Converts a C# dictionary to a python dictionary

    Note:
        We assume that the key is a basic Python type.

    Args:
        pn_dict : C# dictionary

    Returns:
        Dict[TKey, TValue]
    '''

    if not pn_dict:
        return dict()

    return {kvp.Key: kvp.Value for kvp in pn_dict}


def mp_to_pn_dict_float(mp_dict):
    '''Converts a python dictionary to a C# dictionary

    Args:
        mp_dict : python dictionary

    Returns:
        C# dictionary
    '''

    if not isinstance(mp_dict, dict):
        raise ConversionException(
            'Invalid argument provided. Argument must be a dictionary.')

    new_dict = _DICTIONARY[_SYSTEM.String, _SYSTEM.Double]()
    for key, value in mp_dict.items():

        if not isinstance(key, str):
            raise ConversionException(
                'Invalid argument provided. Dictionary keys must be str.')

        if not isinstance(value, float):
            raise ConversionException(
                'Invalid argument provided. Dictionary values must be float.')

        new_dict.Add(key, value)
    return new_dict


def pn_to_mp_objects_in_list_in_ordered_dict(dict_of_objects, wrapper=None):
    '''Wraps up all Pythonnet objects returned in a list in a dictionary in
    mastapy types and returns Python list and OrderedDict structures

    Note:
        We assume that the key is a basic Python type.

    Args:
        dict_of_objects: Dictionary of lists of objects.
            e.g. {float : [PYTHON_NET_OBJECT, ...], ...}
        wrapper: the wrapping mastapy type

    Returns:
        OrderedDict[TKey, List[wrapper]]
    '''
    if wrapper:
        return OrderedDict(
            (kv.Key, [wrapper(obj) for obj in kv.Value])
            for kv in dict_of_objects)
    else:
        return OrderedDict((kv.Key, kv.Value) for kv in dict_of_objects)


def pn_to_mp_objects_in_list_in_dict(dict_of_objects, wrapper=None):
    '''Wraps up all Pythonnet objects returned in a list in a dictionary in
    mastapy types and returns Python list and dictionary structures

    Note:
        We assume that the key is a basic Python type.

    Args:
        dict_of_objects: Dictionary of lists of objects.
            e.g. {float: [PYTHON_NET_OBJECT, ...], ...}
        wrapper: the wrapping mastapy type

    Returns:
        Dict[TKey, List[wrapper]]
    '''

    if wrapper:
        return {
            kv.Key: [wrapper(obj) for obj in kv.Value]
            for kv in dict_of_objects}
    else:
        return {kv.Key: kv.Value for kv in dict_of_objects}


# -----------------------------------------------------------------------
# - List conversions
# -----------------------------------------------------------------------


def _pn_to_mp_tuple_append(values: List[Any], other, attr: str) -> bool:
    try:
        values.append(getattr(other, attr))
    except AttributeError:
        return False

    return True


def pn_to_mp_tuple(pn_tuple):
    '''Converts a C# tuple to a Python tuple

    Args:
        pn_tuple (System.Tuple[...]): C# tuple

    Returns:
        Tuple[...]
    '''

    values = []
    i = 1

    while _pn_to_mp_tuple_append(values, pn_tuple, 'Item{}'.format(i)):
        i += 1

    return tuple(values)


def mp_to_pn_tuple(mp_tuple):
    '''Converts a Python tuple to a C# tuple

    Args:
        mp_tuple (System.Tuple[...]): Python tuple

    Returns:
        System.Tuple[...]
    '''

    if mp_tuple is None or not any(mp_tuple):
        raise ConversionException(
            'Invalid argument provided. Was expecting a tuple')

    return _SYSTEM.Tuple.Create(*mp_tuple)


def pn_to_mp_bytes(pn_list: _SYSTEM.Array[_SYSTEM.Byte]) -> bytes:
    '''Converts a C# byte array to a bytes object

    Args:
        pn_list (System.Array[System.Byte]): 1D Array of bytes

    Returns:
        bytes
    '''

    return bytes([int(x) for x in pn_list])


def pn_to_mp_list_float(pn_list: _SYSTEM.Array[_SYSTEM.Double]) -> List[float]:
    '''Converts a 1D Array of Doubles to a list of floats

    Args:
        pn_list (System.Array[System.Double]): 1D Array

    Returns:
        List[float]
    '''

    return list(pn_list)


def mp_to_pn_array_float(
        mp_list: Union[
            ndarray, Sequence[float]]) -> _SYSTEM.Array[_SYSTEM.Double]:
    '''Converts a list of floats to a 1D array

    Args:
        mp_list (List[float]): List of floats

    Returns:
        System.Array[System.Double]: i.e. System.Double[]
    '''

    if mp_list is None or not any(mp_list):
        return _SYSTEM.Array.CreateInstance(_SYSTEM.Double, 0)

    if isinstance(mp_list, ndarray):
        if len(mp_list.shape) > 1:
            raise ConversionException((
                'Invalid argument provided. Argument must be a 1D array of '
                'float values.'))

    pn_list = _SYSTEM.Array.CreateInstance(_SYSTEM.Double, len(mp_list))
    for i, x in enumerate(mp_list):
        pn_list.SetValue(_SYSTEM.Double(x), i)
    return pn_list


def mp_to_pn_list_float(
        mp_list: Union[ndarray, Sequence[float]]) -> _LIST[_SYSTEM.Double]:
    '''Converts a list of floats to a 1D list

    Args:
        mp_list (List[float]): List of floats

    Returns:
        System.Collections.Generic.List[System.Double]
    '''

    if isinstance(mp_list, ndarray):
        if len(mp_list.shape) > 1:
            raise ConversionException((
                'Invalid argument provided. Argument must be a 1D array of '
                'float values.'))

    new_list = _LIST[_SYSTEM.Double]()
    for x in mp_list:
        new_list.Add(x)
    return new_list


def pn_to_mp_list_float_2d(
        pn_list: _SYSTEM.Array[_SYSTEM.Double]) -> List[List[float]]:
    '''Converts a 2D Array of Doubles to a list of lists of floats

    Args:
        pn_list (System.Array[System.Double]): 2D Array

    Returns:
        List[List[float]]
    '''

    length0 = pn_list.GetLength(0)
    length1 = pn_list.GetLength(1)

    return [
        [pn_list.GetValue(y, x) for x in range(length1)]
        for y in range(length0)]


def mp_to_pn_list_float_2d(
        mp_list: List[List[float]]) -> _SYSTEM.Array[_SYSTEM.Double]:
    '''Converts a list of lists of floats to a 2D array

    Args:
        mp_list (List[List[float]]): List of lists of floats

    Returns:
        System.Array[System.Double]: i.e. System.Double[,]
    '''

    if mp_list is None or not any(mp_list):
        return _SYSTEM.Array.CreateInstance(_SYSTEM.Double, 0, 0)

    length0 = len(mp_list)

    if not length0 or not hasattr(mp_list[0], '__iter__'):
        raise ConversionException(
            'Invalid argument provided. Argument is not a list of lists.')

    length1 = len(mp_list[0])

    pn_list = _SYSTEM.Array.CreateInstance(_SYSTEM.Double, length0, length1)
    for i, y in enumerate(mp_list):
        if not hasattr(y, '__iter__') or len(y) != length1:
            raise ConversionException((
                'Invalid argument provided. Argument must be a '
                '2d array (i.e. [[1.0, 0.0], [0.0, 1.0]])'))
        for j, x in enumerate(y):
            pn_list.SetValue(float(x), i, j)
    return pn_list
