'''matrix_3x3.py'''


import math
from typing import Union, Iterable, Iterator, Tuple, List

from mastapy._math.matrix_base import (
    MatrixBase, flatten, MATRIX_TYPE, MatrixException,
    ERROR_TUPLE, _safe_matrix_op)
from mastapy._math.matrix_2x2 import Matrix2x2
from mastapy._math.vector_4d import Vector4D
from mastapy._math.vector_3d import Vector3D
from mastapy._math.scalar import NUM


__all__ = ('Matrix3x3',)


ERROR_3D_MESSAGE = 'Vector must match matrix3x3 dimension.'
ERROR_3D_INDEX_MESSAGE = 'Invalid column index. There are only 3 columns.'
safe_matrix3x3_op = _safe_matrix_op(ERROR_3D_MESSAGE)


class Matrix3x3(MatrixBase):
    ''' Create a column-major Matrix3x3 from M11, M12, M13, M21, M22, M23,
    M31, M32, M33 components.

    Args:
        m11: NUM
        m12: NUM
        m13: NUM
        m21: NUM
        m22: NUM
        m23: NUM
        m31: NUM
        m32: NUM
        m33: NUM

    Returns:
        Matrix3x3
    '''

    def __init__(
            self,
            m11: NUM, m12: NUM, m13: NUM,
            m21: NUM, m22: NUM, m23: NUM,
            m31: NUM, m32: NUM, m33: NUM) -> 'Matrix3x3':
        super().__init__([
            float(m11), float(m12), float(m13),
            float(m21), float(m22), float(m23),
            float(m31), float(m32), float(m33)])

    @classmethod
    def broadcast(cls, value: NUM) -> 'Matrix3x3':
        ''' Create a Matrix3x3 by broadcasting a value to all of its components

        Args:
            value: NUM

        Returns:
            Matrix3x3
        '''

        return cls(
            value, value, value,
            value, value, value,
            value, value, value)

    @classmethod
    def diagonal(cls, value: Union[NUM, Iterable[NUM]]) -> 'Matrix3x3':
        ''' Create a Matrix3x3 by broadcasting a value along the diagonal

        Args:
            value: Union[NUM, Iterable[NUM]]

        Returns:
            Matrix3x3
        '''

        if hasattr(value, '__iter__'):
            value = tuple(value)
            if len(value) != 3:
                raise MatrixException(ERROR_3D_MESSAGE)
            return cls(
                value[0], 0.0, 0.0,
                0.0, value[1], 0.0,
                0.0, 0.0, value[2])
        return cls(
            value, 0.0, 0.0,
            0.0, value, 0.0,
            0.0, 0.0, value)

    @classmethod
    def from_iterable(
            cls,
            t: Union[Iterable[Iterable[NUM]], Iterable[NUM]]) -> 'Matrix3x3':
        ''' Create a Matrix3x3 from an iterable

        Args:
            t: Union[Iterable[Iterable[NUM]], Iterable[NUM]]

        Returns:
            Matrix3x3
        '''

        return Matrix3x3(*flatten(t))

    @classmethod
    def from_matrix2x2(
            cls,
            t: Union[Iterable[Iterable[NUM]], Iterable[NUM]]) -> 'Matrix3x3':
        ''' Create a Matrix3x3 from a Matrix2x2

        Args:
            t: Union[Iterable[Iterable[NUM]], Iterable[NUM]]

        Returns:
            Matrix4x4
        '''

        m = Matrix2x2(*Matrix2x2._force_dim(t, use_fill_for_scalar=True))
        matrix = Matrix3x3.identity()
        matrix.column0 = *m.column0, 0.0
        matrix.column1 = *m.column1, 0.0

        return matrix

    @classmethod
    def identity(self) -> 'Matrix3x3':
        ''' Returns a 3x3 identity matrix

        Returns:
            Matrix3x3
        '''

        return Matrix3x3.diagonal(1)

    @classmethod
    def zero(self) -> 'Matrix3x3':
        ''' Returns a 3x3 matrix filled with 0s

        Returns:
            Matrix3x3
        '''

        return Matrix3x3.broadcast(0)

    @classmethod
    def one(self) -> 'Matrix3x3':
        ''' Returns a 3x3 matrix filled with 1s

        Returns:
            Matrix3x3
        '''

        return Matrix3x3.broadcast(1)

    @property
    def m11(self) -> float:
        ''' Get the M11 component of the matrix

        Returns:
            float
        '''

        return self._values[0]

    @m11.setter
    def m11(self, value: NUM):
        self._values[0] = float(value)

    @property
    def m12(self) -> float:
        ''' Get the M12 component of the matrix

        Returns:
            float
        '''

        return self._values[1]

    @m12.setter
    def m12(self, value: NUM):
        self._values[1] = float(value)

    @property
    def m13(self) -> float:
        ''' Get the M13 component of the matrix

        Returns:
            float
        '''

        return self._values[2]

    @m13.setter
    def m13(self, value: NUM):
        self._values[2] = float(value)

    @property
    def m21(self) -> float:
        ''' Get the M21 component of the matrix

        Returns:
            float
        '''

        return self._values[3]

    @m21.setter
    def m21(self, value: NUM):
        self._values[3] = float(value)

    @property
    def m22(self) -> float:
        ''' Get the M22 component of the matrix

        Returns:
            float
        '''

        return self._values[4]

    @m22.setter
    def m22(self, value: NUM):
        self._values[4] = float(value)

    @property
    def m23(self) -> float:
        ''' Get the M23 component of the matrix

        Returns:
            float
        '''

        return self._values[5]

    @m23.setter
    def m23(self, value: NUM):
        self._values[5] = float(value)

    @property
    def m31(self) -> float:
        ''' Get the M31 component of the matrix

        Returns:
            float
        '''

        return self._values[6]

    @m31.setter
    def m31(self, value: NUM):
        self._values[6] = float(value)

    @property
    def m32(self) -> float:
        ''' Get the M32 component of the matrix

        Returns:
            float
        '''

        return self._values[7]

    @m32.setter
    def m32(self, value: NUM):
        self._values[7] = float(value)

    @property
    def m33(self) -> float:
        ''' Get the M33 component of the matrix

        Returns:
            float
        '''

        return self._values[8]

    @m33.setter
    def m33(self, value: NUM):
        self._values[8] = float(value)

    @property
    def column0(self) -> Vector3D:
        ''' Get the first column

        Returns:
            float
        '''

        return Vector3D(self.m11, self.m12, self.m13)

    @column0.setter
    def column0(self, value: MATRIX_TYPE):
        value = self._force_dim_vec(value, (3,))
        self._values[0] = value[0]
        self._values[1] = value[1]
        self._values[2] = value[2]

    @property
    def column1(self) -> Vector3D:
        ''' Get the second column

        Returns:
            float
        '''

        return Vector3D(self.m21, self.m22, self.m23)

    @column1.setter
    def column1(self, value: MATRIX_TYPE):
        value = self._force_dim_vec(value, (3,))
        self._values[3] = value[0]
        self._values[4] = value[1]
        self._values[5] = value[2]

    @property
    def column2(self) -> Vector3D:
        ''' Get the third column

        Returns:
            float
        '''

        return Vector3D(self.m31, self.m32, self.m33)

    @column2.setter
    def column2(self, value: MATRIX_TYPE):
        value = self._force_dim_vec(value, (3,))
        self._values[6] = value[0]
        self._values[7] = value[1]
        self._values[8] = value[2]

    @property
    def row0(self) -> Vector3D:
        ''' Get the first row

        Returns:
            float
        '''

        return Vector3D(self.m11, self.m21, self.m31)

    @row0.setter
    def row0(self, value: MATRIX_TYPE):
        value = self._force_dim_vec(value, (3,))
        self._values[0] = value[0]
        self._values[3] = value[1]
        self._values[6] = value[2]

    @property
    def row1(self) -> Vector3D:
        ''' Get the second row

        Returns:
            float
        '''

        return Vector3D(self.m12, self.m22, self.m32)

    @row1.setter
    def row1(self, value: MATRIX_TYPE):
        value = self._force_dim_vec(value, (3,))
        self._values[1] = value[0]
        self._values[4] = value[1]
        self._values[7] = value[2]

    @property
    def row2(self) -> Vector3D:
        ''' Get the third row

        Returns:
            float
        '''

        return Vector3D(self.m13, self.m23, self.m33)

    @row2.setter
    def row2(self, value: MATRIX_TYPE):
        value = self._force_dim_vec(value, (3,))
        self._values[2] = value[0]
        self._values[5] = value[1]
        self._values[8] = value[2]

    @classmethod
    def _force_dim(
            cls,
            v: MATRIX_TYPE,
            fill: float = 0.0,
            use_fill_for_scalar: bool = False) -> Tuple[NUM]:
        b = hasattr(v, '__iter__')

        if b:
            v = flatten(v)

        if b:
            le = len(v)
            if le == 3:
                v = (v[0], fill, fill,
                     fill, v[1], fill,
                     fill, fill, v[2])
            elif le != 9:
                raise MatrixException(ERROR_3D_MESSAGE) from None
        elif not b:
            with_fill = (
                v, fill, fill,
                fill, v, fill,
                fill, fill, v)
            with_scalar = (
                v, v, v,
                v, v, v,
                v, v, v)

            v = with_fill if use_fill_for_scalar else with_scalar

        return tuple(v)

    @classmethod
    def _force_dim_vec(
            cls, v: MATRIX_TYPE, sizes: Tuple[int] = (3, 9)) -> Tuple[NUM]:
        try:
            v = flatten(v)

            if len(v) not in sizes:
                raise MatrixException(ERROR_3D_MESSAGE) from None

            return tuple(v)
        except ERROR_TUPLE:
            raise MatrixException(ERROR_3D_MESSAGE) from None

    def __add__(self, other: MATRIX_TYPE) -> 'Matrix3x3':
        other = Matrix3x3._force_dim(other)

        m11 = self.m11 + other[0]
        m12 = self.m12 + other[1]
        m13 = self.m13 + other[2]
        m21 = self.m21 + other[3]
        m22 = self.m22 + other[4]
        m23 = self.m23 + other[5]
        m31 = self.m31 + other[6]
        m32 = self.m32 + other[7]
        m33 = self.m33 + other[8]

        return Matrix3x3(
            m11, m12, m13,
            m21, m22, m23,
            m31, m32, m33)

    def __radd__(self, other: MATRIX_TYPE) -> 'Matrix3x3':
        other = Matrix3x3._force_dim(other)

        m11 = other[0] + self.m11
        m12 = other[1] + self.m12
        m13 = other[2] + self.m13
        m21 = other[3] + self.m21
        m22 = other[4] + self.m22
        m23 = other[5] + self.m23
        m31 = other[6] + self.m31
        m32 = other[7] + self.m32
        m33 = other[8] + self.m33

        return Matrix3x3(
            m11, m12, m13,
            m21, m22, m23,
            m31, m32, m33)

    def __sub__(self, other: MATRIX_TYPE) -> 'Matrix3x3':
        other = Matrix3x3._force_dim(other)

        m11 = self.m11 - other[0]
        m12 = self.m12 - other[1]
        m13 = self.m13 - other[2]
        m21 = self.m21 - other[3]
        m22 = self.m22 - other[4]
        m23 = self.m23 - other[5]
        m31 = self.m31 - other[6]
        m32 = self.m32 - other[7]
        m33 = self.m33 - other[8]

        return Matrix3x3(
            m11, m12, m13,
            m21, m22, m23,
            m31, m32, m33)

    def __rsub__(self, other: MATRIX_TYPE) -> 'Matrix3x3':
        other = Matrix3x3._force_dim(other)

        m11 = other[0] - self.m11
        m12 = other[1] - self.m12
        m13 = other[2] - self.m13
        m21 = other[3] - self.m21
        m22 = other[4] - self.m22
        m23 = other[5] - self.m23
        m31 = other[6] - self.m31
        m32 = other[7] - self.m32
        m33 = other[8] - self.m33

        return Matrix3x3(
            m11, m12, m13,
            m21, m22, m23,
            m31, m32, m33)

    def __mul__(self, other: MATRIX_TYPE) -> 'Matrix3x3':
        other = Matrix3x3._force_dim(other)

        m11 = self.m11 * other[0]
        m12 = self.m12 * other[1]
        m13 = self.m13 * other[2]
        m21 = self.m21 * other[3]
        m22 = self.m22 * other[4]
        m23 = self.m23 * other[5]
        m31 = self.m31 * other[6]
        m32 = self.m32 * other[7]
        m33 = self.m33 * other[8]

        return Matrix3x3(
            m11, m12, m13,
            m21, m22, m23,
            m31, m32, m33)

    def __rmul__(self, other: MATRIX_TYPE) -> 'Matrix3x3':
        other = Matrix3x3._force_dim(other)

        m11 = other[0] * self.m11
        m12 = other[1] * self.m12
        m13 = other[2] * self.m13
        m21 = other[3] * self.m21
        m22 = other[4] * self.m22
        m23 = other[5] * self.m23
        m31 = other[6] * self.m31
        m32 = other[7] * self.m32
        m33 = other[8] * self.m33

        return Matrix3x3(
            m11, m12, m13,
            m21, m22, m23,
            m31, m32, m33)

    def __matmul__(self, other: MATRIX_TYPE) -> Union['Matrix3x3', Vector3D]:
        other = Matrix3x3._force_dim_vec(other)

        if len(other) == 9:
            m11 = (self.m11 * other[0] + self.m21 * other[1]
                   + self.m31 * other[2])
            m12 = (self.m12 * other[0] + self.m22 * other[1]
                   + self.m32 * other[2])
            m13 = (self.m13 * other[0] + self.m23 * other[1]
                   + self.m33 * other[2])
            m21 = (self.m11 * other[3] + self.m21 * other[4]
                   + self.m31 * other[5])
            m22 = (self.m12 * other[3] + self.m22 * other[4]
                   + self.m32 * other[5])
            m23 = (self.m13 * other[3] + self.m23 * other[4]
                   + self.m33 * other[5])
            m31 = (self.m11 * other[6] + self.m21 * other[7]
                   + self.m31 * other[8])
            m32 = (self.m12 * other[6] + self.m22 * other[7]
                   + self.m32 * other[8])
            m33 = (self.m13 * other[6] + self.m23 * other[7]
                   + self.m33 * other[8])

            return Matrix3x3(
                m11, m12, m13,
                m21, m22, m23,
                m31, m32, m33)
        else:
            x = self.m11 * other[0] + self.m21 * other[1] + self.m31 * other[2]
            y = self.m12 * other[0] + self.m22 * other[1] + self.m32 * other[2]
            z = self.m13 * other[0] + self.m23 * other[1] + self.m33 * other[2]

            return Vector3D(x, y, z)

    def __rmatmul__(self, other: MATRIX_TYPE) -> Union['Matrix3x3', Vector3D]:
        other = Matrix3x3._force_dim_vec(other)

        if len(other) == 9:
            m11 = (other[0] * self.m11 + other[3] * self.m12
                   + other[6] * self.m13)
            m12 = (other[1] * self.m11 + other[4] * self.m12
                   + other[7] * self.m13)
            m13 = (other[2] * self.m11 + other[5] * self.m12
                   + other[8] * self.m13)
            m21 = (other[0] * self.m21 + other[3] * self.m22
                   + other[6] * self.m23)
            m22 = (other[1] * self.m21 + other[4] * self.m22
                   + other[7] * self.m23)
            m23 = (other[2] * self.m21 + other[5] * self.m22
                   + other[8] * self.m23)
            m31 = (other[0] * self.m31 + other[3] * self.m32
                   + other[6] * self.m33)
            m32 = (other[1] * self.m31 + other[4] * self.m32
                   + other[7] * self.m33)
            m33 = (other[2] * self.m31 + other[5] * self.m32
                   + other[8] * self.m33)

            return Matrix3x3(
                m11, m12, m13,
                m21, m22, m23,
                m31, m32, m33)
        else:
            raise MatrixException(ERROR_3D_MESSAGE)

    def __truediv__(self, other: MATRIX_TYPE) -> 'Matrix3x3':
        other = Matrix3x3._force_dim(other, 1.0)

        m11 = self.m11 / other[0]
        m12 = self.m12 / other[1]
        m13 = self.m13 / other[2]
        m21 = self.m21 / other[3]
        m22 = self.m22 / other[4]
        m23 = self.m23 / other[5]
        m31 = self.m31 / other[6]
        m32 = self.m32 / other[7]
        m33 = self.m33 / other[8]

        return Matrix3x3(
            m11, m12, m13,
            m21, m22, m23,
            m31, m32, m33)

    def __rtruediv__(self, other: MATRIX_TYPE) -> 'Matrix3x3':
        other = Matrix3x3._force_dim(other, 1.0)

        m11 = other[0] / self.m11
        m12 = other[1] / self.m12
        m13 = other[2] / self.m13
        m21 = other[3] / self.m21
        m22 = other[4] / self.m22
        m23 = other[5] / self.m23
        m31 = other[6] / self.m31
        m32 = other[7] / self.m32
        m33 = other[8] / self.m33

        return Matrix3x3(
            m11, m12, m13,
            m21, m22, m23,
            m31, m32, m33)

    def __floordiv__(self, other: MATRIX_TYPE) -> 'Matrix3x3':
        other = Matrix3x3._force_dim(other, 1.0)

        m11 = self.m11 // other[0]
        m12 = self.m12 // other[1]
        m13 = self.m13 // other[2]
        m21 = self.m21 // other[3]
        m22 = self.m22 // other[4]
        m23 = self.m23 // other[5]
        m31 = self.m31 // other[6]
        m32 = self.m32 // other[7]
        m33 = self.m33 // other[8]

        return Matrix3x3(
            m11, m12, m13,
            m21, m22, m23,
            m31, m32, m33)

    def __rfloordiv__(self, other: MATRIX_TYPE) -> 'Matrix3x3':
        other = Matrix3x3._force_dim(other, 1.0)

        m11 = other[0] // self.m11
        m12 = other[1] // self.m12
        m13 = other[2] // self.m13
        m21 = other[3] // self.m21
        m22 = other[4] // self.m22
        m23 = other[5] // self.m23
        m31 = other[6] // self.m31
        m32 = other[7] // self.m32
        m33 = other[8] // self.m33

        return Matrix3x3(
            m11, m12, m13,
            m21, m22, m23,
            m31, m32, m33)

    def __abs__(self) -> 'Matrix3x3':
        m11 = abs(self.m11)
        m12 = abs(self.m12)
        m13 = abs(self.m13)
        m21 = abs(self.m21)
        m22 = abs(self.m22)
        m23 = abs(self.m23)
        m31 = abs(self.m31)
        m32 = abs(self.m32)
        m33 = abs(self.m33)

        return Matrix3x3(
            m11, m12, m13,
            m21, m22, m23,
            m31, m32, m33)

    def __mod__(self, other: MATRIX_TYPE) -> 'Matrix3x3':
        if hasattr(other, '__iter__') and len(other) == 3:
            return Matrix3x3(
                self.m11 % float(other[0]),
                self.m12,
                self.m13,
                self.m21,
                self.m22 % float(other[1]),
                self.m23,
                self.m31,
                self.m32,
                self.m33 % float(other[2]))

        other = Matrix3x3._force_dim(other)

        m11 = self.m11 % other[0]
        m12 = self.m12 % other[1]
        m13 = self.m13 % other[2]
        m21 = self.m21 % other[3]
        m22 = self.m22 % other[4]
        m23 = self.m23 % other[5]
        m31 = self.m31 % other[6]
        m32 = self.m32 % other[7]
        m33 = self.m33 % other[8]

        return Matrix3x3(
            m11, m12, m13,
            m21, m22, m23,
            m31, m32, m33)

    def __pow__(self, other: MATRIX_TYPE) -> 'Matrix3x3':
        other = Matrix3x3._force_dim(other)

        m11 = self.m11 ** other[0]
        m12 = self.m12 ** other[1]
        m13 = self.m13 ** other[2]
        m21 = self.m21 ** other[3]
        m22 = self.m22 ** other[4]
        m23 = self.m23 ** other[5]
        m31 = self.m31 ** other[6]
        m32 = self.m32 ** other[7]
        m33 = self.m33 ** other[8]

        return Matrix3x3(
            m11, m12, m13,
            m21, m22, m23,
            m31, m32, m33)

    def __pos__(self) -> 'Matrix3x3':
        return Matrix3x3(
            +self.m11, +self.m12, +self.m13,
            +self.m21, +self.m22, +self.m23,
            +self.m31, +self.m32, +self.m33)

    def __neg__(self) -> 'Matrix3x3':
        return Matrix3x3(
            -self.m11, -self.m12, -self.m13,
            -self.m21, -self.m22, -self.m23,
            -self.m31, -self.m32, -self.m33)

    def __getitem__(
            self, index: Union[int, slice]) -> Union[List[Vector3D], Vector3D]:

        def _get(index: int) -> Vector3D:
            if index == 0 or index == -3:
                return Vector3D(self.m11, self.m12, self.m13)
            elif index == 1 or index == -2:
                return Vector3D(self.m21, self.m22, self.m23)
            elif index == 2 or index == -1:
                return Vector3D(self.m31, self.m32, self.m33)
            else:
                raise IndexError(ERROR_3D_INDEX_MESSAGE) from None

        if isinstance(index, slice):
            return [_get(i) for i in range(*index.indices(len(self)))]
        else:
            return _get(index)

    def __setitem__(
            self,
            index: Union[int, slice],
            value: MATRIX_TYPE):

        def _set(index: int, value: MATRIX_TYPE):
            value = self._force_dim_vec(value, (3,))

            if index == 0 or index == -3:
                self.m11 = value[0]
                self.m12 = value[1]
                self.m13 = value[2]
            elif index == 1 or index == -2:
                self.m21 = value[0]
                self.m22 = value[1]
                self.m23 = value[2]
            elif index == 2 or index == -1:
                self.m31 = value[0]
                self.m32 = value[1]
                self.m33 = value[2]
            else:
                raise IndexError(ERROR_3D_INDEX_MESSAGE) from None

        def _set2(index: Union[int, slice], value: MATRIX_TYPE):
            if isinstance(index, slice):
                value = tuple(value)
                for i in range(*index.indices(len(self))):
                    if (hasattr(value, '__iter__')
                            and hasattr(value[i], '__iter__')):
                        _set(i, value[i])
                    else:
                        _set(i, value)
            else:
                _set(index, value)

        safe_matrix3x3_op(_set2, index, value)

    def __iter__(self) -> Iterator[Vector3D]:
        yield Vector3D(self.m11, self.m12, self.m13)
        yield Vector3D(self.m21, self.m22, self.m23)
        yield Vector3D(self.m31, self.m32, self.m33)

    def __len__(self) -> int:
        return 3

    def __format__(self, format_spec: str) -> str:
        m11 = format(self.m11, format_spec)
        m12 = format(self.m12, format_spec)
        m13 = format(self.m13, format_spec)
        m21 = format(self.m21, format_spec)
        m22 = format(self.m22, format_spec)
        m23 = format(self.m23, format_spec)
        m31 = format(self.m31, format_spec)
        m32 = format(self.m32, format_spec)
        m33 = format(self.m33, format_spec)

        return ('({}, {}, {},\n'
                ' {}, {}, {},\n'
                ' {}, {}, {})').format(
                    m11, m21, m31,
                    m12, m22, m32,
                    m13, m23, m33)

    def __repr__(self) -> str:
        return ('Matrix3x3'
                '({}, {}, {},'
                ' {}, {}, {},'
                ' {}, {}, {})').format(
                    self.m11, self.m12, self.m13,
                    self.m21, self.m22, self.m23,
                    self.m31, self.m32, self.m33)

    def __eq__(
            self,
            value: MATRIX_TYPE) -> Tuple[bool]:
        try:
            values = self._force_dim(value)
            return tuple(
                map(lambda t: t[0] == t[1], zip(self._values, values)))
        except ValueError:
            raise MatrixException(ERROR_3D_MESSAGE) from None

    def __lt__(
            self,
            value: MATRIX_TYPE) -> Tuple[bool]:
        try:
            values = self._force_dim(value)
            return tuple(
                map(lambda t: t[0] < t[1], zip(self._values, values)))
        except ValueError:
            raise MatrixException(ERROR_3D_MESSAGE) from None

    def __le__(
            self,
            value: MATRIX_TYPE) -> Tuple[bool]:
        try:
            values = self._force_dim(value)
            return tuple(
                map(lambda t: t[0] <= t[1], zip(self._values, values)))
        except ValueError:
            raise MatrixException(ERROR_3D_MESSAGE) from None

    def __gt__(
            self,
            value: MATRIX_TYPE) -> Tuple[bool]:
        try:
            values = self._force_dim(value)
            return tuple(
                map(lambda t: t[0] > t[1], zip(self._values, values)))
        except ValueError:
            raise MatrixException(ERROR_3D_MESSAGE) from None

    def __ge__(
            self,
            value: MATRIX_TYPE) -> Tuple[bool]:
        try:
            values = self._force_dim(value)
            return tuple(
                map(lambda t: t[0] >= t[1], zip(self._values, values)))
        except ValueError:
            raise MatrixException(ERROR_3D_MESSAGE) from None

    @classmethod
    def clear_rotation(cls, value: MATRIX_TYPE) -> 'Matrix3x3':
        ''' Clears the rotation from a transformation matrix

        Args:
            value (MATRIX_TYPE): 3x3 input matrix

        Returns:
            Matrix3x3
        '''

        value = Matrix3x3._force_dim(value, use_fill_for_scalar=True)
        value = Matrix3x3(*value)

        col0 = value.column0
        col1 = value.column1
        col2 = value.column2

        value.column0 = Vector3D.length(col0), 0, 0
        value.column1 = 0, Vector3D.length(col1), 0
        value.column2 = 0, 0, Vector3D.length(col2)

        return value

    @classmethod
    def clear_scale(cls, value: MATRIX_TYPE) -> 'Matrix3x3':
        ''' Clears the scale from a transformation matrix

        Args:
            value (MATRIX_TYPE): 3x3 input matrix

        Returns:
            Matrix3x3
        '''

        value = Matrix3x3._force_dim(value, use_fill_for_scalar=True)
        value = Matrix3x3(*value)

        value.column0 = Vector3D.normalize(value.column0)
        value.column1 = Vector3D.normalize(value.column1)
        value.column2 = Vector3D.normalize(value.column2)

        return value

    @classmethod
    def rotation_x(cls, angle: NUM) -> 'Matrix3x3':
        ''' Creates a rotation matrix for rotating about the x-axis

        Args:
            angle (NUM): angle in radians to rotate by

        Returns:
            Matrix3x3
        '''

        cos = math.cos(angle)
        sin = math.sin(angle)

        result = Matrix3x3.identity()
        result.m22 = cos
        result.m23 = sin
        result.m32 = -sin
        result.m33 = cos

        return result

    @classmethod
    def rotation_y(cls, angle: NUM) -> 'Matrix3x3':
        ''' Creates a rotation matrix for rotating about the y-axis

        Args:
            angle (NUM): angle in radians to rotate by

        Returns:
            Matrix3x3
        '''

        cos = math.cos(angle)
        sin = math.sin(angle)

        result = Matrix3x3.identity()
        result.m11 = cos
        result.m13 = -sin
        result.m31 = sin
        result.m33 = cos

        return result

    @classmethod
    def rotation_z(cls, angle: NUM) -> 'Matrix3x3':
        ''' Creates a rotation matrix for rotating about the z-axis

        Args:
            angle (NUM): angle in radians to rotate by

        Returns:
            Matrix3x3
        '''

        cos = math.cos(angle)
        sin = math.sin(angle)

        result = Matrix3x3.identity()
        result.m11 = cos
        result.m12 = sin
        result.m21 = -sin
        result.m22 = cos

        return result

    @classmethod
    def rotation(
            cls, axis: Iterable[NUM], angle: NUM) -> 'Matrix3x3':
        ''' Creates a rotation matrix for rotating about a 3D axis

        Args:
            axis (Iterable[NUM]): 3D axis to rotate about
            angle (NUM): angle in radians to rotate by

        Returns:
            Matrix3x3
        '''

        axis = Matrix3x3._force_dim_vec(axis, (3,))
        axis = Vector3D.normalize(axis)

        cos = math.cos(-angle)
        sin = math.sin(-angle)
        t = 1.0 - cos

        txx = t * axis.x * axis.x
        txy = t * axis.x * axis.y
        txz = t * axis.x * axis.z
        tyy = t * axis.y * axis.y
        tyz = t * axis.y * axis.z
        tzz = t * axis.z * axis.z

        sinx = sin * axis.x
        siny = sin * axis.y
        sinz = sin * axis.z

        result = Matrix3x3.identity()
        result.column0 = txx + cos, txy - sinz, txz + siny
        result.column1 = txy + sinz, tyy + cos, tyz - sinx
        result.column2 = txz - siny, tyz + sinx, tzz + cos

        return result

    @classmethod
    def scale(cls, x: NUM = 1.0, y: NUM = 1.0, z: NUM = 1.0) -> 'Matrix3x3':
        ''' Creates a scale matrix

        Args:
            x (NUM, default=1.0): x-scale
            y (NUM, default=1.0): y-scale
            z (NUM, default=1.0): z-scale

        Returns:
            Matrix3x3
        '''

        result = Matrix3x3.identity()
        result.m11 = x
        result.m22 = y
        result.m33 = z
        return result

    @classmethod
    def _determinant(cls, value: 'Matrix3x3') -> float:
        a = value[0]
        b = value[3]
        c = value[6]

        x = value[4] * value[8] - value[7] * value[5]
        y = value[1] * value[8] - value[7] * value[2]
        z = value[1] * value[5] - value[4] * value[2]

        return a * x - b * y + c * z

    @classmethod
    def determinant(cls, value: MATRIX_TYPE) -> float:
        '''Determinant of a 3x3 matrix.

        Args:
            value (MATRIX_TYPE): 3x3 input matrix

        Returns:
            float
        '''

        value = cls._force_dim(value, use_fill_for_scalar=True)
        return cls._determinant(value)

    @classmethod
    def _transpose(cls, value: 'Matrix3x3') -> 'Matrix3x3':
        return Matrix3x3(
            value[0], value[3], value[6],
            value[1], value[4], value[7],
            value[2], value[5], value[8])

    @classmethod
    def transpose(cls, value: MATRIX_TYPE) -> 'Matrix3x3':
        '''Transpose of a 3x3 matrix.

        Args:
            value (MATRIX_TYPE): 3x3 input matrix

        Returns:
            float
        '''

        value = cls._force_dim(value, use_fill_for_scalar=True)
        return cls._transpose(value)

    @classmethod
    def inverse(cls, value: MATRIX_TYPE) -> 'Matrix3x3':
        '''Inverse of a 3x3 matrix.

        Args:
            value (MATRIX_TYPE): 3x3 input matrix

        Returns:
            float
        '''

        value = cls._force_dim(value, use_fill_for_scalar=True)
        det = cls._determinant(value)

        if det == 0.0:
            raise MatrixException('Matrix has no inverse.')

        d11 = Matrix2x2._determinant((value[4], value[7], value[5], value[8]))
        d21 = Matrix2x2._determinant((value[3], value[6], value[5], value[8]))
        d31 = Matrix2x2._determinant((value[3], value[6], value[4], value[7]))
        d12 = Matrix2x2._determinant((value[1], value[7], value[2], value[8]))
        d22 = Matrix2x2._determinant((value[0], value[6], value[2], value[8]))
        d32 = Matrix2x2._determinant((value[0], value[6], value[1], value[7]))
        d13 = Matrix2x2._determinant((value[1], value[4], value[2], value[5]))
        d23 = Matrix2x2._determinant((value[0], value[3], value[2], value[5]))
        d33 = Matrix2x2._determinant((value[0], value[3], value[1], value[4]))

        adjugate = Matrix3x3(
            d11, -d21, d31,
            -d12, d22, -d32,
            d13, -d23, d33)

        return adjugate / det

    @classmethod
    def normalize(cls, value: MATRIX_TYPE) -> 'Matrix3x3':
        ''' Matrix normalization.

        Args:
            value (MATRIX_TYPE): Matrix to evaluate.

        Returns:
            Matrix3x3
        '''

        value = cls._force_dim(value, use_fill_for_scalar=True)
        det = cls._determinant(value)

        value = Matrix3x3(*value)
        value.column0 /= det
        value.column1 /= det
        value.column2 /= det

        return value
