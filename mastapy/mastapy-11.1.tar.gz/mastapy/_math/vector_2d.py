'''vector_2d.py'''

import math
from typing import Tuple, Union, Iterable, Any

from mastapy._math import scalar
from mastapy._math.vector_base import (
    VectorBase, VectorException, NUM, ERROR_SET_MESSAGE,
    ERROR_SET_PROPERTY, _safe_vector_op, ERROR_TUPLE)


__all__ = ('Vector2D',)


ERROR_2D_MESSAGE = 'Input vectors must be 2D for Vector2D calculations.'
safe_vector2_op = _safe_vector_op(ERROR_2D_MESSAGE)


class Vector2D(VectorBase):
    ''' Create a Vector2D from X and Y components

    Args:
        x: NUM
        y: NUM

    Returns:
        Vector2D
    '''

    def __init__(self, x: NUM, y: NUM) -> 'Vector2D':
        self.wrapped = None
        super().__init__([float(x), float(y)])

    @classmethod
    def broadcast(cls, value: NUM) -> 'Vector2D':
        ''' Create a Vector2D by broadcasting a value to all of its dimensions

        Args:
            value: NUM

        Returns:
            Vector2D
        '''

        return cls(value, value)

    @classmethod
    def from_iterable(cls, t: Iterable[NUM]) -> 'Vector2D':
        ''' Create a Vector2D from an Iterable

        Args:
            t: Iterable[NUM]

        Returns:
            Vector2D
        '''

        t = tuple(t)

        try:
            return cls(t[0], t[1])
        except ERROR_TUPLE:
            raise VectorException(
                'Tuple must be of at least length 2.') from None

    @classmethod
    def wrap(cls, value: Any) -> 'Vector2D':
        try:
            new_vector = cls(value.X, value.Y)
            new_vector.wrapped = value
            return new_vector
        except AttributeError:
            raise VectorException('Value to wrap has no X or Y component.')

    @property
    def x(self) -> float:
        ''' Get the X component of the vector

        Returns:
            float
        '''

        return self[0]

    @x.setter
    def x(self, value: NUM):
        self[0] = float(value)
        if self.wrapped:
            raise VectorException(ERROR_SET_PROPERTY) from None

    @property
    def y(self) -> float:
        ''' Get the Y component of the vector

        Returns:
            float
        '''

        return self[1]

    @y.setter
    def y(self, value: NUM):
        self[1] = float(value)
        if self.wrapped:
            raise VectorException(ERROR_SET_PROPERTY) from None

    @property
    def xx(self) -> 'Vector2D':
        ''' Get the XX components of the vector

        Returns:
            Vector2D
        '''

        return Vector2D.broadcast(self.x)

    @property
    def xy(self) -> 'Vector2D':
        ''' Get the XY components of the vector

        Returns:
            Vector2D
        '''

        return Vector2D(self.x, self.y)

    @xy.setter
    def xy(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 2)
                self.x = values[0]
                self.y = values[1]
            else:
                self.x = self.y = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def yx(self) -> 'Vector2D':
        ''' Get the YX components of the vector

        Returns:
            Vector2D
        '''

        return Vector2D(self.y, self.x)

    @yx.setter
    def yx(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 2)
                self.y = values[0]
                self.x = values[1]
            else:
                self.y = self.x = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def yy(self) -> 'Vector2D':
        ''' Get the YY components of the vector

        Returns:
            Vector2D
        '''

        return Vector2D.broadcast(self.y)

    def __add__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector2D':
        other = Vector2D._force_dim(other)

        x = self.x + other[0]
        y = self.y + other[1]
        return Vector2D(x, y)

    def __radd__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector2D':
        other = Vector2D._force_dim(other)

        x = other[0] + self.x
        y = other[1] + self.y
        return Vector2D(x, y)

    def __sub__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector2D':
        other = Vector2D._force_dim(other)

        x = self.x - other[0]
        y = self.y - other[1]
        return Vector2D(x, y)

    def __rsub__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector2D':
        other = Vector2D._force_dim(other)

        x = other[0] - self.x
        y = other[1] - self.y
        return Vector2D(x, y)

    def __mul__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector2D':
        other = Vector2D._force_dim(other)

        x = self.x * other[0]
        y = self.y * other[1]
        return Vector2D(x, y)

    def __rmul__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector2D':
        other = Vector2D._force_dim(other)

        x = other[0] * self.x
        y = other[1] * self.y
        return Vector2D(x, y)

    def __matmul__(self, other: Union[NUM, Iterable[NUM]]) -> float:
        return Vector2D.dot(self, other)

    def __rmatmul__(self, other: Union[NUM, Iterable[NUM]]) -> float:
        return Vector2D.dot(other, self)

    def __truediv__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector2D':
        other = Vector2D._force_dim(other)

        x = self.x / other[0]
        y = self.y / other[1]
        return Vector2D(x, y)

    def __rtruediv__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector2D':
        other = Vector2D._force_dim(other)

        x = other[0] / self.x
        y = other[1] / self.y
        return Vector2D(x, y)

    def __floordiv__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector2D':
        other = Vector2D._force_dim(other)

        x = self.x // other[0]
        y = self.y // other[1]
        return Vector2D(x, y)

    def __rfloordiv__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector2D':
        other = Vector2D._force_dim(other)

        x = other[0] // self.x
        y = other[1] // self.y
        return Vector2D(x, y)

    def __abs__(self) -> 'Vector2D':
        x = abs(self.x)
        y = abs(self.y)
        return Vector2D(x, y)

    def __mod__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector2D':
        other = Vector2D._force_dim(other)

        x = self.x % other[0]
        y = self.y % other[1]
        return Vector2D(x, y)

    def __rmod__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector2D':
        other = Vector2D._force_dim(other)

        x = other[0] % self.x
        y = other[1] % self.y
        return Vector2D(x, y)

    def __pow__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector2D':
        return Vector2D.pow(self, other)

    def __pos__(self) -> 'Vector2D':
        return Vector2D(+self.x, +self.y)

    def __neg__(self) -> 'Vector2D':
        return Vector2D(-self.x, -self.y)

    @classmethod
    def _force_dim(cls, v: Union[NUM, Iterable[NUM]]) -> Tuple[NUM]:
        b = hasattr(v, '__iter__')

        if b and len(v) != 2:
            raise VectorException(ERROR_2D_MESSAGE)
        elif not b:
            v = (v, v)

        return tuple(v)

    @classmethod
    def _make_vec(cls, v: Union[NUM, Iterable[NUM]]) -> 'Vector2D':
        return Vector2D.from_iterable(cls._force_dim(v))

    @classmethod
    def zero() -> 'Vector2D':
        ''' Returns a Vector2D filled with 0s

        Returns:
            Vector2D
        '''

        return Vector2D.broadcast(0)

    @classmethod
    def one() -> 'Vector2D':
        ''' Returns a Vector2D filled with 1s

        Returns:
            Vector2D
        '''

        return Vector2D.broadcast(1)

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

            return x, y

        return safe_vector2_op(_approximately_equals, v0, v1, epsilon)

    @classmethod
    def min(
            cls,
            v0: Iterable[NUM],
            v1: Union[NUM, Iterable[NUM]]) -> 'Vector2D':
        ''' Component-wise min.

        Args:
            v0 (Iterable[NUM]): First vector to compare
            v1 (Union[NUM, Iterable[NUM]]): Second value to compare

        Returns:
            Vector2D
        '''

        def _min(v0, v1):
            v0 = tuple(v0)
            v1 = cls._force_dim(v1)

            x = min(v0[0], v1[0])
            y = min(v0[1], v1[1])

            return Vector2D(x, y)

        return safe_vector2_op(_min, v0, v1)

    @classmethod
    def max(
            cls,
            v0: Iterable[NUM],
            v1: Union[NUM, Iterable[NUM]]) -> 'Vector2D':
        ''' Component-wise max.

        Args:
            v0 (Iterable[NUM]): First vector to compare
            v1 (Union[NUM, Iterable[NUM]]): Second value to compare

        Returns:
            Vector2D
        '''

        def _max(v0, v1):
            v0 = tuple(v0)
            v1 = cls._force_dim(v1)

            x = max(v0[0], v1[0])
            y = max(v0[1], v1[1])

            return Vector2D(x, y)

        return safe_vector2_op(_max, v0, v1)

    @classmethod
    def clamp(
            cls,
            v: Iterable[NUM],
            vmin: Union[NUM, Iterable[NUM]],
            vmax: Union[NUM, Iterable[NUM]]) -> 'Vector2D':
        ''' Component-wise clamp.

        Equivalent to min(vmax, max(vmin, v))

        Args:
            v (Iterable[NUM]): Vector to clamp
            vmin (Union[NUM, Iterable[NUM]]):
                Lower end of the range into which to constrain v
            vmax (Union[NUM, Iterable[NUM]]):
                Upper end of the range into which to constrain v

        Returns:
            Vector2D
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

            vmin = tuple(vmin)
            vmax = tuple(vmax)

            x = scalar.clamp(v[0], vmin[0], vmax[0])
            y = scalar.clamp(v[1], vmin[1], vmax[1])

            return Vector2D(x, y)

        return safe_vector2_op(_clamp, v, vmin, vmax)

    @classmethod
    def interpolate(
            cls,
            v0: Iterable[NUM],
            v1: Iterable[NUM],
            i: Union[NUM, Iterable[NUM]]) -> 'Vector2D':
        ''' Component-wise interpolation.

        Equivalent to v0 * (1.0 - i) + v1 * i

        Args:
            v0 (Iterable[NUM]): Start of the range in which to interpolate
            v1 (Iterable[NUM]): End of the range in which to interpolate
            i (Union[NUM, Iterable[NUM]]):
                Value to use to interpolate between v0 and v1

        Returns:
            Vector2D
        '''

        v0 = cls._make_vec(v0)
        v1 = cls._make_vec(v1)
        i = cls._make_vec(i)

        return v0 * (1.0 - i) + v1 * i

    @classmethod
    def sign(cls, v: Iterable[NUM]) -> 'Vector2D':
        ''' Component-wise extraction of the sign.

        Returns -1.0 if v is less than 0.0, 0.0 if v is equal to 0.0,
        and +1.0 if v is greater than 0.0.

        Args:
            v (Iterable[NUM]): Vector from which to extract the sign.

        Returns:
            Vector2D
        '''

        def _sign(v):
            v = tuple(v)

            x = scalar.sign(v[0])
            y = scalar.sign(v[1])
            return Vector2D(x, y)

        return safe_vector2_op(_sign, v)

    @classmethod
    def floor(cls, v: Iterable[NUM]) -> 'Vector2D':
        ''' Component-wise floor.

        Args:
            v (Iterable[NUM]): Vector to floor.

        Returns:
            Vector2D
        '''

        def _floor(v):
            v = tuple(v)

            x = math.floor(v[0])
            y = math.floor(v[1])
            return Vector2D(x, y)

        return safe_vector2_op(_floor, v)

    @classmethod
    def ceil(cls, v: Iterable[NUM]) -> 'Vector2D':
        ''' Component-wise ceil.

        Args:
            v (Iterable[NUM]): Vector to ceil.

        Returns:
            Vector2D
        '''

        def _ceil(v):
            v = tuple(v)

            x = math.ceil(v[0])
            y = math.ceil(v[1])
            return Vector2D(x, y)

        return safe_vector2_op(_ceil, v)

    @classmethod
    def fract(cls, v: Iterable[NUM]) -> 'Vector2D':
        ''' Component-wise extraction of the fractional part of the parameter.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector2D
        '''

        def _fract(v):
            v = tuple(v)

            x = scalar.fract(v[0])
            y = scalar.fract(v[1])
            return Vector2D(x, y)

        return safe_vector2_op(_fract, v)

    @classmethod
    def step(
            cls,
            edge: Union[NUM, Iterable[NUM]],
            v: Iterable[NUM]) -> 'Vector2D':
        ''' Component-wise step.

        For each index i, 0.0 is returned if v[i] < edge[i], and 1.0 is
        returned otherwise.

        Args:
            edge (Union[NUM, Iterable[NUM]]): Edge of the step function.
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector2D
        '''

        def _step(edge, v):
            v = tuple(v)
            edge = cls._force_dim(edge)

            x = scalar.step(edge[0], v[0])
            y = scalar.step(edge[1], v[1])
            return Vector2D(x, y)

        return safe_vector2_op(_step, edge, v)

    @classmethod
    def smoothstep(
            cls,
            edge0: Union[NUM, Iterable[NUM]],
            edge1: Union[NUM, Iterable[NUM]],
            v: Iterable[NUM]) -> 'Vector2D':
        ''' Component-wise hermite interpolation between two values.

        Args:
            edge0 (Union[NUM, Iterable[NUM]]):
                Lower edge of the hermite function.
            edge1 (Union[NUM, Iterable[NUM]]):
                Upper edge of the hermite function.
            v (Iterable[NUM]): Vector to interpolate.

        Returns:
            Vector2D
        '''

        def _smoothstep(edge0, edge1, v):
            v = tuple(v)
            edge0 = cls._force_dim(edge0)
            edge1 = cls._force_dim(edge1)

            x = scalar.smoothstep(edge0[0], edge1[0], v[0])
            y = scalar.smoothstep(edge0[1], edge1[1], v[1])
            return Vector2D(x, y)

        return safe_vector2_op(_smoothstep, edge0, edge1, v)

    @classmethod
    def sqrt(cls, v: Iterable[NUM]) -> 'Vector2D':
        ''' Component-wise square root.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector2D
        '''

        def _sqrt(v):
            v = tuple(v)

            x = math.sqrt(v[0])
            y = math.sqrt(v[1])
            return Vector2D(x, y)

        return safe_vector2_op(_sqrt, v)

    @classmethod
    def inverse_sqrt(cls, v: Iterable[NUM]) -> 'Vector2D':
        ''' Component-wise inverse square root.

        This is equivalent to 1.0 / Vector2D.sqrt(v).

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector2D
        '''

        def _inverse_sqrt(v):
            v = tuple(v)

            x = 1.0 / math.sqrt(v[0])
            y = 1.0 / math.sqrt(v[1])
            return Vector2D(x, y)

        return safe_vector2_op(_inverse_sqrt, v)

    @classmethod
    def pow(cls, v: Iterable[NUM], w: Union[NUM, Iterable[NUM]]) -> 'Vector2D':
        ''' Component-wise power.

        Args:
            v (Iterable[NUM]): Vector to evaluate.
            w (Union[NUM, Iterable[NUM]]): Power to which to raise v.

        Returns:
            Vector2D
        '''

        def _pow(v, w):
            v = tuple(v)
            w = cls._force_dim(w)

            x = v[0] ** w[0]
            y = v[1] ** w[1]
            return Vector2D(x, y)

        return safe_vector2_op(_pow, v, w)

    @classmethod
    def exp(cls, v: Iterable[NUM]) -> 'Vector2D':
        ''' Component-wise natural exponential.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector2D
        '''

        def _exp(v):
            v = tuple(v)

            x = math.exp(v[0])
            y = math.exp(v[1])
            return Vector2D(x, y)

        return safe_vector2_op(_exp, v)

    @classmethod
    def exp2(cls, v: Iterable[NUM]) -> 'Vector2D':
        ''' Component-wise. 2 raised to the power of the parameter.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector2D
        '''

        def _exp2(v):
            v = tuple(v)

            x = 2 ** v[0]
            y = 2 ** v[1]
            return Vector2D(x, y)

        return safe_vector2_op(_exp2, v)

    @classmethod
    def exp10(cls, v: Iterable[NUM]) -> 'Vector2D':
        ''' Component-wise. 10 raised to the power of the parameter.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector2D
        '''

        def _exp10(v):
            v = tuple(v)

            x = 10 ** v[0]
            y = 10 ** v[1]
            return Vector2D(x, y)

        return safe_vector2_op(_exp10, v)

    @classmethod
    def log(cls, v: Iterable[NUM]) -> 'Vector2D':
        ''' Component-wise natural logarithm.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector2D
        '''

        def _log(v):
            v = tuple(v)

            x = math.log(v[0])
            y = math.log(v[1])
            return Vector2D(x, y)

        return safe_vector2_op(_log, v)

    @classmethod
    def log2(cls, v: Iterable[NUM]) -> 'Vector2D':
        ''' Component-wise base-2 logarithm.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector2D
        '''

        def _log2(v):
            v = tuple(v)

            x = math.log2(v[0])
            y = math.log2(v[1])
            return Vector2D(x, y)

        return safe_vector2_op(_log2, v)

    @classmethod
    def log10(cls, v: Iterable[NUM]) -> 'Vector2D':
        ''' Component-wise base-10 logarithm.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector2D
        '''

        def _log10(v):
            v = tuple(v)

            x = math.log10(v[0])
            y = math.log10(v[1])
            return Vector2D(x, y)

        return safe_vector2_op(_log10, v)

    @classmethod
    def radians(cls, v: Iterable[NUM]) -> 'Vector2D':
        ''' Component-wise conversion from degrees to radians.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector2D
        '''

        def _radians(v):
            v = tuple(v)

            x = math.radians(v[0])
            y = math.radians(v[1])
            return Vector2D(x, y)

        return safe_vector2_op(_radians, v)

    @classmethod
    def degrees(cls, v: Iterable[NUM]) -> 'Vector2D':
        ''' Component-wise conversion from radians to degrees.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector2D
        '''

        def _degrees(v):
            v = tuple(v)

            x = math.degrees(v[0])
            y = math.degrees(v[1])
            return Vector2D(x, y)

        return safe_vector2_op(_degrees, v)

    @classmethod
    def sin(cls, v: Iterable[NUM]) -> 'Vector2D':
        ''' Component-wise sine.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector2D
        '''

        def _sin(v):
            v = tuple(v)

            x = math.sin(v[0])
            y = math.sin(v[1])
            return Vector2D(x, y)

        return safe_vector2_op(_sin, v)

    @classmethod
    def cos(cls, v: Iterable[NUM]) -> 'Vector2D':
        ''' Component-wise cosine.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector2D
        '''

        def _cos(v):
            v = tuple(v)

            x = math.cos(v[0])
            y = math.cos(v[1])
            return Vector2D(x, y)

        return safe_vector2_op(_cos, v)

    @classmethod
    def tan(cls, v: Iterable[NUM]) -> 'Vector2D':
        ''' Component-wise tangent.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector2D
        '''

        def _tan(v):
            v = tuple(v)

            x = math.tan(v[0])
            y = math.tan(v[1])
            return Vector2D(x, y)

        return safe_vector2_op(_tan, v)

    @classmethod
    def sinh(cls, v: Iterable[NUM]) -> 'Vector2D':
        ''' Component-wise hyperbolic sine.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector2D
        '''

        def _sinh(v):
            v = tuple(v)

            x = math.sinh(v[0])
            y = math.sinh(v[1])
            return Vector2D(x, y)

        return safe_vector2_op(_sinh, v)

    @classmethod
    def cosh(cls, v: Iterable[NUM]) -> 'Vector2D':
        ''' Component-wise hyperbolic cosine.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector2D
        '''

        def _cosh(v):
            v = tuple(v)

            x = math.cosh(v[0])
            y = math.cosh(v[1])
            return Vector2D(x, y)

        return safe_vector2_op(_cosh, v)

    @classmethod
    def tanh(cls, v: Iterable[NUM]) -> 'Vector2D':
        ''' Component-wise hyperbolic tangent.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector2D
        '''

        def _tanh(v):
            v = tuple(v)

            x = math.tanh(v[0])
            y = math.tanh(v[1])
            return Vector2D(x, y)

        return safe_vector2_op(_tanh, v)

    @classmethod
    def asin(cls, v: Iterable[NUM]) -> 'Vector2D':
        ''' Component-wise arc-sine.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector2D
        '''

        def _asin(v):
            v = tuple(v)

            x = math.asin(v[0])
            y = math.asin(v[1])
            return Vector2D(x, y)

        return safe_vector2_op(_asin, v)

    @classmethod
    def acos(cls, v: Iterable[NUM]) -> 'Vector2D':
        ''' Component-wise arc-cosine.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector2D
        '''

        def _acos(v):
            v = tuple(v)

            x = math.acos(v[0])
            y = math.acos(v[1])
            return Vector2D(x, y)

        return safe_vector2_op(_acos, v)

    @classmethod
    def atan(cls, v: Iterable[NUM]) -> 'Vector2D':
        ''' Component-wise arc-tangent.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector2D
        '''

        def _atan(v):
            v = tuple(v)

            x = math.atan(v[0])
            y = math.atan(v[1])
            return Vector2D(x, y)

        return safe_vector2_op(_atan, v)

    @classmethod
    def atan2(
            cls, v: Iterable[NUM], w: Union[NUM, Iterable[NUM]]) -> 'Vector2D':
        ''' Component-wise arc-tangent with separable numerator
        and denominator.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector2D
        '''

        def _atan2(v, w):
            v = tuple(v)
            w = cls._force_dim(w)

            x = math.atan2(v[0], w[0])
            y = math.atan2(v[1], w[1])
            return Vector2D(x, y)

        return safe_vector2_op(_atan2, v, w)

    @classmethod
    def asinh(cls, v: Iterable[NUM]) -> 'Vector2D':
        ''' Component-wise hyperbolic arc-sine.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector2D
        '''

        def _asinh(v):
            v = tuple(v)

            x = math.asinh(v[0])
            y = math.asinh(v[1])
            return Vector2D(x, y)

        return safe_vector2_op(_asinh, v)

    @classmethod
    def acosh(cls, v: Iterable[NUM]) -> 'Vector2D':
        ''' Component-wise hyperbolic arc-cosine.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector2D
        '''

        def _acosh(v):
            v = tuple(v)

            x = math.acosh(v[0])
            y = math.acosh(v[1])
            return Vector2D(x, y)

        return safe_vector2_op(_acosh, v)

    @classmethod
    def atanh(cls, v: Iterable[NUM]) -> 'Vector2D':
        ''' Component-wise hyperbolic arc-tangent.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector2D
        '''

        def _atanh(v):
            v = tuple(v)

            x = math.atanh(v[0])
            y = math.atanh(v[1])
            return Vector2D(x, y)

        return safe_vector2_op(_atanh, v)

    @classmethod
    def _dot(cls, v0: 'Vector2D', v1: 'Vector2D') -> float:
        return v0[0] * v1[0] + v0[1] * v1[1]

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

        return safe_vector2_op(_d, v0, v1)

    @classmethod
    def _length(cls, v: 'Vector2D') -> float:
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
    def normalize(cls, v: Iterable[NUM]) -> 'Vector2D':
        ''' Vector normalization.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector2D
        '''

        v = cls._make_vec(v)

        return v / cls._length(v)

    @classmethod
    def face_forward(
            cls,
            v: Iterable[NUM],
            i: Iterable[NUM],
            vref: Iterable[NUM]) -> 'Vector2D':
        ''' Return a vector pointing in the same direction as another.

        If dot(vref, i) < 0.0, returns v. Otherwise returns -v.

        Args:
            v (Iterable[NUM]): Vector to orient.
            i (Iterable[NUM]): Incident vector.
            vref (Iterable[NUM]): Reference vector.

        Returns:
            Vector2D
        '''

        v = cls._make_vec(v)
        i = cls._make_vec(i)
        vref = cls._make_vec(vref)

        return v if cls._dot(vref, i) < 0.0 else -v

    @classmethod
    def reflect(cls, i: Iterable[NUM], n: Iterable[NUM]) -> 'Vector2D':
        ''' Reflection direction of an incident vector.

        Note:
            n should be normalized.

        Args:
            i (Iterable[NUM]): Incident vector.
            n (Iterable[NUM]): Normal vector.

        Returns:
            Vector2D
        '''

        i = cls._make_vec(i)
        n = cls._make_vec(n)

        return i - 2.0 * cls._dot(n, i) * n

    @classmethod
    def refract(
            cls, i: Iterable[NUM], n: Iterable[NUM], r: float) -> 'Vector2D':
        ''' Refraction direction of an incident vector.

        Note:
            i and n should be normalized.

        Args:
            i (Iterable[NUM]): Incident vector.
            n (Iterable[NUM]): Normal vector.
            r (float): Ratio of indices of refraction.

        Returns:
            Vector2D
        '''

        i = cls._make_vec(i)
        n = cls._make_vec(n)

        ndoti = cls._dot(n, i)
        d = 1.0 - r * r * (1.0 - ndoti * ndoti)

        # Total internal reflection
        if d < 0.0:
            return 0.0

        return r * i - (r * ndoti + math.sqrt(d)) * n
