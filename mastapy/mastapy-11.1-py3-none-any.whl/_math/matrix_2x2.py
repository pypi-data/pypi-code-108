'''matrix_2x2.py'''


import math
from typing import Union, Iterable, Iterator, Tuple, List

from mastapy._math.matrix_base import (
    MatrixBase, flatten, MATRIX_TYPE, MatrixException,
    ERROR_TUPLE, _safe_matrix_op)
from mastapy._math.vector_2d import Vector2D
from mastapy._math.scalar import NUM


__all__ = ('Matrix2x2',)


ERROR_2D_MESSAGE = 'Vector must match matrix2x2 dimension.'
ERROR_2D_INDEX_MESSAGE = 'Invalid column index. There are only 2 columns.'
safe_matrix2x2_op = _safe_matrix_op(ERROR_2D_MESSAGE)


class Matrix2x2(MatrixBase):
    ''' Create a column-major Matrix2x2 from M11, M12, M21, M22 components.

    Args:
        m11: NUM
        m12: NUM
        m21: NUM
        m22: NUM

    Returns:
        Matrix2x2
    '''

    def __init__(self, m11: NUM, m12: NUM, m21: NUM, m22: NUM) -> 'Matrix2x2':
        super().__init__([float(m11), float(m12), float(m21), float(m22)])

    @classmethod
    def broadcast(cls, value: NUM) -> 'Matrix2x2':
        ''' Create a Matrix2x2 by broadcasting a value to all of its components

        Args:
            value: NUM

        Returns:
            Matrix2x2
        '''

        return cls(value, value, value, value)

    @classmethod
    def diagonal(cls, value: Union[NUM, Iterable[NUM]]) -> 'Matrix2x2':
        ''' Create a Matrix2x2 by broadcasting a value along the diagonal

        Args:
            value: Union[NUM, Iterable[NUM]]

        Returns:
            Matrix2x2
        '''

        if hasattr(value, '__iter__'):
            value = tuple(value)
            if len(value) != 2:
                raise MatrixException(ERROR_2D_MESSAGE)
            return cls(value[0], 0.0, 0.0, value[1])
        return cls(value, 0.0, 0.0, value)

    @classmethod
    def from_iterable(
            cls,
            t: Union[Iterable[Iterable[NUM]], Iterable[NUM]]) -> 'Matrix2x2':
        ''' Create a Matrix2x2 from an iterable

        Args:
            t: Union[Iterable[Iterable[NUM]], Iterable[NUM]]

        Returns:
            Matrix2x2
        '''

        return Matrix2x2(*flatten(t))

    @classmethod
    def identity(self) -> 'Matrix2x2':
        ''' Returns a 2x2 identity matrix

        Returns:
            Matrix2x2
        '''

        return Matrix2x2.diagonal(1)

    @classmethod
    def zero(self) -> 'Matrix2x2':
        ''' Returns a 2x2 matrix filled with 0s

        Returns:
            Matrix2x2
        '''

        return Matrix2x2.broadcast(0)

    @classmethod
    def one(self) -> 'Matrix2x2':
        ''' Returns a 2x2 matrix filled with 1s

        Returns:
            Matrix2x2
        '''

        return Matrix2x2.broadcast(1)

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
    def m21(self) -> float:
        ''' Get the M21 component of the matrix

        Returns:
            float
        '''

        return self._values[2]

    @m21.setter
    def m21(self, value: NUM):
        self._values[2] = float(value)

    @property
    def m22(self) -> float:
        ''' Get the M22 component of the matrix

        Returns:
            float
        '''

        return self._values[3]

    @m22.setter
    def m22(self, value: NUM):
        self._values[3] = float(value)

    @property
    def column0(self) -> Vector2D:
        ''' Get the first column

        Returns:
            float
        '''

        return Vector2D(self.m11, self.m12)

    @column0.setter
    def column0(self, value: MATRIX_TYPE):
        value = self._force_dim_vec(value, (2,))
        self._values[0] = value[0]
        self._values[1] = value[1]

    @property
    def column1(self) -> Vector2D:
        ''' Get the second column

        Returns:
            float
        '''

        return Vector2D(self.m21, self.m22)

    @column1.setter
    def column1(self, value: MATRIX_TYPE):
        value = self._force_dim_vec(value, (2,))
        self._values[2] = value[0]
        self._values[3] = value[1]

    @property
    def row0(self) -> Vector2D:
        ''' Get the first row

        Returns:
            float
        '''

        return Vector2D(self.m11, self.m21)

    @row0.setter
    def row0(self, value: MATRIX_TYPE):
        value = self._force_dim_vec(value, (2,))
        self._values[0] = value[0]
        self._values[2] = value[1]

    @property
    def row1(self) -> Vector2D:
        ''' Get the second row

        Returns:
            float
        '''

        return Vector2D(self.m12, self.m22)

    @row1.setter
    def row1(self, value: MATRIX_TYPE):
        value = self._force_dim_vec(value, (2,))
        self._values[1] = value[0]
        self._values[3] = value[1]

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
            if le == 2:
                v = (v[0], fill, fill, v[1])
            elif le != 4:
                raise MatrixException(ERROR_2D_MESSAGE) from None
        elif not b:
            v = (v, fill, fill, v) if use_fill_for_scalar else (v, v, v, v)

        return tuple(v)

    @classmethod
    def _force_dim_vec(
            cls, v: MATRIX_TYPE, sizes: Tuple[int] = (2, 4)) -> Tuple[NUM]:
        try:
            v = flatten(v)

            if len(v) not in sizes:
                raise MatrixException(ERROR_2D_MESSAGE) from None

            return tuple(v)
        except ERROR_TUPLE:
            raise MatrixException(ERROR_2D_MESSAGE) from None

    def __add__(self, other: MATRIX_TYPE) -> 'Matrix2x2':
        other = Matrix2x2._force_dim(other)

        m11 = self.m11 + other[0]
        m12 = self.m12 + other[1]
        m21 = self.m21 + other[2]
        m22 = self.m22 + other[3]

        return Matrix2x2(m11, m12, m21, m22)

    def __radd__(self, other: MATRIX_TYPE) -> 'Matrix2x2':
        other = Matrix2x2._force_dim(other)

        m11 = other[0] + self.m11
        m12 = other[1] + self.m12
        m21 = other[2] + self.m21
        m22 = other[3] + self.m22

        return Matrix2x2(m11, m12, m21, m22)

    def __sub__(self, other: MATRIX_TYPE) -> 'Matrix2x2':
        other = Matrix2x2._force_dim(other)

        m11 = self.m11 - other[0]
        m12 = self.m12 - other[1]
        m21 = self.m21 - other[2]
        m22 = self.m22 - other[3]

        return Matrix2x2(m11, m12, m21, m22)

    def __rsub__(self, other: MATRIX_TYPE) -> 'Matrix2x2':
        other = Matrix2x2._force_dim(other)

        m11 = other[0] - self.m11
        m12 = other[1] - self.m12
        m21 = other[2] - self.m21
        m22 = other[3] - self.m22

        return Matrix2x2(m11, m12, m21, m22)

    def __mul__(self, other: MATRIX_TYPE) -> 'Matrix2x2':
        other = Matrix2x2._force_dim(other, 1.0)

        m11 = self.m11 * other[0]
        m12 = self.m12 * other[1]
        m21 = self.m21 * other[2]
        m22 = self.m22 * other[3]

        return Matrix2x2(m11, m12, m21, m22)

    def __rmul__(self, other: MATRIX_TYPE) -> 'Matrix2x2':
        other = Matrix2x2._force_dim(other, 1.0)

        m11 = other[0] * self.m11
        m12 = other[1] * self.m12
        m21 = other[2] * self.m21
        m22 = other[3] * self.m22

        return Matrix2x2(m11, m12, m21, m22)

    def __matmul__(self, other: MATRIX_TYPE) -> Union['Matrix2x2', Vector2D]:
        other = Matrix2x2._force_dim_vec(other)

        if len(other) == 4:
            m11 = self.m11 * other[0] + self.m21 * other[1]
            m12 = self.m12 * other[0] + self.m22 * other[1]
            m21 = self.m11 * other[2] + self.m21 * other[3]
            m22 = self.m12 * other[2] + self.m22 * other[3]

            return Matrix2x2(m11, m12, m21, m22)
        else:
            x = self.m11 * other[0] + self.m21 * other[1]
            y = self.m12 * other[0] + self.m22 * other[1]

            return Vector2D(x, y)

    def __rmatmul__(self, other: MATRIX_TYPE) -> 'Matrix2x2':
        other = Matrix2x2._force_dim_vec(other)

        if len(other) == 4:
            m11 = other[0] * self.m11 + other[2] * self.m12
            m12 = other[1] * self.m11 + other[3] * self.m12
            m21 = other[0] * self.m21 + other[2] * self.m22
            m22 = other[1] * self.m21 + other[3] * self.m22

            return Matrix2x2(m11, m12, m21, m22)
        else:
            raise MatrixException(ERROR_2D_MESSAGE)

    def __truediv__(self, other: MATRIX_TYPE) -> 'Matrix2x2':
        other = Matrix2x2._force_dim(other, 1.0)

        m11 = self.m11 / other[0]
        m12 = self.m12 / other[1]
        m21 = self.m21 / other[2]
        m22 = self.m22 / other[3]

        return Matrix2x2(m11, m12, m21, m22)

    def __rtruediv__(self, other: MATRIX_TYPE) -> 'Matrix2x2':
        other = Matrix2x2._force_dim(other, 1.)

        m11 = other[0] / self.m11
        m12 = other[1] / self.m12
        m21 = other[2] / self.m21
        m22 = other[3] / self.m22

        return Matrix2x2(m11, m12, m21, m22)

    def __floordiv__(self, other: MATRIX_TYPE) -> 'Matrix2x2':
        other = Matrix2x2._force_dim(other, 1.0)

        m11 = self.m11 // other[0]
        m12 = self.m12 // other[1]
        m21 = self.m21 // other[2]
        m22 = self.m22 // other[3]

        return Matrix2x2(m11, m12, m21, m22)

    def __rfloordiv__(self, other: MATRIX_TYPE) -> 'Matrix2x2':
        other = Matrix2x2._force_dim(other, 1.0)

        m11 = other[0] // self.m11
        m12 = other[1] // self.m12
        m21 = other[2] // self.m21
        m22 = other[3] // self.m22

        return Matrix2x2(m11, m12, m21, m22)

    def __abs__(self) -> 'Matrix2x2':
        m11 = abs(self.m11)
        m12 = abs(self.m12)
        m21 = abs(self.m21)
        m22 = abs(self.m22)

        return Matrix2x2(m11, m12, m21, m22)

    def __mod__(self, other: MATRIX_TYPE) -> 'Matrix2x2':
        if hasattr(other, '__iter__') and len(other) == 2:
            return Matrix2x2(
                self.m11 % float(other[0]),
                self.m12,
                self.m21,
                self.m22 % float(other[1]))

        other = Matrix2x2._force_dim(other)

        m11 = self.m11 % other[0]
        m12 = self.m12 % other[1]
        m21 = self.m21 % other[2]
        m22 = self.m22 % other[3]

        return Matrix2x2(m11, m12, m21, m22)

    def __pow__(self, other: MATRIX_TYPE) -> 'Matrix2x2':
        other = Matrix2x2._force_dim(other)

        m11 = self.m11 ** other[0]
        m12 = self.m12 ** other[1]
        m21 = self.m21 ** other[2]
        m22 = self.m22 ** other[3]

        return Matrix2x2(m11, m12, m21, m22)

    def __pos__(self) -> 'Matrix2x2':
        return Matrix2x2(+self.m11, +self.m12, +self.m21, +self.m22)

    def __neg__(self) -> 'Matrix2x2':
        return Matrix2x2(-self.m11, -self.m12, -self.m21, -self.m22)

    def __getitem__(
            self, index: Union[int, slice]) -> Union[List[Vector2D], Vector2D]:

        def _get(index: int) -> Vector2D:
            if index == -1 or index == 1:
                return Vector2D(self.m21, self.m22)
            elif index == 0 or index == -2:
                return Vector2D(self.m11, self.m12)
            else:
                raise IndexError(ERROR_2D_INDEX_MESSAGE) from None

        if isinstance(index, slice):
            return [_get(i) for i in range(*index.indices(len(self)))]
        else:
            return _get(index)

    def __setitem__(
            self,
            index: Union[int, slice],
            value: MATRIX_TYPE):

        def _set(index: int, value: MATRIX_TYPE):
            value = self._force_dim_vec(value, (2,))

            if index == -1 or index == 1:
                self.m21 = value[0]
                self.m22 = value[1]
            elif index == 0 or index == -2:
                self.m11 = value[0]
                self.m12 = value[1]
            else:
                raise IndexError(ERROR_2D_INDEX_MESSAGE) from None

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

        safe_matrix2x2_op(_set2, index, value)

    def __iter__(self) -> Iterator[Vector2D]:
        yield Vector2D(self.m11, self.m12)
        yield Vector2D(self.m21, self.m22)

    def __len__(self) -> int:
        return 2

    def __format__(self, format_spec: str) -> str:
        m11 = format(self.m11, format_spec)
        m12 = format(self.m12, format_spec)
        m21 = format(self.m21, format_spec)
        m22 = format(self.m22, format_spec)

        return '({}, {},\n {}, {})'.format(m11, m21, m12, m22)

    def __repr__(self) -> str:
        return 'Matrix2x2({}, {}, {}, {})'.format(
            self.m11, self.m12, self.m21, self.m22)

    def __eq__(
            self,
            value: MATRIX_TYPE) -> Tuple[bool]:
        try:
            values = self._force_dim(value)
            return tuple(
                map(lambda t: t[0] == t[1], zip(self._values, values)))
        except ValueError:
            raise MatrixException(ERROR_2D_MESSAGE) from None

    def __lt__(
            self,
            value: MATRIX_TYPE) -> Tuple[bool]:
        try:
            values = self._force_dim(value)
            return tuple(
                map(lambda t: t[0] < t[1], zip(self._values, values)))
        except ValueError:
            raise MatrixException(ERROR_2D_MESSAGE) from None

    def __le__(
            self,
            value: MATRIX_TYPE) -> Tuple[bool]:
        try:
            values = self._force_dim(value)
            return tuple(
                map(lambda t: t[0] <= t[1], zip(self._values, values)))
        except ValueError:
            raise MatrixException(ERROR_2D_MESSAGE) from None

    def __gt__(
            self,
            value: MATRIX_TYPE) -> Tuple[bool]:
        try:
            values = self._force_dim(value)
            return tuple(
                map(lambda t: t[0] > t[1], zip(self._values, values)))
        except ValueError:
            raise MatrixException(ERROR_2D_MESSAGE) from None

    def __ge__(
            self,
            value: MATRIX_TYPE) -> Tuple[bool]:
        try:
            values = self._force_dim(value)
            return tuple(
                map(lambda t: t[0] >= t[1], zip(self._values, values)))
        except ValueError:
            raise MatrixException(ERROR_2D_MESSAGE) from None

    @classmethod
    def clear_rotation(cls, value: MATRIX_TYPE) -> 'Matrix2x2':
        ''' Clears the rotation from a transformation matrix

        Args:
            value (MATRIX_TYPE): 2x2 input matrix

        Returns:
            Matrix2x2
        '''

        value = Matrix2x2._force_dim(value, use_fill_for_scalar=True)
        value = Matrix2x2(*value)

        col0 = value.column0
        col1 = value.column1

        value.column0 = Vector2D.length(col0), 0
        value.column1 = 0, Vector2D.length(col1)

        return value

    @classmethod
    def clear_scale(cls, value: MATRIX_TYPE) -> 'Matrix2x2':
        ''' Clears the scale from a transformation matrix

        Args:
            value (MATRIX_TYPE): 2x2 input matrix

        Returns:
            Matrix2x2
        '''

        value = Matrix2x2._force_dim(value, use_fill_for_scalar=True)
        value = Matrix2x2(*value)

        value.column0 = Vector2D.normalize(value.column0)
        value.column1 = Vector2D.normalize(value.column1)

        return value

    @classmethod
    def rotation(cls, angle: NUM) -> 'Matrix2x2':
        ''' Creates a rotation matrix for rotating about a 3D axis

        Args:
            angle (NUM): angle in radians to rotate by

        Returns:
            Matrix2x2
        '''

        cos = math.cos(angle)
        sin = math.sin(angle)

        result = Matrix2x2.identity()
        result.m11 = cos
        result.m12 = sin
        result.m21 = -sin
        result.m22 = cos

        return result

    @classmethod
    def scale(cls, x: NUM = 1.0, y: NUM = 1.0) -> 'Matrix2x2':
        ''' Creates a scale matrix

        Args:
            x (NUM, default=1.0): x-scale
            y (NUM, default=1.0): y-scale

        Returns:
            Matrix2x2
        '''

        result = Matrix2x2.identity()
        result.m11 = x
        result.m22 = y
        return result

    @classmethod
    def _determinant(cls, value: 'Matrix2x2') -> float:
        return value[0] * value[3] - value[1] * value[2]

    @classmethod
    def determinant(cls, value: MATRIX_TYPE) -> float:
        '''Determinant of a 2x2 matrix.

        Args:
            value (MATRIX_TYPE): 2x2 input matrix

        Returns:
            float
        '''

        value = cls._force_dim(value, use_fill_for_scalar=True)
        return cls._determinant(value)

    @classmethod
    def transpose(cls, value: MATRIX_TYPE) -> 'Matrix2x2':
        '''Transpose of a 2x2 matrix.

        Args:
            value (MATRIX_TYPE): 2x2 input matrix

        Returns:
            float
        '''

        value = cls._force_dim(value, use_fill_for_scalar=True)
        return Matrix2x2(value[0], value[2], value[1], value[3])

    @classmethod
    def inverse(cls, value: MATRIX_TYPE) -> 'Matrix2x2':
        '''Inverse of a 2x2 matrix.

        Args:
            value (MATRIX_TYPE): 2x2 input matrix

        Returns:
            float
        '''

        value = cls._force_dim(value, use_fill_for_scalar=True)
        det = cls._determinant(value)

        if det == 0.0:
            raise MatrixException('Matrix has no inverse.')

        return Matrix2x2(value[3], -value[1], -value[2], value[0]) / det

    @classmethod
    def normalize(cls, value: MATRIX_TYPE) -> 'Matrix2x2':
        ''' Matrix normalization.

        Args:
            value (MATRIX_TYPE): Matrix to evaluate.

        Returns:
            Matrix2x2
        '''

        value = cls._force_dim(value, use_fill_for_scalar=True)
        det = cls._determinant(value)

        value = Matrix2x2(*value)
        value.column0 /= det
        value.column1 /= det

        return value
