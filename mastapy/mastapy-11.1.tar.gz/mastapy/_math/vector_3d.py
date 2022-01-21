'''vector_3d.py'''


import math
from typing import Tuple, Union, Iterable, Any

from mastapy._math import scalar
from mastapy._math.vector_base import (
    VectorException, NUM, ERROR_SET_MESSAGE,
    ERROR_SET_PROPERTY, _safe_vector_op)
from mastapy._math.vector_2d import Vector2D


__all__ = ('Vector3D',)


ERROR_3D_MESSAGE = 'Input vectors must be 3D for Vector3D calculations.'
safe_vector3_op = _safe_vector_op(ERROR_3D_MESSAGE)


class Vector3D(Vector2D):
    '''Create a Vector3D from X, Y and Z components

    Args:
        x: NUM
        y: NUM
        z: NUM

    Returns:
        Vector3D
    '''

    def __init__(self, x: NUM, y: NUM, z: NUM) -> 'Vector3D':
        self.wrapped = None
        super(Vector2D, self).__init__([float(x), float(y), float(z)])

    @classmethod
    def broadcast(cls, value: NUM) -> 'Vector3D':
        ''' Create a Vector3D by broadcasting a value to all of its dimensions

        Args:
            value: NUM

        Returns:
            Vector3D
        '''

        return cls(value, value, value)

    @classmethod
    def from_iterable(cls, t: Iterable[NUM]) -> 'Vector3D':
        ''' Create a Vector3D from an Iterable

        Args:
            t: Iterable[NUM]

        Returns:
            Vector3D
        '''

        t = tuple(t)

        try:
            return cls(t[0], t[1], t[2])
        except (KeyError, TypeError, AttributeError):
            raise VectorException(
                'Tuple must be of at least length 3.') from None

    @classmethod
    def wrap(cls, value: Any) -> 'Vector3D':
        try:
            new_vector = cls(value.X, value.Y, value.Z)
            new_vector.wrapped = value
            return new_vector
        except AttributeError:
            raise VectorException('Value to wrap has no X, Y or Z component.')

    @property
    def z(self) -> float:
        ''' Get the Z component of the vector

        Returns:
            float
        '''

        return self[2]

    @z.setter
    def z(self, value: NUM):
        self[2] = float(value)
        if self.wrapped:
            raise VectorException(ERROR_SET_PROPERTY) from None

    @property
    def xz(self) -> Vector2D:
        ''' Get the XZ components of the vector

        Returns:
            Vector2D
        '''

        return Vector2D(self.x, self.z)

    @xz.setter
    def xz(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 2)
                self.x = values[0]
                self.z = values[1]
            else:
                self.x = self.z = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def yz(self) -> Vector2D:
        ''' Get the YZ components of the vector

        Returns:
            Vector2D
        '''

        return Vector2D(self.y, self.z)

    @yz.setter
    def yz(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 2)
                self.y = values[0]
                self.z = values[1]
            else:
                self.y = self.z = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def zx(self) -> Vector2D:
        ''' Get the ZX components of the vector

        Returns:
            Vector2D
        '''

        return Vector2D(self.z, self.x)

    @zx.setter
    def zx(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 2)
                self.z = values[0]
                self.x = values[1]
            else:
                self.z = self.x = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def zy(self) -> Vector2D:
        ''' Get the ZY components of the vector

        Returns:
            Vector2D
        '''

        return Vector2D(self.z, self.y)

    @zy.setter
    def zy(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 2)
                self.z = values[0]
                self.y = values[1]
            else:
                self.z = self.y = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def zz(self) -> Vector2D:
        ''' Get the ZZ components of the vector

        Returns:
            Vector2D
        '''

        return Vector2D.broadcast(self.z)

    @property
    def xxx(self) -> 'Vector3D':
        ''' Get the XXX components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D.broadcast(self.x)

    @property
    def xxy(self) -> 'Vector3D':
        ''' Get the XXY components of the vector

        Returns:
            Vector3D

        '''

        return Vector3D(self.x, self.x, self.y)

    @property
    def xxz(self) -> 'Vector3D':
        ''' Get the XXZ components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.x, self.x, self.z)

    @property
    def xyx(self) -> 'Vector3D':
        ''' Get the XYX components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.x, self.y, self.x)

    @property
    def xyy(self) -> 'Vector3D':
        ''' Get the XYY components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.x, self.y, self.y)

    @property
    def xyz(self) -> 'Vector3D':
        ''' Get the XYZ components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.x, self.y, self.z)

    @xyz.setter
    def xyz(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 3)
                self.x = values[0]
                self.y = values[1]
                self.z = values[2]
            else:
                self.z = self.y = self.z = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def xzx(self) -> 'Vector3D':
        ''' Get the XZX components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.x, self.z, self.x)

    @property
    def xzy(self) -> 'Vector3D':
        ''' Get the XZY components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.x, self.z, self.y)

    @xzy.setter
    def xzy(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 3)
                self.x = values[0]
                self.z = values[1]
                self.y = values[2]
            else:
                self.x = self.z = self.y = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def xzz(self) -> 'Vector3D':
        ''' Get the XZZ components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.x, self.z, self.z)

    @property
    def yxx(self) -> 'Vector3D':
        ''' Get the YXX components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.y, self.x, self.x)

    @property
    def yxy(self) -> 'Vector3D':
        ''' Get the YXY components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.y, self.x, self.y)

    @property
    def yxz(self) -> 'Vector3D':
        ''' Get the YXZ components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.y, self.x, self.z)

    @yxz.setter
    def yxz(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 3)
                self.y = values[0]
                self.x = values[1]
                self.z = values[2]
            else:
                self.y = self.x = self.z = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def yyx(self) -> 'Vector3D':
        ''' Get the YYX components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.y, self.y, self.x)

    @property
    def yyy(self) -> 'Vector3D':
        ''' Get the YYY components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D.broadcast(self.y)

    @property
    def yyz(self) -> 'Vector3D':
        ''' Get the YYZ components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.y, self.y, self.z)

    @property
    def yzx(self) -> 'Vector3D':
        ''' Get the YZX components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.y, self.z, self.x)

    @yzx.setter
    def yzx(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 3)
                self.y = values[0]
                self.z = values[1]
                self.x = values[2]
            else:
                self.y = self.z = self.x = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def yzy(self) -> 'Vector3D':
        ''' Get the YZY components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.y, self.z, self.y)

    @property
    def yzz(self) -> 'Vector3D':
        ''' Get the YZZ components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.y, self.z, self.z)

    @property
    def zxx(self) -> 'Vector3D':
        ''' Get the ZXX components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.z, self.x, self.x)

    @property
    def zxy(self) -> 'Vector3D':
        ''' Get the ZXY components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.z, self.x, self.y)

    @zxy.setter
    def zxy(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 3)
                self.z = values[0]
                self.x = values[1]
                self.y = values[2]
            else:
                self.z = self.x = self.y = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def zxz(self) -> 'Vector3D':
        ''' Get the ZXZ components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.z, self.x, self.z)

    @property
    def zyx(self) -> 'Vector3D':
        ''' Get the ZYX components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.z, self.y, self.x)

    @zyx.setter
    def zyx(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 3)
                self.z = values[0]
                self.y = values[1]
                self.x = values[2]
            else:
                self.z = self.y = self.x = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def zyy(self) -> 'Vector3D':
        ''' Get the ZYY components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.z, self.y, self.y)

    @property
    def zyz(self) -> 'Vector3D':
        ''' Get the ZYZ components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.z, self.y, self.z)

    @property
    def zzx(self) -> 'Vector3D':
        ''' Get the ZZX components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.z, self.z, self.x)

    @property
    def zzy(self) -> 'Vector3D':
        ''' Get the ZZY components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.z, self.z, self.y)

    @property
    def zzz(self) -> 'Vector3D':
        ''' Get the ZZZ components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D.broadcast(self.z)

    def __add__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector3D':
        other = Vector3D._force_dim(other)

        x = self.x + other[0]
        y = self.y + other[1]
        z = self.z + other[2]
        return Vector3D(x, y, z)

    def __radd__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector3D':
        other = Vector3D._force_dim(other)

        x = other[0] + self.x
        y = other[1] + self.y
        z = other[2] + self.z
        return Vector3D(x, y, z)

    def __sub__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector3D':
        other = Vector3D._force_dim(other)

        x = self.x - other[0]
        y = self.y - other[1]
        z = self.z - other[2]
        return Vector3D(x, y, z)

    def __rsub__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector3D':
        other = Vector3D._force_dim(other)

        x = other[0] - self.x
        y = other[1] - self.y
        z = other[2] - self.z
        return Vector3D(x, y, z)

    def __mul__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector3D':
        other = Vector3D._force_dim(other)

        x = self.x * other[0]
        y = self.y * other[1]
        z = self.z * other[2]
        return Vector3D(x, y, z)

    def __rmul__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector3D':
        other = Vector3D._force_dim(other)

        x = other[0] * self.x
        y = other[1] * self.y
        z = other[2] * self.z
        return Vector3D(x, y, z)

    def __matmul__(self, other: Union[NUM, Iterable[NUM]]) -> float:
        return Vector3D.dot(self, other)

    def __rmatmul__(self, other: Union[NUM, Iterable[NUM]]) -> float:
        return Vector3D.dot(other, self)

    def __truediv__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector3D':
        other = Vector3D._force_dim(other)

        x = self.x / other[0]
        y = self.y / other[1]
        z = self.z / other[2]
        return Vector3D(x, y, z)

    def __rtruediv__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector3D':
        other = Vector3D._force_dim(other)

        x = other[0] / self.x
        y = other[1] / self.y
        z = other[2] / self.z
        return Vector3D(x, y, z)

    def __floordiv__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector3D':
        other = Vector3D._force_dim(other)

        x = self.x // other[0]
        y = self.y // other[1]
        z = self.z // other[2]
        return Vector3D(x, y, z)

    def __rfloordiv__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector3D':
        other = Vector3D._force_dim(other)

        x = other[0] // self.x
        y = other[1] // self.y
        z = other[2] // self.z
        return Vector3D(x, y, z)

    def __abs__(self) -> 'Vector3D':
        x = abs(self.x)
        y = abs(self.y)
        z = abs(self.z)
        return Vector3D(x, y, z)

    def __mod__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector3D':
        other = Vector3D._force_dim(other)

        x = self.x % other[0]
        y = self.y % other[1]
        z = self.z % other[2]
        return Vector3D(x, y, z)

    def __rmod__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector3D':
        other = Vector3D._force_dim(other)

        x = other[0] % self.x
        y = other[1] % self.y
        z = other[2] % self.z
        return Vector3D(x, y, z)

    def __pow__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector3D':
        return Vector3D.pow(self, other)

    def __pos__(self) -> 'Vector3D':
        return Vector3D(+self.x, +self.y, +self.z)

    def __neg__(self) -> 'Vector3D':
        return Vector3D(-self.x, -self.y, -self.z)

    @classmethod
    def _force_dim(cls, v: Union[NUM, Iterable[NUM]]) -> Tuple[NUM]:
        b = hasattr(v, '__iter__')

        if b and len(v) != 3:
            raise VectorException(ERROR_3D_MESSAGE)
        elif not b:
            v = (v, v, v)

        return tuple(v)

    @classmethod
    def _make_vec(cls, v: Union[NUM, Iterable[NUM]]) -> 'Vector3D':
        return Vector3D.from_iterable(cls._force_dim(v))

    @classmethod
    def zero() -> 'Vector3D':
        ''' Returns a Vector3D filled with 0s

        Returns:
            Vector3D
        '''

        return Vector3D.broadcast(0)

    @classmethod
    def one() -> 'Vector3D':
        ''' Returns a Vector3D filled with 1s

        Returns:
            Vector3D
        '''

        return Vector3D.broadcast(1)

    @classmethod
    def approximately_equal(
            cls,
            v0: Iterable[NUM],
            v1: Union[NUM, Iterable[NUM]],
            epsilon: NUM = 0.001) -> Tuple[bool]:
        ''' Component-wise approximately equal comparison.

        Args:
            v0 (Iterable[NUM]): First vector to compare
            v1 (Union[NUM, Iterable[NUM]]): Second value to compare
            epsilon (NUM, default=0.001): Sensitivity of the equals operation

        Returns:
            Tuple[bool]
        '''

        def _approximately_equals(v0, v1, e):
            v0 = tuple(v0)
            v1 = cls._force_dim(v1)

            x = scalar.approximately_equal(v0[0], v1[0], e)
            y = scalar.approximately_equal(v0[1], v1[1], e)
            z = scalar.approximately_equal(v0[2], v1[2], e)

            return x, y, z

        return safe_vector3_op(_approximately_equals, v0, v1, epsilon)

    @classmethod
    def min(
            cls,
            v0: Iterable[NUM],
            v1: Union[NUM, Iterable[NUM]]) -> 'Vector3D':
        ''' Component-wise min.

        Args:
            v0 (Iterable[NUM]): First vector to compare
            v1 (Union[NUM, Iterable[NUM]]): Second value to compare

        Returns:
            Vector3D
        '''

        def _min(v0, v1):
            v0 = tuple(v0)
            v1 = cls._force_dim(v1)

            x = min(v0[0], v1[0])
            y = min(v0[1], v1[1])
            z = min(v0[2], v1[2])

            return Vector3D(x, y, z)

        return safe_vector3_op(_min, v0, v1)

    @classmethod
    def max(
            cls,
            v0: Iterable[NUM],
            v1: Union[NUM, Iterable[NUM]]) -> 'Vector3D':
        ''' Component-wise max.

        Args:
            v0 (Iterable[NUM]): First vector to compare
            v1 (Union[NUM, Iterable[NUM]]): Second value to compare

        Returns:
            Vector3D
        '''

        def _max(v0, v1):
            v0 = tuple(v0)
            v1 = cls._force_dim(v1)

            x = max(v0[0], v1[0])
            y = max(v0[1], v1[1])
            z = max(v0[2], v1[2])

            return Vector3D(x, y, z)

        return safe_vector3_op(_max, v0, v1)

    @classmethod
    def clamp(
            cls,
            v: Iterable[NUM],
            vmin: Union[NUM, Iterable[NUM]],
            vmax: Union[NUM, Iterable[NUM]]) -> 'Vector3D':
        ''' Component-wise clamp.

        Equivalent to min(vmax, max(vmin, v))

        Args:
            v (Iterable[NUM]): Vector to clamp
            vmin (Union[NUM, Iterable[NUM]]):
                Lower end of the range into which to constrain v
            vmax (Union[NUM, Iterable[NUM]]):
                Upper end of the range into which to constrain v

        Returns:
            Vector3D
        '''

        def _clamp(v, vmin, vmax):
            v = tuple(v)

            min_is_iter = hasattr(vmin, '__iter__')
            max_is_iter = hasattr(vmax, '__iter__')

            if min_is_iter ^ max_is_iter:
                raise VectorException(
                    ('vmin and vmax must either both be '
                     'vectors or both be scalars.'))
            elif not min_is_iter and not max_is_iter:
                vmin = (vmin, vmin)
                vmax = (vmax, vmax)

            x = scalar.clamp(v[0], vmin[0], vmax[0])
            y = scalar.clamp(v[1], vmin[1], vmax[1])
            z = scalar.clamp(v[2], vmin[2], vmax[2])

            return Vector3D(x, y, z)

        return safe_vector3_op(_clamp, v, vmin, vmax)

    @classmethod
    def interpolate(
            cls,
            v0: Iterable[NUM],
            v1: Iterable[NUM],
            i: Union[NUM, Iterable[NUM]]) -> 'Vector3D':
        ''' Component-wise interpolation.

        Equivalent to v0 * (1.0 - i) + v1 * i

        Args:
            v0 (Iterable[NUM]): Start of the range in which to interpolate
            v1 (Iterable[NUM]): End of the range in which to interpolate
            i (Union[NUM, Iterable[NUM]]):
                Value to use to interpolate between v0 and v1

        Returns:
            Vector3D
        '''

        v0 = cls._make_vec(v0)
        v1 = cls._make_vec(v1)
        i = cls._make_vec(i)

        return v0 * (1.0 - i) + v1 * i

    @classmethod
    def sign(cls, v: Iterable[NUM]) -> 'Vector3D':
        ''' Component-wise extraction of the sign.

        Returns -1.0 if v is less than 0.0, 0.0 if v is equal to 0.0,
        and +1.0 if v is greater than 0.0.

        Args:
            v (Iterable[NUM]): Vector from which to extract the sign.

        Returns:
            Vector3D
        '''

        def _sign(v):
            v = tuple(v)

            x = scalar.sign(v[0])
            y = scalar.sign(v[1])
            z = scalar.sign(v[2])
            return Vector3D(x, y, z)

        return safe_vector3_op(_sign, v)

    @classmethod
    def floor(cls, v: Iterable[NUM]) -> 'Vector3D':
        ''' Component-wise floor.

        Args:
            v (Iterable[NUM]): Vector to floor.

        Returns:
            Vector3D
        '''

        def _floor(v):
            v = tuple(v)

            x = math.floor(v[0])
            y = math.floor(v[1])
            z = math.floor(v[2])
            return Vector3D(x, y, z)

        return safe_vector3_op(_floor, v)

    @classmethod
    def ceil(cls, v: Iterable[NUM]) -> 'Vector3D':
        ''' Component-wise ceil.

        Args:
            v (Iterable[NUM]): Vector to ceil.

        Returns:
            Vector3D
        '''

        def _ceil(v):
            v = tuple(v)

            x = math.ceil(v[0])
            y = math.ceil(v[1])
            z = math.ceil(v[2])
            return Vector3D(x, y, z)

        return safe_vector3_op(_ceil, v)

    @classmethod
    def fract(cls, v: Iterable[NUM]) -> 'Vector3D':
        ''' Component-wise extraction of the fractional part of the parameter.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector3D
        '''

        def _fract(v):
            v = tuple(v)

            x = scalar.fract(v[0])
            y = scalar.fract(v[1])
            z = scalar.fract(v[2])
            return Vector3D(x, y, z)

        return safe_vector3_op(_fract, v)

    @classmethod
    def step(
            cls,
            edge: Union[NUM, Iterable[NUM]],
            v: Iterable[NUM]) -> 'Vector3D':
        ''' Component-wise step.

        For each index i, 0.0 is returned if v[i] < edge[i], and 1.0 is
        returned otherwise.

        Args:
            edge (Union[NUM, Iterable[NUM]]): Edge of the step function.
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector3D
        '''

        def _step(edge, v):
            v = tuple(v)
            edge = cls._force_dim(edge)

            x = scalar.step(edge[0], v[0])
            y = scalar.step(edge[1], v[1])
            z = scalar.step(edge[2], v[2])
            return Vector3D(x, y, z)

        return safe_vector3_op(_step, edge, v)

    @classmethod
    def smoothstep(
            cls,
            edge0: Union[NUM, Iterable[NUM]],
            edge1: Union[NUM, Iterable[NUM]],
            v: Iterable[NUM]) -> 'Vector3D':
        ''' Component-wise hermite interpolation between two values.

        Args:
            edge0 (Union[NUM, Iterable[NUM]]):
                Lower edge of the hermite function.
            edge1 (Union[NUM, Iterable[NUM]]):
                Upper edge of the hermite function.
            v (Iterable[NUM]): Vector to interpolate.

        Returns:
            Vector3D
        '''

        def _smoothstep(edge0, edge1, v):
            v = tuple(v)
            edge0 = cls._force_dim(edge0)
            edge1 = cls._force_dim(edge1)

            x = scalar.smoothstep(edge0[0], edge1[0], v[0])
            y = scalar.smoothstep(edge0[1], edge1[1], v[1])
            z = scalar.smoothstep(edge0[2], edge1[2], v[2])
            return Vector3D(x, y, z)

        return safe_vector3_op(_smoothstep, edge0, edge1, v)

    @classmethod
    def sqrt(cls, v: Iterable[NUM]) -> 'Vector3D':
        ''' Component-wise square root.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector3D
        '''

        def _sqrt(v):
            v = tuple(v)

            x = math.sqrt(v[0])
            y = math.sqrt(v[1])
            z = math.sqrt(v[2])
            return Vector3D(x, y, z)

        return safe_vector3_op(_sqrt, v)

    @classmethod
    def inverse_sqrt(cls, v: Iterable[NUM]) -> 'Vector3D':
        ''' Component-wise inverse square root.

        This is equivalent to 1.0 / Vector3D.sqrt(v).

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector3D
        '''

        def _inverse_sqrt(v):
            v = tuple(v)

            x = 1.0 / math.sqrt(v[0])
            y = 1.0 / math.sqrt(v[1])
            z = 1.0 / math.sqrt(v[2])
            return Vector3D(x, y, z)

        return safe_vector3_op(_inverse_sqrt, v)

    @classmethod
    def pow(cls, v: Iterable[NUM], w: Union[NUM, Iterable[NUM]]) -> 'Vector3D':
        ''' Component-wise power.

        Args:
            v (Iterable[NUM]): Vector to evaluate.
            w (Union[NUM, Iterable[NUM]]): Power to which to raise v.

        Returns:
            Vector3D
        '''

        def _pow(v, w):
            v = tuple(v)
            w = cls._force_dim(w)

            x = v[0] ** w[0]
            y = v[1] ** w[1]
            z = v[2] ** w[2]
            return Vector3D(x, y, z)

        return safe_vector3_op(_pow, v, w)

    @classmethod
    def exp(cls, v: Iterable[NUM]) -> 'Vector3D':
        ''' Component-wise natural exponential.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector3D
        '''

        def _exp(v):
            v = tuple(v)

            x = math.exp(v[0])
            y = math.exp(v[1])
            z = math.exp(v[2])
            return Vector3D(x, y, z)

        return safe_vector3_op(_exp, v)

    @classmethod
    def exp2(cls, v: Iterable[NUM]) -> 'Vector3D':
        ''' Component-wise. 2 raised to the power of the parameter.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector3D
        '''

        def _exp2(v):
            v = tuple(v)

            x = 2 ** v[0]
            y = 2 ** v[1]
            z = 2 ** v[2]
            return Vector3D(x, y, z)

        return safe_vector3_op(_exp2, v)

    @classmethod
    def exp10(cls, v: Iterable[NUM]) -> 'Vector3D':
        ''' Component-wise. 10 raised to the power of the parameter.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector3D
        '''

        def _exp10(v):
            v = tuple(v)

            x = 10 ** v[0]
            y = 10 ** v[1]
            z = 10 ** v[2]
            return Vector3D(x, y, z)

        return safe_vector3_op(_exp10, v)

    @classmethod
    def log(cls, v: Iterable[NUM]) -> 'Vector3D':
        ''' Component-wise natural logarithm.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector3D
        '''

        def _log(v):
            v = tuple(v)

            x = math.log(v[0])
            y = math.log(v[1])
            z = math.log(v[2])
            return Vector3D(x, y, z)

        return safe_vector3_op(_log, v)

    @classmethod
    def log2(cls, v: Iterable[NUM]) -> 'Vector3D':
        ''' Component-wise base-2 logarithm.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector3D
        '''

        def _log2(v):
            v = tuple(v)

            x = math.log2(v[0])
            y = math.log2(v[1])
            z = math.log2(v[2])
            return Vector3D(x, y, z)

        return safe_vector3_op(_log2, v)

    @classmethod
    def log10(cls, v: Iterable[NUM]) -> 'Vector3D':
        ''' Component-wise base-10 logarithm.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector3D
        '''

        def _log10(v):
            v = tuple(v)

            x = math.log10(v[0])
            y = math.log10(v[1])
            z = math.log10(v[2])
            return Vector3D(x, y, z)

        return safe_vector3_op(_log10, v)

    @classmethod
    def radians(cls, v: Iterable[NUM]) -> 'Vector3D':
        ''' Component-wise conversion from degrees to radians.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector3D
        '''

        def _radians(v):
            v = tuple(v)

            x = math.radians(v[0])
            y = math.radians(v[1])
            z = math.radians(v[2])
            return Vector3D(x, y, z)

        return safe_vector3_op(_radians, v)

    @classmethod
    def degrees(cls, v: Iterable[NUM]) -> 'Vector3D':
        ''' Component-wise conversion from radians to degrees.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector3D
        '''

        def _degrees(v):
            v = tuple(v)

            x = math.degrees(v[0])
            y = math.degrees(v[1])
            z = math.degrees(v[2])
            return Vector3D(x, y, z)

        return safe_vector3_op(_degrees, v)

    @classmethod
    def sin(cls, v: Iterable[NUM]) -> 'Vector3D':
        ''' Component-wise sine.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector3D
        '''

        def _sin(v):
            v = tuple(v)

            x = math.sin(v[0])
            y = math.sin(v[1])
            z = math.sin(v[2])
            return Vector3D(x, y, z)

        return safe_vector3_op(_sin, v)

    @classmethod
    def cos(cls, v: Iterable[NUM]) -> 'Vector3D':
        ''' Component-wise cosine.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector3D
        '''

        def _cos(v):
            v = tuple(v)

            x = math.cos(v[0])
            y = math.cos(v[1])
            z = math.cos(v[2])
            return Vector3D(x, y, z)

        return safe_vector3_op(_cos, v)

    @classmethod
    def tan(cls, v: Iterable[NUM]) -> 'Vector3D':
        ''' Component-wise tangent.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector3D
        '''

        def _tan(v):
            v = tuple(v)

            x = math.tan(v[0])
            y = math.tan(v[1])
            z = math.tan(v[2])
            return Vector3D(x, y, z)

        return safe_vector3_op(_tan, v)

    @classmethod
    def sinh(cls, v: Iterable[NUM]) -> 'Vector3D':
        ''' Component-wise hyperbolic sine.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector3D
        '''

        def _sinh(v):
            v = tuple(v)

            x = math.sinh(v[0])
            y = math.sinh(v[1])
            z = math.sinh(v[2])
            return Vector3D(x, y, z)

        return safe_vector3_op(_sinh, v)

    @classmethod
    def cosh(cls, v: Iterable[NUM]) -> 'Vector3D':
        ''' Component-wise hyperbolic cosine.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector3D
        '''

        def _cosh(v):
            v = tuple(v)

            x = math.cosh(v[0])
            y = math.cosh(v[1])
            z = math.cosh(v[2])
            return Vector3D(x, y, z)

        return safe_vector3_op(_cosh, v)

    @classmethod
    def tanh(cls, v: Iterable[NUM]) -> 'Vector3D':
        ''' Component-wise hyperbolic tangent.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector3D
        '''

        def _tanh(v):
            v = tuple(v)

            x = math.tanh(v[0])
            y = math.tanh(v[1])
            z = math.tanh(v[2])
            return Vector3D(x, y, z)

        return safe_vector3_op(_tanh, v)

    @classmethod
    def asin(cls, v: Iterable[NUM]) -> 'Vector3D':
        ''' Component-wise arc-sine.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector3D
        '''

        def _asin(v):
            v = tuple(v)

            x = math.asin(v[0])
            y = math.asin(v[1])
            z = math.asin(v[2])
            return Vector3D(x, y, z)

        return safe_vector3_op(_asin, v)

    @classmethod
    def acos(cls, v: Iterable[NUM]) -> 'Vector3D':
        ''' Component-wise arc-cosine.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector3D
        '''

        def _acos(v):
            v = tuple(v)

            x = math.acos(v[0])
            y = math.acos(v[1])
            z = math.acos(v[2])
            return Vector3D(x, y, z)

        return safe_vector3_op(_acos, v)

    @classmethod
    def atan(cls, v: Iterable[NUM]) -> 'Vector3D':
        ''' Component-wise arc-tangent.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector3D
        '''

        def _atan(v):
            v = tuple(v)

            x = math.atan(v[0])
            y = math.atan(v[1])
            z = math.atan(v[2])
            return Vector3D(x, y, z)

        return safe_vector3_op(_atan, v)

    @classmethod
    def atan2(
            cls, v: Iterable[NUM], w: Union[NUM, Iterable[NUM]]) -> 'Vector3D':
        ''' Component-wise arc-tangent with separable numerator
        and denominator.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector3D
        '''

        def _atan2(v, w):
            v = tuple(v)
            w = cls._force_dim(w)

            x = math.atan2(v[0], w[0])
            y = math.atan2(v[1], w[1])
            z = math.atan2(v[2], w[2])
            return Vector3D(x, y, z)

        return safe_vector3_op(_atan2, v, w)

    @classmethod
    def asinh(cls, v: Iterable[NUM]) -> 'Vector3D':
        ''' Component-wise hyperbolic arc-sine.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector3D
        '''

        def _asinh(v):
            v = tuple(v)

            x = math.asinh(v[0])
            y = math.asinh(v[1])
            z = math.asinh(v[2])
            return Vector3D(x, y, z)

        return safe_vector3_op(_asinh, v)

    @classmethod
    def acosh(cls, v: Iterable[NUM]) -> 'Vector3D':
        ''' Component-wise hyperbolic arc-cosine.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector3D
        '''

        def _acosh(v):
            v = tuple(v)

            x = math.acosh(v[0])
            y = math.acosh(v[1])
            z = math.acosh(v[2])
            return Vector3D(x, y, z)

        return safe_vector3_op(_acosh, v)

    @classmethod
    def atanh(cls, v: Iterable[NUM]) -> 'Vector3D':
        ''' Component-wise hyperbolic arc-tangent.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector3D
        '''

        def _atanh(v):
            v = tuple(v)

            x = math.atanh(v[0])
            y = math.atanh(v[1])
            z = math.atanh(v[2])
            return Vector3D(x, y, z)

        return safe_vector3_op(_atanh, v)

    @classmethod
    def _dot(cls, v0: 'Vector3D', v1: 'Vector3D') -> float:
        return v0[0] * v1[0] + v0[1] * v1[1] + v0[2] * v1[2]

    @classmethod
    def dot(cls, v0: Iterable[NUM], v1: Iterable[NUM]) -> float:
        ''' Dot product of two vectors.

        Args:
            v0 (Iterable[NUM]): First Vector of dot product.
            v1 (Iterable[NUM]): Second vector of dot product.

        Returns:
            float
        '''

        def _d(v0, v1):
            v0 = tuple(v0)
            v1 = tuple(v1)

            return cls._dot(v0, v1)

        return safe_vector3_op(_d, v0, v1)

    @classmethod
    def cross(cls, v0: Iterable[NUM], v1: Iterable[NUM]) -> 'Vector3D':
        ''' Cross product of two vectors.

        Args:
            v0 (Iterable[NUM]): First Vector of cross product.
            v1 (Iterable[NUM]): Second vector of cross product.

        Returns:
            Vector3D
        '''

        def _cross(v0, v1):
            v0 = tuple(v0)
            v1 = tuple(v1)

            x = v0[1] * v1[2] - v1[1] * v0[2]
            y = v0[2] * v1[0] - v1[2] * v0[0]
            z = v0[0] * v1[1] - v1[0] * v0[1]

            return Vector3D(x, y, z)

        return safe_vector3_op(_cross, v0, v1)

    @classmethod
    def _length(cls, v: 'Vector3D') -> float:
        return math.sqrt(cls._dot(v, v))

    @classmethod
    def length(cls, v: Iterable[NUM]) -> float:
        ''' The length (or magnitude) of the vector.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            float
        '''

        v = cls._make_vec(v)

        return cls._length(v)

    @classmethod
    def distance(cls, v0: Iterable[NUM], v1: Iterable[NUM]) -> float:
        ''' Distance between two vectors.

        Calculated as length(v0 - v1).

        Args:
            v0 (Iterable[NUM]): First vector of distance calculation.
            v1 (Iterable[NUM]): Second vector of distance calculation.

        Returns:
            float
        '''

        v0 = cls._make_vec(v0)
        v1 = cls._make_vec(v1)

        return cls._length(v0 - v1)

    @classmethod
    def normalize(cls, v: Iterable[NUM]) -> 'Vector3D':
        ''' Vector normalization.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector3D
        '''

        v = cls._make_vec(v)

        return v / cls._length(v)

    @classmethod
    def face_forward(
            cls,
            v: Iterable[NUM],
            i: Iterable[NUM],
            vref: Iterable[NUM]) -> 'Vector3D':
        ''' Return a vector pointing in the same direction as another.

        If dot(vref, i) < 0.0, returns v. Otherwise returns -v.

        Args:
            v (Iterable[NUM]): Vector to orient.
            i (Iterable[NUM]): Incident vector.
            vref (Iterable[NUM]): Reference vector.

        Returns:
            Vector3D
        '''

        v = cls._make_vec(v)
        i = cls._make_vec(i)
        vref = cls._make_vec(vref)

        return v if cls._dot(vref, i) < 0.0 else -v

    @classmethod
    def reflect(cls, i: Iterable[NUM], n: Iterable[NUM]) -> 'Vector3D':
        ''' Reflection direction of an incident vector.

        Note:
            n should be normalized.

        Args:
            i (Iterable[NUM]): Incident vector.
            n (Iterable[NUM]): Normal vector.

        Returns:
            Vector3D
        '''

        i = cls._make_vec(i)
        n = cls._make_vec(n)

        return i - 2.0 * cls._dot(n, i) * n

    @classmethod
    def refract(
            cls, i: Iterable[NUM], n: Iterable[NUM], r: float) -> 'Vector3D':
        ''' Refraction direction of an incident vector.

        Note:
            i and n should be normalized.

        Args:
            i (Iterable[NUM]): Incident vector.
            n (Iterable[NUM]): Normal vector.
            r (float): Ratio of indices of refraction.

        Returns:
            Vector3D
        '''

        i = cls._make_vec(i)
        n = cls._make_vec(n)

        ndoti = cls._dot(n, i)
        d = 1.0 - r * r * (1.0 - ndoti * ndoti)

        # Total internal reflection
        if d < 0.0:
            return 0.0

        return r * i - (r * ndoti + math.sqrt(d)) * n
