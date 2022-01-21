'''matrix_4x4.py'''


import math
from typing import Union, Iterable, Iterator, Tuple, List, Any

from mastapy._math.matrix_base import (
    MatrixBase, flatten, MATRIX_TYPE, MatrixException,
    ERROR_TUPLE, _safe_matrix_op)
from mastapy._math.matrix_2x2 import Matrix2x2
from mastapy._math.matrix_3x3 import Matrix3x3
from mastapy._math.vector_3d import Vector3D
from mastapy._math.vector_4d import Vector4D
from mastapy._math.scalar import NUM


__all__ = ('Matrix4x4',)


ERROR_4D_MESSAGE = 'Vector must match matrix4x4 dimension.'
ERROR_4D_INDEX_MESSAGE = 'Invalid column index. There are only 4 columns.'
ERROR_4D_SET_PROPERTY = ('Cannot set W component of Matrix4x4 column '
                         'that is directly linked to a property '
                         'derived from Masta.')
safe_matrix4x4_op = _safe_matrix_op(ERROR_4D_MESSAGE)


def _convert(mp_vector3d):
    ''' Slight hack to force lazy loading on import '''

    from mastapy._internal.conversion import mp_to_pn_vector3d
    return mp_to_pn_vector3d(mp_vector3d)


class Matrix4x4(MatrixBase):
    ''' Create a column-major Matrix4x4 from M11, M12, M13, M14, M21, M22,
    M23, M24, M31, M32, M33, M34, M41, M42, M43, M44 components.

    Args:
        m11: NUM
        m12: NUM
        m13: NUM
        m14: NUM
        m21: NUM
        m22: NUM
        m23: NUM
        m24: NUM
        m31: NUM
        m32: NUM
        m33: NUM
        m34: NUM
        m41: NUM
        m42: NUM
        m43: NUM
        m44: NUM

    Returns:
        Matrix4x4
    '''

    def __init__(
            self,
            m11: NUM, m12: NUM, m13: NUM, m14: NUM,
            m21: NUM, m22: NUM, m23: NUM, m24: NUM,
            m31: NUM, m32: NUM, m33: NUM, m34: NUM,
            m41: NUM, m42: NUM, m43: NUM, m44: NUM) -> 'Matrix4x4':
        self.wrapped = None
        super().__init__([
            float(m11), float(m12), float(m13), float(m14),
            float(m21), float(m22), float(m23), float(m24),
            float(m31), float(m32), float(m33), float(m34),
            float(m41), float(m42), float(m43), float(m44)])

    @classmethod
    def broadcast(cls, value: NUM) -> 'Matrix4x4':
        ''' Create a Matrix4x4 by broadcasting a value to all of its components

        Args:
            value: NUM

        Returns:
            Matrix4x4
        '''

        return cls(
            value, value, value, value,
            value, value, value, value,
            value, value, value, value,
            value, value, value, value)

    @classmethod
    def diagonal(cls, value: Union[NUM, Iterable[NUM]]) -> 'Matrix4x4':
        ''' Create a Matrix4x4 by broadcasting a value along the diagonal

        Args:
            value: Union[NUM, Iterable[NUM]]

        Returns:
            Matrix4x4
        '''

        if hasattr(value, '__iter__'):
            value = tuple(value)
            if len(value) != 4:
                raise MatrixException(ERROR_4D_MESSAGE)
            return cls(
                value[0], 0.0, 0.0, 0.0,
                0.0, value[1], 0.0, 0.0,
                0.0, 0.0, value[2], 0.0,
                0.0, 0.0, 0.0, value[3])
        return cls(
            value, 0.0, 0.0, 0.0,
            0.0, value, 0.0, 0.0,
            0.0, 0.0, value, 0.0,
            0.0, 0.0, 0.0, value)

    @classmethod
    def from_iterable(
            cls,
            t: Union[Iterable[Iterable[NUM]], Iterable[NUM]]) -> 'Matrix4x4':
        ''' Create a Matrix4x4 from an iterable

        Args:
            t: Union[Iterable[Iterable[NUM]], Iterable[NUM]]

        Returns:
            Matrix4x4
        '''

        return t if isinstance(t, Matrix4x4) else Matrix4x4(*flatten(t))

    @classmethod
    def from_matrix2x2(
            cls,
            t: Union[Iterable[Iterable[NUM]], Iterable[NUM]]) -> 'Matrix4x4':
        ''' Create a Matrix4x4 from a Matrix2x2

        Args:
            t: Union[Iterable[Iterable[NUM]], Iterable[NUM]]

        Returns:
            Matrix4x4
        '''

        m = Matrix2x2(*Matrix2x2._force_dim(t, use_fill_for_scalar=True))
        matrix = Matrix4x4.identity()
        matrix.column0 = *m.column0, 0.0, 0.0
        matrix.column1 = *m.column1, 0.0, 0.0

        return matrix

    @classmethod
    def from_matrix3x3(
            cls,
            t: Union[Iterable[Iterable[NUM]], Iterable[NUM]]) -> 'Matrix4x4':
        ''' Create a Matrix4x4 from a Matrix3x3

        Args:
            t: Union[Iterable[Iterable[NUM]], Iterable[NUM]]

        Returns:
            Matrix4x4
        '''

        m = Matrix3x3(*Matrix3x3._force_dim(t, use_fill_for_scalar=True))
        matrix = Matrix4x4.identity()
        matrix.column0 = *m.column0, 0.0
        matrix.column1 = *m.column1, 0.0
        matrix.column2 = *m.column2, 0.0

        return matrix

    @classmethod
    def wrap(cls, value: Any) -> 'Matrix4x4':
        try:
            new_matrix = Matrix4x4.identity()

            x = value.XAxis
            y = value.YAxis
            z = value.ZAxis
            w = value.Translation

            new_matrix.column0 = (x.X, x.Y, x.Z, 0.0)
            new_matrix.column1 = (y.X, y.Y, y.Z, 0.0)
            new_matrix.column2 = (z.X, z.Y, z.Z, 0.0)
            new_matrix.column3 = (w.X, w.Y, w.Z, 1.0)
            new_matrix.wrapped = value

            return new_matrix
        except AttributeError:
            raise MatrixException('Value to wrap has no X, Y or Z component.')

    @classmethod
    def identity(self) -> 'Matrix4x4':
        ''' Returns a 4x4 identity matrix

        Returns:
            Matrix4x4
        '''

        return Matrix4x4.diagonal(1)

    @classmethod
    def zero(self) -> 'Matrix4x4':
        ''' Returns a 4x4 matrix filled with 0s

        Returns:
            Matrix4x4
        '''

        return Matrix4x4.broadcast(0)

    @classmethod
    def one(self) -> 'Matrix4x4':
        ''' Returns a 4x4 matrix filled with 1s

        Returns:
            Matrix4x4
        '''

        return Matrix4x4.broadcast(1)

    @property
    def m11(self) -> float:
        ''' Get the M11 component of the matrix

        Returns:
            float
        '''

        if self.wrapped:
            self._values[0] = float(self.wrapped.XAxis.X)

        return self._values[0]

    @m11.setter
    def m11(self, value: NUM):
        if self.wrapped:
            self.wrapped.XAxis = _convert((value, self.m12, self.m13))

        self._values[0] = float(value)

    @property
    def m12(self) -> float:
        ''' Get the M12 component of the matrix

        Returns:
            float
        '''

        if self.wrapped:
            self._values[1] = float(self.wrapped.XAxis.Y)

        return self._values[1]

    @m12.setter
    def m12(self, value: NUM):
        if self.wrapped:
            self.wrapped.XAxis = _convert((self.m11, value, self.m13))

        self._values[1] = float(value)

    @property
    def m13(self) -> float:
        ''' Get the M13 component of the matrix

        Returns:
            float
        '''

        if self.wrapped:
            self._values[2] = float(self.wrapped.XAxis.Z)

        return self._values[2]

    @m13.setter
    def m13(self, value: NUM):
        if self.wrapped:
            self.wrapped.XAxis = _convert((self.m11, self.m12, value))

        self._values[2] = float(value)

    @property
    def m14(self) -> float:
        ''' Get the M14 component of the matrix

        Returns:
            float
        '''

        if self.wrapped:
            self._values[3] = 0.0

        return self._values[3]

    @m14.setter
    def m14(self, value: NUM):
        if self.wrapped:
            raise MatrixException(ERROR_4D_SET_PROPERTY) from None

        self._values[3] = float(value)

    @property
    def m21(self) -> float:
        ''' Get the M21 component of the matrix

        Returns:
            float
        '''

        if self.wrapped:
            self._values[4] = float(self.wrapped.YAxis.X)

        return self._values[4]

    @m21.setter
    def m21(self, value: NUM):
        if self.wrapped:
            self.wrapped.YAxis = _convert((value, self.m22, self.m23))

        self._values[4] = float(value)

    @property
    def m22(self) -> float:
        ''' Get the M22 component of the matrix

        Returns:
            float
        '''

        if self.wrapped:
            self._values[5] = float(self.wrapped.YAxis.Y)

        return self._values[5]

    @m22.setter
    def m22(self, value: NUM):
        if self.wrapped:
            self.wrapped.YAxis = _convert((self.m21, value, self.m23))

        self._values[5] = float(value)

    @property
    def m23(self) -> float:
        ''' Get the M23 component of the matrix

        Returns:
            float
        '''

        if self.wrapped:
            self._values[6] = float(self.wrapped.YAxis.Z)

        return self._values[6]

    @m23.setter
    def m23(self, value: NUM):
        if self.wrapped:
            self.wrapped.YAxis = _convert((self.m21, self.m22, value))

        self._values[6] = float(value)

    @property
    def m24(self) -> float:
        ''' Get the M24 component of the matrix

        Returns:
            float
        '''

        if self.wrapped:
            self._values[7] = 0.0

        return self._values[7]

    @m24.setter
    def m24(self, value: NUM):
        if self.wrapped:
            raise MatrixException(ERROR_4D_SET_PROPERTY) from None

        self._values[7] = float(value)

    @property
    def m31(self) -> float:
        ''' Get the M31 component of the matrix

        Returns:
            float
        '''

        if self.wrapped:
            self._values[8] = float(self.wrapped.ZAxis.X)

        return self._values[8]

    @m31.setter
    def m31(self, value: NUM):
        if self.wrapped:
            self.wrapped.ZAxis = _convert((value, self.m32, self.m33))

        self._values[8] = float(value)

    @property
    def m32(self) -> float:
        ''' Get the M32 component of the matrix

        Returns:
            float
        '''

        if self.wrapped:
            self._values[9] = float(self.wrapped.ZAxis.Y)

        return self._values[9]

    @m32.setter
    def m32(self, value: NUM):
        if self.wrapped:
            self.wrapped.ZAxis = _convert((self.m31, value, self.m33))

        self._values[9] = float(value)

    @property
    def m33(self) -> float:
        ''' Get the M33 component of the matrix

        Returns:
            float
        '''

        if self.wrapped:
            self._values[10] = float(self.wrapped.ZAxis.Z)

        return self._values[10]

    @m33.setter
    def m33(self, value: NUM):
        if self.wrapped:
            self.wrapped.ZAxis = _convert((self.m31, self.m32, value))

        self._values[10] = float(value)

    @property
    def m34(self) -> float:
        ''' Get the M34 component of the matrix

        Returns:
            float
        '''

        if self.wrapped:
            self._values[11] = 0.0

        return self._values[11]

    @m34.setter
    def m34(self, value: NUM):
        if self.wrapped:
            raise MatrixException(ERROR_4D_SET_PROPERTY) from None

        self._values[11] = float(value)

    @property
    def m41(self) -> float:
        ''' Get the M41 component of the matrix

        Returns:
            float
        '''

        if self.wrapped:
            self._values[12] = float(self.wrapped.Translation.X)

        return self._values[12]

    @m41.setter
    def m41(self, value: NUM):
        if self.wrapped:
            self.wrapped.Translation = _convert(
                (value, self.m42, self.m43))

        self._values[12] = float(value)

    @property
    def m42(self) -> float:
        ''' Get the M42 component of the matrix

        Returns:
            float
        '''

        if self.wrapped:
            self._values[13] = float(self.wrapped.Translation.Y)

        return self._values[13]

    @m42.setter
    def m42(self, value: NUM):
        if self.wrapped:
            self.wrapped.Translation = _convert(
                (self.m41, value, self.m43))

        self._values[13] = float(value)

    @property
    def m43(self) -> float:
        ''' Get the M43 component of the matrix

        Returns:
            float
        '''

        if self.wrapped:
            self._values[14] = float(self.wrapped.Translation.Z)

        return self._values[14]

    @m43.setter
    def m43(self, value: NUM):
        if self.wrapped:
            self.wrapped.Translation = _convert(
                (self.m41, self.m42, value))

        self._values[14] = float(value)

    @property
    def m44(self) -> float:
        ''' Get the M44 component of the matrix

        Returns:
            float
        '''

        if self.wrapped:
            self._values[15] = 1.0

        return self._values[15]

    @m44.setter
    def m44(self, value: NUM):
        if self.wrapped:
            raise MatrixException(ERROR_4D_SET_PROPERTY) from None

        self._values[15] = float(value)

    @property
    def column0(self) -> Vector4D:
        ''' Get the first column

        Returns:
            float
        '''
        return Vector4D(self.m11, self.m12, self.m13, self.m14)

    @column0.setter
    def column0(self, value: MATRIX_TYPE):
        value = self._force_dim_vec(value, (3, 4))

        if len(value) == 3:
            value = (*value, 0.0)

        if self.wrapped:
            self.wrapped.XAxis = _convert(
                (value[0], value[1], value[2]))

        self._values[0] = value[0]
        self._values[1] = value[1]
        self._values[2] = value[2]
        self._values[3] = value[3]

    @property
    def column1(self) -> Vector4D:
        ''' Get the second column

        Returns:
            float
        '''

        return Vector4D(self.m21, self.m22, self.m23, self.m24)

    @column1.setter
    def column1(self, value: MATRIX_TYPE):
        value = self._force_dim_vec(value, (3, 4))

        if len(value) == 3:
            value = (*value, 0.0)

        if self.wrapped:
            self.wrapped.YAxis = _convert(
                (value[0], value[1], value[2]))

        self._values[4] = value[0]
        self._values[5] = value[1]
        self._values[6] = value[2]
        self._values[7] = value[3]

    @property
    def column2(self) -> Vector4D:
        ''' Get the third column

        Returns:
            float
        '''

        return Vector4D(self.m31, self.m32, self.m33, self.m34)

    @column2.setter
    def column2(self, value: MATRIX_TYPE):
        value = self._force_dim_vec(value, (3, 4))

        if len(value) == 3:
            value = (*value, 0.0)

        if self.wrapped:
            self.wrapped.ZAxis = _convert(
                (value[0], value[1], value[2]))

        self._values[8] = value[0]
        self._values[9] = value[1]
        self._values[10] = value[2]
        self._values[11] = value[3]

    @property
    def column3(self) -> Vector4D:
        ''' Get the fourth column (translation)

        Returns:
            float
        '''

        return Vector4D(self.m41, self.m42, self.m43, self.m44)

    @column3.setter
    def column3(self, value: MATRIX_TYPE):
        value = self._force_dim_vec(value, (3, 4))

        if len(value) == 3:
            value = (*value, 1.0)

        if self.wrapped:
            self.wrapped.Translation = _convert(
                (value[0], value[1], value[2]))

        self._values[12] = value[0]
        self._values[13] = value[1]
        self._values[14] = value[2]
        self._values[15] = value[3]

    @property
    def row0(self) -> Vector4D:
        ''' Get the first row

        Returns:
            float
        '''

        return Vector4D(self.m11, self.m21, self.m31, self.m41)

    @row0.setter
    def row0(self, value: MATRIX_TYPE):
        value = self._force_dim_vec(value, (4,))

        if self.wrapped:
            self.wrapped.XAxis = _convert(
                (value[0], self.m12, self.m13))
            self.wrapped.YAxis = _convert(
                (value[1], self.m22, self.m23))
            self.wrapped.ZAxis = _convert(
                (value[2], self.m32, self.m33))
            self.wrapped.Translation = _convert(
                (value[3], self.m42, self.m43))

        self._values[0] = value[0]
        self._values[4] = value[1]
        self._values[8] = value[2]
        self._values[12] = value[3]

    @property
    def row1(self) -> Vector4D:
        ''' Get the second row

        Returns:
            float
        '''

        return Vector4D(self.m12, self.m22, self.m32, self.m42)

    @row1.setter
    def row1(self, value: MATRIX_TYPE):
        value = self._force_dim_vec(value, (4,))

        if self.wrapped:
            self.wrapped.XAxis = _convert(
                (self.m11, value[0], self.m13))
            self.wrapped.YAxis = _convert(
                (self.m21, value[1], self.m23))
            self.wrapped.ZAxis = _convert(
                (self.m31, value[2], self.m33))
            self.wrapped.Translation = _convert(
                (self.m41, value[3], self.m43))

        self._values[1] = value[0]
        self._values[5] = value[1]
        self._values[9] = value[2]
        self._values[13] = value[3]

    @property
    def row2(self) -> Vector4D:
        ''' Get the third row

        Returns:
            float
        '''

        return Vector4D(self.m13, self.m23, self.m33, self.m43)

    @row2.setter
    def row2(self, value: MATRIX_TYPE):
        value = self._force_dim_vec(value, (4,))

        if self.wrapped:
            self.wrapped.XAxis = _convert(
                (self.m11, self.m12, value[0]))
            self.wrapped.YAxis = _convert(
                (self.m21, self.m22, value[1]))
            self.wrapped.ZAxis = _convert(
                (self.m31, self.m32, value[2]))
            self.wrapped.Translation = _convert(
                (self.m41, self.m42, value[3]))

        self._values[2] = value[0]
        self._values[6] = value[1]
        self._values[10] = value[2]
        self._values[14] = value[3]

    @property
    def row3(self) -> Vector4D:
        ''' Get the fourth row

        Returns:
            float
        '''

        return Vector4D(self.m14, self.m24, self.m34, self.m44)

    @row3.setter
    def row3(self, value: MATRIX_TYPE):
        value = self._force_dim_vec(value, (4,))

        if self.wrapped:
            raise MatrixException(ERROR_4D_SET_PROPERTY) from None

        self._values[3] = value[0]
        self._values[7] = value[1]
        self._values[11] = value[2]
        self._values[15] = value[3]

    @classmethod
    def _force_dim(
            cls,
            v: MATRIX_TYPE,
            fill: float = 0.0,
            use_fill_for_scalar: bool = False) -> 'Matrix4x4':

        if isinstance(v, Matrix4x4):
            return v

        b = hasattr(v, '__iter__')

        if b:
            v = flatten(v)

        if b:
            le = len(v)
            if le == 4:
                v = Matrix4x4(
                     v[0], fill, fill, fill,
                     fill, v[1], fill, fill,
                     fill, fill, v[2], fill,
                     fill, fill, fill, v[3])
            elif le == 16:
                v = Matrix4x4.from_iterable(v)
            else:
                raise MatrixException(ERROR_4D_MESSAGE) from None
        elif not b:
            with_fill = Matrix4x4(
                v, fill, fill, fill,
                fill, v, fill, fill,
                fill, fill, v, fill,
                fill, fill, fill, v)
            with_scalar = Matrix4x4(
                v, v, v, v,
                v, v, v, v,
                v, v, v, v,
                v, v, v, v)

            v = with_fill if use_fill_for_scalar else with_scalar

        return v

    @classmethod
    def _force_dim_vec(
            cls, v: MATRIX_TYPE, sizes: Tuple[int] = (4, 16)) -> Tuple[NUM]:
        try:
            if isinstance(v, Matrix4x4):
                return v

            v = flatten(v)

            if len(v) not in sizes:
                raise MatrixException(ERROR_4D_MESSAGE) from None

            return tuple(v)
        except ERROR_TUPLE:
            raise MatrixException(ERROR_4D_MESSAGE) from None

    @classmethod
    def construct_from_wrapped(
            cls, x: 'Matrix4x4', y: 'Matrix4x4',
            m11: NUM, m12: NUM, m13: NUM, m14: NUM,
            m21: NUM, m22: NUM, m23: NUM, m24: NUM,
            m31: NUM, m32: NUM, m33: NUM, m34: NUM,
            m41: NUM, m42: NUM, m43: NUM, m44: NUM) -> 'Matrix4x4':

        wrapped0 = x.wrapped if hasattr(x, 'wrapped') else None
        wrapped1 = y.wrapped if hasattr(y, 'wrapped') else None
        wrapped = wrapped0 if wrapped0 else wrapped1

        if wrapped:
            m = Matrix4x4.identity()
            m.wrapped = wrapped

            m.column0 = m11, m12, m13, m14
            m.column1 = m21, m22, m23, m24
            m.column2 = m31, m32, m33, m34
            m.column3 = m41, m42, m43, m44

            return m
        else:
            return Matrix4x4(
                m11, m12, m13, m14,
                m21, m22, m23, m24,
                m31, m32, m33, m34,
                m41, m42, m43, m44)

    def __add__(self, other: MATRIX_TYPE) -> 'Matrix4x4':
        other = Matrix4x4._force_dim(other)

        m11 = self.m11 + other.m11
        m12 = self.m12 + other.m12
        m13 = self.m13 + other.m13
        m14 = self.m14 + other.m14
        m21 = self.m21 + other.m21
        m22 = self.m22 + other.m22
        m23 = self.m23 + other.m23
        m24 = self.m24 + other.m24
        m31 = self.m31 + other.m31
        m32 = self.m32 + other.m32
        m33 = self.m33 + other.m33
        m34 = self.m34 + other.m34
        m41 = self.m41 + other.m41
        m42 = self.m42 + other.m42
        m43 = self.m43 + other.m43
        m44 = self.m44 + other.m44

        return Matrix4x4.construct_from_wrapped(
            self, other,
            m11, m12, m13, m14,
            m21, m22, m23, m24,
            m31, m32, m33, m34,
            m41, m42, m43, m44)

    def __radd__(self, other: MATRIX_TYPE) -> 'Matrix4x4':
        other = Matrix4x4._force_dim(other)

        m11 = other.m11 + self.m11
        m12 = other.m12 + self.m12
        m13 = other.m13 + self.m13
        m14 = other.m14 + self.m14
        m21 = other.m21 + self.m21
        m22 = other.m22 + self.m22
        m23 = other.m23 + self.m23
        m24 = other.m24 + self.m24
        m31 = other.m31 + self.m31
        m32 = other.m32 + self.m32
        m33 = other.m33 + self.m33
        m34 = other.m34 + self.m34
        m41 = other.m41 + self.m41
        m42 = other.m42 + self.m42
        m43 = other.m43 + self.m43
        m44 = other.m44 + self.m44

        return Matrix4x4.construct_from_wrapped(
            self, other,
            m11, m12, m13, m14,
            m21, m22, m23, m24,
            m31, m32, m33, m34,
            m41, m42, m43, m44)

    def __sub__(self, other: MATRIX_TYPE) -> 'Matrix4x4':
        other = Matrix4x4._force_dim(other)

        m11 = self.m11 - other.m11
        m12 = self.m12 - other.m12
        m13 = self.m13 - other.m13
        m14 = self.m14 - other.m14
        m21 = self.m21 - other.m21
        m22 = self.m22 - other.m22
        m23 = self.m23 - other.m23
        m24 = self.m24 - other.m24
        m31 = self.m31 - other.m31
        m32 = self.m32 - other.m32
        m33 = self.m33 - other.m33
        m34 = self.m34 - other.m34
        m41 = self.m41 - other.m41
        m42 = self.m42 - other.m42
        m43 = self.m43 - other.m43
        m44 = self.m44 - other.m44

        return Matrix4x4.construct_from_wrapped(
            self, other,
            m11, m12, m13, m14,
            m21, m22, m23, m24,
            m31, m32, m33, m34,
            m41, m42, m43, m44)

    def __rsub__(self, other: MATRIX_TYPE) -> 'Matrix4x4':
        other = Matrix4x4._force_dim(other)

        m11 = other.m11 - self.m11
        m12 = other.m12 - self.m12
        m13 = other.m13 - self.m13
        m14 = other.m14 - self.m14
        m21 = other.m21 - self.m21
        m22 = other.m22 - self.m22
        m23 = other.m23 - self.m23
        m24 = other.m24 - self.m24
        m31 = other.m31 - self.m31
        m32 = other.m32 - self.m32
        m33 = other.m33 - self.m33
        m34 = other.m34 - self.m34
        m41 = other.m41 - self.m41
        m42 = other.m42 - self.m42
        m43 = other.m43 - self.m43
        m44 = other.m44 - self.m44

        return Matrix4x4.construct_from_wrapped(
            self, other,
            m11, m12, m13, m14,
            m21, m22, m23, m24,
            m31, m32, m33, m34,
            m41, m42, m43, m44)

    def __mul__(self, other: MATRIX_TYPE) -> 'Matrix4x4':
        other = Matrix4x4._force_dim(other)

        m11 = self.m11 * other.m11
        m12 = self.m12 * other.m12
        m13 = self.m13 * other.m13
        m14 = self.m14 * other.m14
        m21 = self.m21 * other.m21
        m22 = self.m22 * other.m22
        m23 = self.m23 * other.m23
        m24 = self.m24 * other.m24
        m31 = self.m31 * other.m31
        m32 = self.m32 * other.m32
        m33 = self.m33 * other.m33
        m34 = self.m34 * other.m34
        m41 = self.m41 * other.m41
        m42 = self.m42 * other.m42
        m43 = self.m43 * other.m43
        m44 = self.m44 * other.m44

        return Matrix4x4.construct_from_wrapped(
            self, other,
            m11, m12, m13, m14,
            m21, m22, m23, m24,
            m31, m32, m33, m34,
            m41, m42, m43, m44)

    def __rmul__(self, other: MATRIX_TYPE) -> 'Matrix4x4':
        other = Matrix4x4._force_dim(other)

        m11 = other.m11 * self.m11
        m12 = other.m12 * self.m12
        m13 = other.m13 * self.m13
        m14 = other.m14 * self.m14
        m21 = other.m21 * self.m21
        m22 = other.m22 * self.m22
        m23 = other.m23 * self.m23
        m24 = other.m24 * self.m24
        m31 = other.m31 * self.m31
        m32 = other.m32 * self.m32
        m33 = other.m33 * self.m33
        m34 = other.m34 * self.m34
        m41 = other.m41 * self.m41
        m42 = other.m42 * self.m42
        m43 = other.m43 * self.m43
        m44 = other.m44 * self.m44

        return Matrix4x4.construct_from_wrapped(
            self, other,
            m11, m12, m13, m14,
            m21, m22, m23, m24,
            m31, m32, m33, m34,
            m41, m42, m43, m44)

    def __matmul__(self, other: MATRIX_TYPE) -> Union['Matrix4x4', Vector4D]:
        other = Matrix4x4._force_dim_vec(other)

        if len(other) == 16 or isinstance(other, Matrix4x4):
            other = Matrix4x4.from_iterable(other)

            m11 = (self.m11 * other.m11 + self.m21 * other.m12
                   + self.m31 * other.m13 + self.m41 * other.m14)
            m12 = (self.m12 * other.m11 + self.m22 * other.m12
                   + self.m32 * other.m13 + self.m42 * other.m14)
            m13 = (self.m13 * other.m11 + self.m23 * other.m12
                   + self.m33 * other.m13 + self.m43 * other.m14)
            m14 = (self.m14 * other.m11 + self.m24 * other.m12
                   + self.m34 * other.m13 + self.m44 * other.m14)
            m21 = (self.m11 * other.m21 + self.m21 * other.m22
                   + self.m31 * other.m23 + self.m41 * other.m24)
            m22 = (self.m12 * other.m21 + self.m22 * other.m22
                   + self.m32 * other.m23 + self.m42 * other.m24)
            m23 = (self.m13 * other.m21 + self.m23 * other.m22
                   + self.m33 * other.m23 + self.m43 * other.m24)
            m24 = (self.m14 * other.m21 + self.m24 * other.m22
                   + self.m34 * other.m23 + self.m44 * other.m24)
            m31 = (self.m11 * other.m31 + self.m21 * other.m32
                   + self.m31 * other.m33 + self.m41 * other.m34)
            m32 = (self.m12 * other.m31 + self.m22 * other.m32
                   + self.m32 * other.m33 + self.m42 * other.m34)
            m33 = (self.m13 * other.m31 + self.m23 * other.m32
                   + self.m33 * other.m33 + self.m43 * other.m34)
            m34 = (self.m14 * other.m31 + self.m24 * other.m32
                   + self.m34 * other.m33 + self.m44 * other.m34)
            m41 = (self.m11 * other.m41 + self.m21 * other.m42
                   + self.m31 * other.m43 + self.m41 * other.m44)
            m42 = (self.m12 * other.m41 + self.m22 * other.m42
                   + self.m32 * other.m43 + self.m42 * other.m44)
            m43 = (self.m13 * other.m41 + self.m23 * other.m42
                   + self.m33 * other.m43 + self.m43 * other.m44)
            m44 = (self.m14 * other.m41 + self.m24 * other.m42
                   + self.m34 * other.m43 + self.m44 * other.m44)

            return Matrix4x4.construct_from_wrapped(
                self, other,
                m11, m12, m13, m14,
                m21, m22, m23, m24,
                m31, m32, m33, m34,
                m41, m42, m43, m44)
        else:
            x = (self.m11 * other[0]
                 + self.m21 * other[1]
                 + self.m31 * other[2]
                 + self.m41 * other[3])
            y = (self.m12 * other[0]
                 + self.m22 * other[1]
                 + self.m32 * other[2]
                 + self.m42 * other[3])
            z = (self.m13 * other[0]
                 + self.m23 * other[1]
                 + self.m33 * other[2]
                 + self.m43 * other[3])
            w = (self.m14 * other[0]
                 + self.m24 * other[1]
                 + self.m34 * other[2]
                 + self.m44 * other[3])

            return Vector4D(x, y, z, w)

    def __rmatmul__(self, other: MATRIX_TYPE) -> Union['Matrix4x4', Vector4D]:
        m = Matrix4x4._force_dim_vec(other)

        if len(other) == 16 or isinstance(other, Matrix4x4):
            other = Matrix4x4.from_iterable(m)

            m11 = (other.m11 * self.m11 + other.m21 * self.m12
                   + other.m31 * self.m13 + other.m41 * self.m14)
            m12 = (other.m12 * self.m11 + other.m22 * self.m12
                   + other.m32 * self.m13 + other.m42 * self.m14)
            m13 = (other.m13 * self.m11 + other.m23 * self.m12
                   + other.m33 * self.m13 + other.m43 * self.m14)
            m14 = (other.m14 * self.m11 + other.m24 * self.m12
                   + other.m34 * self.m13 + other.m44 * self.m14)
            m21 = (other.m11 * self.m21 + other.m21 * self.m22
                   + other.m31 * self.m23 + other.m41 * self.m24)
            m22 = (other.m12 * self.m21 + other.m22 * self.m22
                   + other.m32 * self.m23 + other.m42 * self.m24)
            m23 = (other.m13 * self.m21 + other.m23 * self.m22
                   + other.m33 * self.m23 + other.m43 * self.m24)
            m24 = (other.m14 * self.m21 + other.m24 * self.m22
                   + other.m34 * self.m23 + other.m44 * self.m24)
            m31 = (other.m11 * self.m31 + other.m21 * self.m32
                   + other.m31 * self.m33 + other.m41 * self.m34)
            m32 = (other.m12 * self.m31 + other.m22 * self.m32
                   + other.m32 * self.m33 + other.m42 * self.m34)
            m33 = (other.m13 * self.m31 + other.m23 * self.m32
                   + other.m33 * self.m33 + other.m43 * self.m34)
            m34 = (other.m14 * self.m31 + other.m24 * self.m32
                   + other.m34 * self.m33 + other.m44 * self.m34)
            m41 = (other.m11 * self.m41 + other.m21 * self.m42
                   + other.m31 * self.m43 + other.m41 * self.m44)
            m42 = (other.m12 * self.m41 + other.m22 * self.m42
                   + other.m32 * self.m43 + other.m42 * self.m44)
            m43 = (other.m13 * self.m41 + other.m23 * self.m42
                   + other.m33 * self.m43 + other.m43 * self.m44)
            m44 = (other.m14 * self.m41 + other.m24 * self.m42
                   + other.m34 * self.m43 + other.m44 * self.m44)

            return Matrix4x4.construct_from_wrapped(
                self, other,
                m11, m12, m13, m14,
                m21, m22, m23, m24,
                m31, m32, m33, m34,
                m41, m42, m43, m44)
        else:
            raise MatrixException(ERROR_4D_MESSAGE)

    def __truediv__(self, other: MATRIX_TYPE) -> 'Matrix4x4':
        other = Matrix4x4._force_dim(other, 1.0)

        m11 = self.m11 / other.m11
        m12 = self.m12 / other.m12
        m13 = self.m13 / other.m13
        m14 = self.m14 / other.m14
        m21 = self.m21 / other.m21
        m22 = self.m22 / other.m22
        m23 = self.m23 / other.m23
        m24 = self.m24 / other.m24
        m31 = self.m31 / other.m31
        m32 = self.m32 / other.m32
        m33 = self.m33 / other.m33
        m34 = self.m34 / other.m34
        m41 = self.m41 / other.m41
        m42 = self.m42 / other.m42
        m43 = self.m43 / other.m43
        m44 = self.m44 / other.m44

        return Matrix4x4.construct_from_wrapped(
            self, other,
            m11, m12, m13, m14,
            m21, m22, m23, m24,
            m31, m32, m33, m34,
            m41, m42, m43, m44)

    def __rtruediv__(self, other: MATRIX_TYPE) -> 'Matrix4x4':
        other = Matrix4x4._force_dim(other, 1.0)

        m11 = other.m11 / self.m11
        m12 = other.m12 / self.m12
        m13 = other.m13 / self.m13
        m14 = other.m14 / self.m14
        m21 = other.m21 / self.m21
        m22 = other.m22 / self.m22
        m23 = other.m23 / self.m23
        m24 = other.m24 / self.m24
        m31 = other.m31 / self.m31
        m32 = other.m32 / self.m32
        m33 = other.m33 / self.m33
        m34 = other.m34 / self.m34
        m41 = other.m41 / self.m41
        m42 = other.m42 / self.m42
        m43 = other.m43 / self.m43
        m44 = other.m44 / self.m44

        return Matrix4x4.construct_from_wrapped(
            self, other,
            m11, m12, m13, m14,
            m21, m22, m23, m24,
            m31, m32, m33, m34,
            m41, m42, m43, m44)

    def __floordiv__(self, other: MATRIX_TYPE) -> 'Matrix4x4':
        other = Matrix4x4._force_dim(other, 1.0)

        m11 = self.m11 // other.m11
        m12 = self.m12 // other.m12
        m13 = self.m13 // other.m13
        m14 = self.m14 // other.m14
        m21 = self.m21 // other.m21
        m22 = self.m22 // other.m22
        m23 = self.m23 // other.m23
        m24 = self.m24 // other.m24
        m31 = self.m31 // other.m31
        m32 = self.m32 // other.m32
        m33 = self.m33 // other.m33
        m34 = self.m34 // other.m34
        m41 = self.m41 // other.m41
        m42 = self.m42 // other.m42
        m43 = self.m43 // other.m43
        m44 = self.m44 // other.m44

        return Matrix4x4.construct_from_wrapped(
            self, other,
            m11, m12, m13, m14,
            m21, m22, m23, m24,
            m31, m32, m33, m34,
            m41, m42, m43, m44)

    def __rfloordiv__(self, other: MATRIX_TYPE) -> 'Matrix4x4':
        other = Matrix4x4._force_dim(other, 1.0)

        m11 = other.m11 // self.m11
        m12 = other.m12 // self.m12
        m13 = other.m13 // self.m13
        m14 = other.m14 // self.m14
        m21 = other.m21 // self.m21
        m22 = other.m22 // self.m22
        m23 = other.m23 // self.m23
        m24 = other.m24 // self.m24
        m31 = other.m31 // self.m31
        m32 = other.m32 // self.m32
        m33 = other.m33 // self.m33
        m34 = other.m34 // self.m34
        m41 = other.m41 // self.m41
        m42 = other.m42 // self.m42
        m43 = other.m43 // self.m43
        m44 = other.m44 // self.m44

        return Matrix4x4.construct_from_wrapped(
            self, other,
            m11, m12, m13, m14,
            m21, m22, m23, m24,
            m31, m32, m33, m34,
            m41, m42, m43, m44)

    def __abs__(self) -> 'Matrix4x4':
        m11 = abs(self.m11)
        m12 = abs(self.m12)
        m13 = abs(self.m13)
        m14 = abs(self.m14)
        m21 = abs(self.m21)
        m22 = abs(self.m22)
        m23 = abs(self.m23)
        m24 = abs(self.m24)
        m31 = abs(self.m31)
        m32 = abs(self.m32)
        m33 = abs(self.m33)
        m34 = abs(self.m34)
        m41 = abs(self.m41)
        m42 = abs(self.m42)
        m43 = abs(self.m43)
        m44 = abs(self.m44)

        return Matrix4x4.construct_from_wrapped(
            self, self,
            m11, m12, m13, m14,
            m21, m22, m23, m24,
            m31, m32, m33, m34,
            m41, m42, m43, m44)

    def __mod__(self, other: MATRIX_TYPE) -> 'Matrix4x4':
        if hasattr(other, '__iter__') and len(other) == 4:
            return Matrix4x4.construct_from_wrapped(
                self, self,
                self.m11 % float(other[0]),
                self.m12,
                self.m13,
                self.m14,
                self.m21,
                self.m22 % float(other[1]),
                self.m23,
                self.m24,
                self.m31,
                self.m32,
                self.m33 % float(other[2]),
                self.m34,
                self.m41,
                self.m42,
                self.m43,
                self.m44 % float(other[3]))

        other = Matrix4x4._force_dim(other)

        m11 = self.m11 % other.m11
        m12 = self.m12 % other.m12
        m13 = self.m13 % other.m13
        m14 = self.m14 % other.m14
        m21 = self.m21 % other.m21
        m22 = self.m22 % other.m22
        m23 = self.m23 % other.m23
        m24 = self.m24 % other.m24
        m31 = self.m31 % other.m31
        m32 = self.m32 % other.m32
        m33 = self.m33 % other.m33
        m34 = self.m34 % other.m34
        m41 = self.m41 % other.m41
        m42 = self.m42 % other.m42
        m43 = self.m43 % other.m43
        m44 = self.m44 % other.m44

        return Matrix4x4.construct_from_wrapped(
            self, other,
            m11, m12, m13, m14,
            m21, m22, m23, m24,
            m31, m32, m33, m34,
            m41, m42, m43, m44)

    def __pow__(self, other: MATRIX_TYPE) -> 'Matrix4x4':
        other = Matrix4x4._force_dim(other)

        m11 = self.m11 ** other.m11
        m12 = self.m12 ** other.m12
        m13 = self.m13 ** other.m13
        m14 = self.m14 ** other.m14
        m21 = self.m21 ** other.m21
        m22 = self.m22 ** other.m22
        m23 = self.m23 ** other.m23
        m24 = self.m24 ** other.m24
        m31 = self.m31 ** other.m31
        m32 = self.m32 ** other.m32
        m33 = self.m33 ** other.m33
        m34 = self.m34 ** other.m34
        m41 = self.m41 ** other.m41
        m42 = self.m42 ** other.m42
        m43 = self.m43 ** other.m43
        m44 = self.m44 ** other.m44

        return Matrix4x4.construct_from_wrapped(
            self, other,
            m11, m12, m13, m14,
            m21, m22, m23, m24,
            m31, m32, m33, m34,
            m41, m42, m43, m44)

    def __pos__(self) -> 'Matrix4x4':
        return Matrix4x4.construct_from_wrapped(
            self, self,
            +self.m11, +self.m12, +self.m13, +self.m14,
            +self.m21, +self.m22, +self.m23, +self.m24,
            +self.m31, +self.m32, +self.m33, +self.m34,
            +self.m41, +self.m42, +self.m43, +self.m44)

    def __neg__(self) -> 'Matrix4x4':
        return Matrix4x4.construct_from_wrapped(
            self, self,
            -self.m11, -self.m12, -self.m13, -self.m14,
            -self.m21, -self.m22, -self.m23, -self.m24,
            -self.m31, -self.m32, -self.m33, -self.m34,
            -self.m41, -self.m42, -self.m43, -self.m44)

    def __getitem__(
            self, index: Union[int, slice]) -> Union[List[Vector4D], Vector4D]:

        def _get(index: int) -> Vector4D:
            if index == 0 or index == -4:
                return Vector4D(self.m11, self.m12, self.m13, self.m14)
            elif index == 1 or index == -3:
                return Vector4D(self.m21, self.m22, self.m23, self.m24)
            elif index == 2 or index == -2:
                return Vector4D(self.m31, self.m32, self.m33, self.m34)
            elif index == 3 or index == -1:
                return Vector4D(self.m41, self.m42, self.m43, self.m44)
            else:
                raise IndexError(ERROR_4D_INDEX_MESSAGE) from None

        if isinstance(index, slice):
            return [_get(i) for i in range(*index.indices(len(self)))]
        else:
            return _get(index)

    def __setitem__(
            self,
            index: Union[int, slice],
            value: MATRIX_TYPE):

        def _set(index: int, value: MATRIX_TYPE):
            value = self._force_dim_vec(value, (4,))

            if index == 0 or index == -4:
                self.m11 = value[0]
                self.m12 = value[1]
                self.m13 = value[2]
                self.m14 = value[3]
            elif index == 1 or index == -3:
                self.m21 = value[0]
                self.m22 = value[1]
                self.m23 = value[2]
                self.m24 = value[3]
            elif index == 2 or index == -2:
                self.m31 = value[0]
                self.m32 = value[1]
                self.m33 = value[2]
                self.m34 = value[3]
            elif index == 3 or index == -1:
                self.m41 = value[0]
                self.m42 = value[1]
                self.m43 = value[2]
                self.m44 = value[3]
            else:
                raise IndexError(ERROR_4D_INDEX_MESSAGE) from None

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

        safe_matrix4x4_op(_set2, index, value)

    def __iter__(self) -> Iterator[Vector4D]:
        yield Vector4D(self.m11, self.m12, self.m13, self.m14)
        yield Vector4D(self.m21, self.m22, self.m23, self.m24)
        yield Vector4D(self.m31, self.m32, self.m33, self.m34)
        yield Vector4D(self.m41, self.m42, self.m43, self.m44)

    def __len__(self) -> int:
        return 4

    def __format__(self, format_spec: str) -> str:
        m11 = format(self.m11, format_spec)
        m12 = format(self.m12, format_spec)
        m13 = format(self.m13, format_spec)
        m14 = format(self.m14, format_spec)
        m21 = format(self.m21, format_spec)
        m22 = format(self.m22, format_spec)
        m23 = format(self.m23, format_spec)
        m24 = format(self.m24, format_spec)
        m31 = format(self.m31, format_spec)
        m32 = format(self.m32, format_spec)
        m33 = format(self.m33, format_spec)
        m34 = format(self.m34, format_spec)
        m41 = format(self.m41, format_spec)
        m42 = format(self.m42, format_spec)
        m43 = format(self.m43, format_spec)
        m44 = format(self.m44, format_spec)

        return ('({}, {}, {}, {},\n'
                ' {}, {}, {}, {},\n'
                ' {}, {}, {}, {},\n'
                ' {}, {}, {}, {})').format(
                    m11, m21, m31, m41,
                    m12, m22, m32, m42,
                    m13, m23, m33, m43,
                    m14, m24, m34, m44)

    def __repr__(self) -> str:
        return ('Matrix4x4'
                '({}, {}, {}, {},'
                ' {}, {}, {}, {},'
                ' {}, {}, {}, {},'
                ' {}, {}, {}, {})').format(
                    self.m11, self.m12, self.m13, self.m14,
                    self.m21, self.m22, self.m23, self.m24,
                    self.m31, self.m32, self.m33, self.m34,
                    self.m41, self.m42, self.m43, self.m44)

    def __eq__(
            self,
            value: MATRIX_TYPE) -> Tuple[bool]:
        try:
            values = self._force_dim(value)
            return tuple(
                map(lambda t: t[0] == t[1], zip(self._values, values._values)))
        except ValueError:
            raise MatrixException(ERROR_4D_MESSAGE) from None

    def __lt__(
            self,
            value: MATRIX_TYPE) -> Tuple[bool]:
        try:
            values = self._force_dim(value)
            return tuple(
                map(lambda t: t[0] < t[1], zip(self._values, values._values)))
        except ValueError:
            raise MatrixException(ERROR_4D_MESSAGE) from None

    def __le__(
            self,
            value: MATRIX_TYPE) -> Tuple[bool]:
        try:
            values = self._force_dim(value)
            return tuple(
                map(lambda t: t[0] <= t[1], zip(self._values, values._values)))
        except ValueError:
            raise MatrixException(ERROR_4D_MESSAGE) from None

    def __gt__(
            self,
            value: MATRIX_TYPE) -> Tuple[bool]:
        try:
            values = self._force_dim(value)
            return tuple(
                map(lambda t: t[0] > t[1], zip(self._values, values._values)))
        except ValueError:
            raise MatrixException(ERROR_4D_MESSAGE) from None

    def __ge__(
            self,
            value: MATRIX_TYPE) -> Tuple[bool]:
        try:
            values = self._force_dim(value)
            return tuple(
                map(lambda t: t[0] >= t[1], zip(self._values, values._values)))
        except ValueError:
            raise MatrixException(ERROR_4D_MESSAGE) from None

    @classmethod
    def transform_point(
            cls, matrix: MATRIX_TYPE, point: Iterable[NUM]) -> Vector3D:
        '''Transform a point using a transformation matrix

        Args:
            matrix (MATRIX_TYPE): transformation matrix
            point (Iterable[NUM]): point to transform

        Returns:
            Vector3D
        '''

        lp = len(point)
        if not hasattr(point, '__iter__') or lp not in (3, 4):
            raise MatrixException(
                ('Failed to transform value. '
                 'Expected a Vector3D or Vector4D.')) from None

        matrix = Matrix4x4._force_dim(matrix, use_fill_for_scalar=True)
        point = Matrix4x4._force_dim_vec(point, (3, 4))

        return ((matrix @ Vector4D(*point, 1.0)).xyz if lp == 3
                else (matrix @ Vector4D(*point[:3], 1.0)).xyz)

    @classmethod
    def transform_direction(
            cls, matrix: MATRIX_TYPE, direction: Iterable[NUM]) -> Vector3D:
        '''Transform a direction vector using a transformation matrix

        Args:
            matrix (MATRIX_TYPE): transformation matrix
            direction (Iterable[NUM]): direction vector to transform

        Returns:
            Vector3D
        '''

        ld = len(direction)
        if not hasattr(direction, '__iter__') or ld not in (3, 4):
            raise MatrixException(
                ('Failed to transform value. '
                 'Expected a Vector3D or Vector4D.')) from None

        matrix = Matrix4x4._force_dim(matrix, use_fill_for_scalar=True)
        direction = Matrix4x4._force_dim_vec(direction, (3, 4))

        return ((matrix @ Vector4D(*direction, 0.0)).xyz if ld == 3
                else (matrix @ Vector4D(*direction[:3], 0.0)).xyz)

    @classmethod
    def clear_translation(cls, value: MATRIX_TYPE) -> 'Matrix4x4':
        ''' Clears the translation from a transformation matrix

        Args:
            value (MATRIX_TYPE): 4x4 input matrix

        Returns:
            Matrix4x4
        '''

        value = Matrix4x4._force_dim(value, use_fill_for_scalar=True)
        value.m41 = 0
        value.m42 = 0
        value.m43 = 0
        return value

    @classmethod
    def clear_rotation(cls, value: MATRIX_TYPE) -> 'Matrix4x4':
        ''' Clears the rotation from a transformation matrix

        Args:
            value (MATRIX_TYPE): 4x4 input matrix

        Returns:
            Matrix4x4
        '''

        value = Matrix4x4._force_dim(value, use_fill_for_scalar=True)

        col0 = value.column0
        col1 = value.column1
        col2 = value.column2

        col0 = Vector3D.length(col0.xyz), 0, 0, col0.w
        col1 = 0, Vector3D.length(col1.xyz), 0, col1.w
        col2 = 0, 0, Vector3D.length(col2.xyz), col2.w

        value.column0 = col0
        value.column1 = col1
        value.column2 = col2

        return value

    @classmethod
    def clear_scale(cls, value: MATRIX_TYPE) -> 'Matrix4x4':
        ''' Clears the scale from a transformation matrix

        Args:
            value (MATRIX_TYPE): 4x4 input matrix

        Returns:
            Matrix4x4
        '''

        value = Matrix4x4._force_dim(value, use_fill_for_scalar=True)

        col0 = value.column0
        col1 = value.column1
        col2 = value.column2

        col0 = Vector4D(*Vector3D.normalize(col0.xyz), col0.w)
        col1 = Vector4D(*Vector3D.normalize(col1.xyz), col1.w)
        col2 = Vector4D(*Vector3D.normalize(col2.xyz), col2.w)

        value.column0 = col0
        value.column1 = col1
        value.column2 = col2

        return value

    @classmethod
    def translation(
            cls, x: NUM = 0.0, y: NUM = 0.0, z: NUM = 0.0) -> 'Matrix4x4':
        ''' Creates a translation matrix

        Args:
            x (NUM, default=0.0): x-translation
            y (NUM, default=0.0): y-translation
            z (NUM, default=0.0): z-translation

        Returns:
            Matrix4x4
        '''

        result = Matrix4x4.identity()
        result.column3 = Vector4D(x, y, z, 1)
        return result

    @classmethod
    def rotation_x(cls, angle: NUM) -> 'Matrix4x4':
        ''' Creates a rotation matrix for rotating about the x-axis

        Args:
            angle (NUM): angle in radians to rotate by

        Returns:
            Matrix4x4
        '''

        cos = math.cos(angle)
        sin = math.sin(angle)

        result = Matrix4x4.identity()
        result.m22 = cos
        result.m23 = sin
        result.m32 = -sin
        result.m33 = cos

        return result

    @classmethod
    def rotation_y(cls, angle: NUM) -> 'Matrix4x4':
        ''' Creates a rotation matrix for rotating about the y-axis

        Args:
            angle (NUM): angle in radians to rotate by

        Returns:
            Matrix4x4
        '''

        cos = math.cos(angle)
        sin = math.sin(angle)

        result = Matrix4x4.identity()
        result.m11 = cos
        result.m13 = -sin
        result.m31 = sin
        result.m33 = cos

        return result

    @classmethod
    def rotation_z(cls, angle: NUM) -> 'Matrix4x4':
        ''' Creates a rotation matrix for rotating about the z-axis

        Args:
            angle (NUM): angle in radians to rotate by

        Returns:
            Matrix4x4
        '''

        cos = math.cos(angle)
        sin = math.sin(angle)

        result = Matrix4x4.identity()
        result.m11 = cos
        result.m12 = sin
        result.m21 = -sin
        result.m22 = cos

        return result

    @classmethod
    def rotation(
            cls, axis: Iterable[NUM], angle: NUM) -> 'Matrix4x4':
        ''' Creates a rotation matrix for rotating about a 3D axis

        Args:
            axis (Iterable[NUM]): 3D axis to rotate about
            angle (NUM): angle in radians to rotate by

        Returns:
            Matrix4x4
        '''

        axis = Matrix4x4._force_dim_vec(axis, (3,))
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

        result = Matrix4x4.identity()
        result.column0 = txx + cos, txy - sinz, txz + siny, 0
        result.column1 = txy + sinz, tyy + cos, tyz - sinx, 0
        result.column2 = txz - siny, tyz + sinx, tzz + cos, 0

        return result

    @classmethod
    def scale(cls, x: NUM = 1.0, y: NUM = 1.0, z: NUM = 1.0) -> 'Matrix4x4':
        ''' Creates a scale matrix

        Args:
            x (NUM, default=1.0): x-scale
            y (NUM, default=1.0): y-scale
            z (NUM, default=1.0): z-scale

        Returns:
            Matrix4x4
        '''

        result = Matrix4x4.identity()
        result.m11 = x
        result.m22 = y
        result.m33 = z
        return result

    @classmethod
    def _determinant(cls, value: 'Matrix4x4') -> float:
        a = value.m11
        b = value.m21
        c = value.m31
        d = value.m41

        x = Matrix3x3.determinant((
            value.m22, value.m23, value.m24,
            value.m32, value.m33, value.m34,
            value.m42, value.m43, value.m44))
        y = Matrix3x3.determinant((
            value.m12, value.m13, value.m14,
            value.m32, value.m33, value.m34,
            value.m42, value.m43, value.m44))
        z = Matrix3x3.determinant((
            value.m12, value.m13, value.m14,
            value.m22, value.m23, value.m24,
            value.m42, value.m43, value.m44))
        w = Matrix3x3.determinant((
            value.m12, value.m13, value.m14,
            value.m22, value.m23, value.m24,
            value.m32, value.m33, value.m34))

        return a * x - b * y + c * z - d * w

    @classmethod
    def determinant(cls, value: MATRIX_TYPE) -> float:
        '''Determinant of a 4x4 matrix.

        Args:
            value (MATRIX_TYPE): 4x4 input matrix

        Returns:
            float
        '''

        value = cls._force_dim(value, use_fill_for_scalar=True)
        return cls._determinant(value)

    @classmethod
    def _transpose(cls, value: 'Matrix4x4') -> 'Matrix4x4':
        return Matrix4x4.construct_from_wrapped(
            value, value,
            value.m11, value.m21, value.m31, value.m41,
            value.m12, value.m22, value.m32, value.m42,
            value.m13, value.m23, value.m33, value.m43,
            value.m14, value.m24, value.m34, value.m44)

    @classmethod
    def transpose(cls, value: MATRIX_TYPE) -> 'Matrix4x4':
        '''Transpose of a 4x4 matrix.

        Args:
            value (MATRIX_TYPE): 4x4 input matrix

        Returns:
            float
        '''

        value = cls._force_dim(value, use_fill_for_scalar=True)
        return cls._transpose(value)

    @classmethod
    def inverse(cls, value: MATRIX_TYPE) -> 'Matrix4x4':
        '''Inverse of a 4x4 matrix.

        Args:
            value (MATRIX_TYPE): 4x4 input matrix

        Returns:
            float
        '''

        value = cls._force_dim(value, use_fill_for_scalar=True)
        det = cls._determinant(value)

        if det == 0.0:
            raise MatrixException('Matrix has no inverse.')

        d11 = Matrix3x3._determinant((
            value.m22, value.m23, value.m24,
            value.m32, value.m33, value.m34,
            value.m42, value.m43, value.m44))
        d21 = Matrix3x3._determinant((
            value.m12, value.m13, value.m14,
            value.m32, value.m33, value.m34,
            value.m42, value.m43, value.m44))
        d31 = Matrix3x3._determinant((
            value.m12, value.m13, value.m14,
            value.m22, value.m23, value.m24,
            value.m42, value.m43, value.m44))
        d41 = Matrix3x3._determinant((
            value.m12, value.m13, value.m14,
            value.m22, value.m23, value.m24,
            value.m32, value.m33, value.m34))
        d12 = Matrix3x3._determinant((
            value.m21, value.m23, value.m24,
            value.m31, value.m33, value.m34,
            value.m41, value.m43, value.m44))
        d22 = Matrix3x3._determinant((
            value.m11, value.m13, value.m14,
            value.m31, value.m33, value.m34,
            value.m41, value.m43, value.m44))
        d32 = Matrix3x3._determinant((
            value.m11, value.m13, value.m14,
            value.m21, value.m23, value.m24,
            value.m41, value.m43, value.m44))
        d42 = Matrix3x3._determinant((
            value.m11, value.m13, value.m14,
            value.m21, value.m23, value.m24,
            value.m31, value.m33, value.m34))
        d13 = Matrix3x3._determinant((
            value.m21, value.m22, value.m24,
            value.m31, value.m32, value.m34,
            value.m41, value.m42, value.m44))
        d23 = Matrix3x3._determinant((
            value.m11, value.m12, value.m14,
            value.m31, value.m32, value.m34,
            value.m41, value.m42, value.m44))
        d33 = Matrix3x3._determinant((
            value.m11, value.m12, value.m14,
            value.m21, value.m22, value.m24,
            value.m41, value.m42, value.m44))
        d43 = Matrix3x3._determinant((
            value.m11, value.m12, value.m14,
            value.m21, value.m22, value.m24,
            value.m31, value.m32, value.m34))
        d14 = Matrix3x3._determinant((
            value.m21, value.m22, value.m23,
            value.m31, value.m32, value.m33,
            value.m41, value.m42, value.m43))
        d24 = Matrix3x3._determinant((
            value.m11, value.m12, value.m13,
            value.m31, value.m32, value.m33,
            value.m41, value.m42, value.m43))
        d34 = Matrix3x3._determinant((
            value.m11, value.m12, value.m13,
            value.m21, value.m22, value.m23,
            value.m41, value.m42, value.m43))
        d44 = Matrix3x3._determinant((
            value.m11, value.m12, value.m13,
            value.m21, value.m22, value.m23,
            value.m31, value.m32, value.m33))

        adjugate = Matrix4x4.construct_from_wrapped(
            value, value,
            d11, -d21, d31, -d41,
            -d12, d22, -d32, d42,
            d13, -d23, d33, -d43,
            -d14, d24, -d34, d44)

        return adjugate / det

    @classmethod
    def normalize(cls, value: MATRIX_TYPE) -> 'Matrix4x4':
        ''' Matrix normalization.

        Args:
            value (MATRIX_TYPE): Matrix to evaluate.

        Returns:
            Matrix4x4
        '''

        value = cls._force_dim(value, use_fill_for_scalar=True)
        det = cls._determinant(value)

        value = Matrix4x4(*value)
        value.column0 /= det
        value.column1 /= det
        value.column2 /= det
        value.column3 /= det

        return value
