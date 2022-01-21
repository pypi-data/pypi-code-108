'''vector_4d.py'''


import math
from typing import Tuple, Union, Iterable, Any

from mastapy._math import scalar
from mastapy._math.vector_base import (
    VectorException, NUM, ERROR_SET_MESSAGE,
    ERROR_SET_PROPERTY, _safe_vector_op)
from mastapy._math.vector_2d import Vector2D
from mastapy._math.vector_3d import Vector3D


__all__ = ('Vector4D',)


ERROR_4D_MESSAGE = 'Input vectors must be 4D for Vector4D calculations.'
safe_vector4_op = _safe_vector_op(ERROR_4D_MESSAGE)


class Vector4D(Vector3D):
    '''Create a Vector4D from X, Y, Z and W components

    Args:
        x: NUM
        y: NUM
        z: NUM
        w: NUM

    Returns:
        Vector4D
    '''

    def __init__(self, x: NUM, y: NUM, z: NUM, w: NUM) -> 'Vector4D':
        self.wrapped = None
        super(Vector2D, self).__init__(
            [float(x), float(y), float(z), float(w)])

    @classmethod
    def broadcast(cls, value: NUM) -> 'Vector4D':
        ''' Create a Vector4D by broadcasting a value to all of its dimensions

        Args:
            value: NUM

        Returns:
            Vector4D
        '''

        return cls(value, value, value, value)

    @classmethod
    def from_iterable(cls, t: Iterable[NUM]) -> 'Vector4D':
        ''' Create a Vector4D from an Iterable

        Args:
            t: Iterable[NUM]

        Returns:
            Vector4D
        '''

        t = tuple(t)

        try:
            return cls(t[0], t[1], t[2], t[3])
        except (KeyError, TypeError, AttributeError):
            raise VectorException(
                'Tuple must be of at least length 4.') from None

    @property
    def w(self) -> float:
        ''' Get the W component of the vector

        Returns:
            float
        '''

        return self[3]

    @w.setter
    def w(self, value: NUM):
        self[3] = float(value)
        if self.wrapped:
            raise VectorException(ERROR_SET_PROPERTY) from None

    @property
    def xw(self) -> Vector2D:
        ''' Get the XW components of the vector

        Returns:
            Vector2D
        '''

        return Vector2D(self.x, self.w)

    @xw.setter
    def xw(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 2)
                self.x = values[0]
                self.w = values[1]
            else:
                self.x = self.w = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def yw(self) -> Vector2D:
        ''' Get the YW components of the vector

        Returns:
            Vector2D
        '''

        return Vector2D(self.y, self.w)

    @yw.setter
    def yw(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 2)
                self.y = values[0]
                self.w = values[1]
            else:
                self.y = self.w = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def zw(self) -> Vector2D:
        ''' Get the ZW components of the vector

        Returns:
            Vector2D
        '''

        return Vector2D(self.z, self.w)

    @zw.setter
    def zw(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 2)
                self.z = values[0]
                self.w = values[1]
            else:
                self.z = self.w = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def wx(self) -> Vector2D:
        ''' Get the WX components of the vector

        Returns:
            Vector2D
        '''

        return Vector2D(self.w, self.x)

    @wx.setter
    def wx(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 2)
                self.w = values[0]
                self.x = values[1]
            else:
                self.w = self.x = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def wy(self) -> Vector2D:
        ''' Get the WY components of the vector

        Returns:
            Vector2D
        '''

        return Vector2D(self.w, self.y)

    @wy.setter
    def wy(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 2)
                self.w = values[0]
                self.y = values[1]
            else:
                self.w = self.y = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def wz(self) -> Vector2D:
        ''' Get the WZ components of the vector

        Returns:
            Vector2D
        '''

        return Vector2D(self.w, self.z)

    @wz.setter
    def wz(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 2)
                self.w = values[0]
                self.z = values[1]
            else:
                self.w = self.z = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def ww(self) -> Vector2D:
        ''' Get the WW components of the vector

        Returns:
            Vector2D
        '''

        return Vector2D(self.w, self.w)

    @property
    def xxw(self) -> Vector3D:
        ''' Get the XXW components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.x, self.x, self.w)

    @property
    def xyw(self) -> Vector3D:
        ''' Get the XYW components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.x, self.y, self.w)

    @xyw.setter
    def xyw(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 3)
                self.x = values[0]
                self.y = values[1]
                self.w = values[2]
            else:
                self.x = self.y = self.w = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def xzw(self) -> Vector3D:
        ''' Get the XZW components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.x, self.z, self.w)

    @xzw.setter
    def xzw(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 3)
                self.x = values[0]
                self.z = values[1]
                self.w = values[2]
            else:
                self.x = self.z = self.w = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def xwx(self) -> Vector3D:
        ''' Get the XWX components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.x, self.w, self.x)

    @property
    def xwy(self) -> Vector3D:
        ''' Get the XWY components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.x, self.w, self.y)

    @xwy.setter
    def xwy(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 3)
                self.x = values[0]
                self.w = values[1]
                self.y = values[2]
            else:
                self.x = self.w = self.y = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def xwz(self) -> Vector3D:
        ''' Get the XWZ components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.x, self.w, self.z)

    @xwz.setter
    def xwz(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 3)
                self.x = values[0]
                self.w = values[1]
                self.z = values[2]
            else:
                self.x = self.w = self.z = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def xww(self) -> Vector3D:
        ''' Get the XWW components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.x, self.w, self.w)

    @property
    def yxw(self) -> Vector3D:
        ''' Get the YXW components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.y, self.x, self.w)

    @yxw.setter
    def yxw(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 3)
                self.y = values[0]
                self.x = values[1]
                self.w = values[2]
            else:
                self.y = self.x = self.w = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def yyw(self) -> Vector3D:
        ''' Get the YYW components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.y, self.y, self.w)

    @property
    def yzw(self) -> Vector3D:
        ''' Get the YZW components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.y, self.z, self.w)

    @yzw.setter
    def yzw(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 3)
                self.y = values[0]
                self.z = values[1]
                self.w = values[2]
            else:
                self.y = self.z = self.w = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def ywx(self) -> Vector3D:
        ''' Get the YWX components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.y, self.w, self.x)

    @ywx.setter
    def ywx(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 3)
                self.y = values[0]
                self.w = values[1]
                self.x = values[2]
            else:
                self.y = self.w = self.x = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def ywy(self) -> Vector3D:
        ''' Get the YWY components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.y, self.w, self.y)

    @property
    def ywz(self) -> Vector3D:
        ''' Get the YWZ components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.y, self.w, self.z)

    @ywz.setter
    def ywz(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 3)
                self.y = values[0]
                self.w = values[1]
                self.z = values[2]
            else:
                self.y = self.w = self.z = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def yww(self) -> Vector3D:
        ''' Get the YWW components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.y, self.w, self.w)

    @property
    def zxw(self) -> Vector3D:
        ''' Get the ZXW components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.z, self.x, self.w)

    @zxw.setter
    def zxw(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 3)
                self.z = values[0]
                self.x = values[1]
                self.w = values[2]
            else:
                self.z = self.x = self.w = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def zyw(self) -> Vector3D:
        ''' Get the ZYW components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.z, self.y, self.w)

    @zyw.setter
    def zyw(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 3)
                self.z = values[0]
                self.y = values[1]
                self.w = values[2]
            else:
                self.z = self.y = self.w = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def zzw(self) -> Vector3D:
        ''' Get the ZZW components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.z, self.z, self.w)

    @property
    def zwx(self) -> Vector3D:
        ''' Get the ZWX components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.z, self.w, self.x)

    @zwx.setter
    def zwx(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 3)
                self.z = values[0]
                self.w = values[1]
                self.x = values[2]
            else:
                self.z = self.w = self.x = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def zwy(self) -> Vector3D:
        ''' Get the ZWY components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.z, self.w, self.y)

    @zwy.setter
    def zwy(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 3)
                self.z = values[0]
                self.w = values[1]
                self.y = values[2]
            else:
                self.z = self.w = self.y = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def zwz(self) -> Vector3D:
        ''' Get the ZWZ components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.z, self.w, self.z)

    @property
    def zww(self) -> Vector3D:
        ''' Get the ZWW components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.z, self.w, self.w)

    @property
    def wxx(self) -> Vector3D:
        ''' Get the WXX components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.w, self.x, self.x)

    @property
    def wxy(self) -> Vector3D:
        ''' Get the WXY components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.w, self.x, self.y)

    @wxy.setter
    def wxy(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 3)
                self.w = values[0]
                self.x = values[1]
                self.y = values[2]
            else:
                self.w = self.x = self.y = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def wxz(self) -> Vector3D:
        ''' Get the WXZ components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.w, self.x, self.z)

    @wxz.setter
    def wxz(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 3)
                self.w = values[0]
                self.x = values[1]
                self.z = values[2]
            else:
                self.w = self.x = self.z = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def wxw(self) -> Vector3D:
        ''' Get the WXW components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.w, self.x, self.w)

    @property
    def wyx(self) -> Vector3D:
        ''' Get the WYX components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.w, self.y, self.x)

    @wyx.setter
    def wyx(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 3)
                self.w = values[0]
                self.y = values[1]
                self.x = values[2]
            else:
                self.w = self.y = self.x = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def wyy(self) -> Vector3D:
        ''' Get the WYY components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.w, self.y, self.y)

    @property
    def wyz(self) -> Vector3D:
        ''' Get the WYZ components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.w, self.y, self.z)

    @wyz.setter
    def wyz(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 3)
                self.w = values[0]
                self.y = values[1]
                self.z = values[2]
            else:
                self.w = self.y = self.z = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def wyw(self) -> Vector3D:
        ''' Get the WYW components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.w, self.y, self.w)

    @property
    def wzx(self) -> Vector3D:
        ''' Get the WZX components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.w, self.z, self.x)

    @wzx.setter
    def wzx(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 3)
                self.w = values[0]
                self.z = values[1]
                self.x = values[2]
            else:
                self.w = self.z = self.x = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def wzy(self) -> Vector3D:
        ''' Get the WZY components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.w, self.z, self.y)

    @wzy.setter
    def wzy(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 3)
                self.w = values[0]
                self.z = values[1]
                self.y = values[2]
            else:
                self.w = self.z = self.y = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def wzz(self) -> Vector3D:
        ''' Get the WZZ components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.w, self.z, self.z)

    @property
    def wzw(self) -> Vector3D:
        ''' Get the WZW components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.w, self.z, self.w)

    @property
    def wwx(self) -> Vector3D:
        ''' Get the WWX components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.w, self.w, self.x)

    @property
    def wwy(self) -> Vector3D:
        ''' Get the WWY components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.w, self.w, self.y)

    @property
    def wwz(self) -> Vector3D:
        ''' Get the WWZ components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.w, self.w, self.z)

    @property
    def www(self) -> Vector3D:
        ''' Get the WWW components of the vector

        Returns:
            Vector3D
        '''

        return Vector3D(self.w, self.w, self.w)

    @property
    def xxxx(self) -> 'Vector4D':
        ''' Get the XXXX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.x, self.x, self.x)

    @property
    def xxxy(self) -> 'Vector4D':
        ''' Get the XXXY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.x, self.x, self.y)

    @property
    def xxxz(self) -> 'Vector4D':
        ''' Get the XXXZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.x, self.x, self.z)

    @property
    def xxxw(self) -> 'Vector4D':
        ''' Get the XXXW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.x, self.x, self.w)

    @property
    def xxyx(self) -> 'Vector4D':
        ''' Get the XXYX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.x, self.y, self.x)

    @property
    def xxyy(self) -> 'Vector4D':
        ''' Get the XXYY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.x, self.y, self.y)

    @property
    def xxyz(self) -> 'Vector4D':
        ''' Get the XXYZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.x, self.y, self.z)

    @property
    def xxyw(self) -> 'Vector4D':
        ''' Get the XXYW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.x, self.y, self.w)

    @property
    def xxzx(self) -> 'Vector4D':
        ''' Get the XXZX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.x, self.z, self.x)

    @property
    def xxzy(self) -> 'Vector4D':
        ''' Get the XXZY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.x, self.z, self.y)

    @property
    def xxzz(self) -> 'Vector4D':
        ''' Get the XXZZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.x, self.z, self.z)

    @property
    def xxzw(self) -> 'Vector4D':
        ''' Get the XXZW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.x, self.z, self.w)

    @property
    def xxwx(self) -> 'Vector4D':
        ''' Get the XXWX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.x, self.w, self.x)

    @property
    def xxwy(self) -> 'Vector4D':
        ''' Get the XXWY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.x, self.w, self.y)

    @property
    def xxwz(self) -> 'Vector4D':
        ''' Get the XXWZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.x, self.w, self.z)

    @property
    def xxww(self) -> 'Vector4D':
        ''' Get the XXWW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.x, self.w, self.w)

    @property
    def xyxx(self) -> 'Vector4D':
        ''' Get the XYXX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.y, self.x, self.x)

    @property
    def xyxy(self) -> 'Vector4D':
        ''' Get the XYXY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.y, self.x, self.y)

    @property
    def xyxz(self) -> 'Vector4D':
        ''' Get the XYXZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.y, self.x, self.z)

    @property
    def xyxw(self) -> 'Vector4D':
        ''' Get the XYXW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.y, self.x, self.w)

    @property
    def xyyx(self) -> 'Vector4D':
        ''' Get the XYYX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.y, self.y, self.x)

    @property
    def xyyy(self) -> 'Vector4D':
        ''' Get the XYYY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.y, self.y, self.y)

    @property
    def xyyz(self) -> 'Vector4D':
        ''' Get the XYYZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.y, self.y, self.z)

    @property
    def xyyw(self) -> 'Vector4D':
        ''' Get the XYYW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.y, self.y, self.w)

    @property
    def xyzx(self) -> 'Vector4D':
        ''' Get the XYZX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.y, self.z, self.x)

    @property
    def xyzy(self) -> 'Vector4D':
        ''' Get the XYZY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.y, self.z, self.y)

    @property
    def xyzz(self) -> 'Vector4D':
        ''' Get the XYZZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.y, self.z, self.z)

    @property
    def xyzw(self) -> 'Vector4D':
        ''' Get the XYZW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.y, self.z, self.w)

    @xyzw.setter
    def xyzw(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 4)
                self.x = values[0]
                self.y = values[1]
                self.z = values[2]
                self.w = values[3]
            else:
                self.x = self.y = self.z = self.w = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def xywx(self) -> 'Vector4D':
        ''' Get the XYWX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.y, self.w, self.x)

    @property
    def xywy(self) -> 'Vector4D':
        ''' Get the XYWY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.y, self.w, self.y)

    @property
    def xywz(self) -> 'Vector4D':
        ''' Get the XYWZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.y, self.w, self.z)

    @xywz.setter
    def xywz(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 4)
                self.x = values[0]
                self.y = values[1]
                self.w = values[2]
                self.z = values[3]
            else:
                self.x = self.y = self.w = self.z = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def xyww(self) -> 'Vector4D':
        ''' Get the XYWW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.y, self.w, self.w)

    @property
    def xzxx(self) -> 'Vector4D':
        ''' Get the XZXX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.z, self.x, self.x)

    @property
    def xzxy(self) -> 'Vector4D':
        ''' Get the XZXY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.z, self.x, self.y)

    @property
    def xzxz(self) -> 'Vector4D':
        ''' Get the XZXZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.z, self.x, self.z)

    @property
    def xzxw(self) -> 'Vector4D':
        ''' Get the XZXW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.z, self.x, self.w)

    @property
    def xzyx(self) -> 'Vector4D':
        ''' Get the XZYX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.z, self.y, self.x)

    @property
    def xzyy(self) -> 'Vector4D':
        ''' Get the XZYY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.z, self.y, self.y)

    @property
    def xzyz(self) -> 'Vector4D':
        ''' Get the XZYZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.z, self.y, self.z)

    @property
    def xzyw(self) -> 'Vector4D':
        ''' Get the XZYW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.z, self.y, self.w)

    @xzyw.setter
    def xzyw(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 4)
                self.x = values[0]
                self.z = values[1]
                self.y = values[2]
                self.w = values[3]
            else:
                self.x = self.z = self.y = self.w = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def xzzx(self) -> 'Vector4D':
        ''' Get the XZZX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.z, self.z, self.x)

    @property
    def xzzy(self) -> 'Vector4D':
        ''' Get the XZZY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.z, self.z, self.y)

    @property
    def xzzz(self) -> 'Vector4D':
        ''' Get the XZZZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.z, self.z, self.z)

    @property
    def xzzw(self) -> 'Vector4D':
        ''' Get the XZZW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.z, self.z, self.w)

    @property
    def xzwx(self) -> 'Vector4D':
        ''' Get the XZWX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.z, self.w, self.x)

    @property
    def xzwy(self) -> 'Vector4D':
        ''' Get the XZWY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.z, self.w, self.y)

    @xzwy.setter
    def xzwy(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 4)
                self.x = values[0]
                self.z = values[1]
                self.w = values[2]
                self.y = values[3]
            else:
                self.x = self.z = self.w = self.y = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def xzwz(self) -> 'Vector4D':
        ''' Get the XZWZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.z, self.w, self.z)

    @property
    def xzww(self) -> 'Vector4D':
        ''' Get the XZWW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.z, self.w, self.w)

    @property
    def xwxx(self) -> 'Vector4D':
        ''' Get the XWXX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.w, self.x, self.x)

    @property
    def xwxy(self) -> 'Vector4D':
        ''' Get the XWXY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.w, self.x, self.y)

    @property
    def xwxz(self) -> 'Vector4D':
        ''' Get the XWXZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.w, self.x, self.z)

    @property
    def xwxw(self) -> 'Vector4D':
        ''' Get the XWXW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.w, self.x, self.w)

    @property
    def xwyx(self) -> 'Vector4D':
        ''' Get the XWYX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.w, self.y, self.x)

    @property
    def xwyy(self) -> 'Vector4D':
        ''' Get the XWYY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.w, self.y, self.y)

    @property
    def xwyz(self) -> 'Vector4D':
        ''' Get the XWYZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.w, self.y, self.z)

    @xwyz.setter
    def xwyz(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 4)
                self.x = values[0]
                self.w = values[1]
                self.y = values[2]
                self.z = values[3]
            else:
                self.x = self.w = self.y = self.z = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def xwyw(self) -> 'Vector4D':
        ''' Get the XWYW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.w, self.y, self.w)

    @property
    def xwzx(self) -> 'Vector4D':
        ''' Get the XWZX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.w, self.z, self.x)

    @property
    def xwzy(self) -> 'Vector4D':
        ''' Get the XWZY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.w, self.z, self.y)

    @xwzy.setter
    def xwzy(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 4)
                self.x = values[0]
                self.w = values[1]
                self.z = values[2]
                self.y = values[3]
            else:
                self.x = self.w = self.z = self.y = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def xwzz(self) -> 'Vector4D':
        ''' Get the XWZZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.w, self.z, self.z)

    @property
    def xwzw(self) -> 'Vector4D':
        ''' Get the XWZW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.w, self.z, self.w)

    @property
    def xwwx(self) -> 'Vector4D':
        ''' Get the XWWX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.w, self.w, self.x)

    @property
    def xwwy(self) -> 'Vector4D':
        ''' Get the XWWY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.w, self.w, self.y)

    @property
    def xwwz(self) -> 'Vector4D':
        ''' Get the XWWZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.w, self.w, self.z)

    @property
    def xwww(self) -> 'Vector4D':
        ''' Get the XWWW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.x, self.w, self.w, self.w)

    @property
    def yxxx(self) -> 'Vector4D':
        ''' Get the YXXX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.x, self.x, self.x)

    @property
    def yxxy(self) -> 'Vector4D':
        ''' Get the YXXY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.x, self.x, self.y)

    @property
    def yxxz(self) -> 'Vector4D':
        ''' Get the YXXZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.x, self.x, self.z)

    @property
    def yxxw(self) -> 'Vector4D':
        ''' Get the YXXW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.x, self.x, self.w)

    @property
    def yxyx(self) -> 'Vector4D':
        ''' Get the YXYX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.x, self.y, self.x)

    @property
    def yxyy(self) -> 'Vector4D':
        ''' Get the YXYY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.x, self.y, self.y)

    @property
    def yxyz(self) -> 'Vector4D':
        ''' Get the YXYZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.x, self.y, self.z)

    @property
    def yxyw(self) -> 'Vector4D':
        ''' Get the YXYW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.x, self.y, self.w)

    @property
    def yxzx(self) -> 'Vector4D':
        ''' Get the YXZX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.x, self.z, self.x)

    @property
    def yxzy(self) -> 'Vector4D':
        ''' Get the YXZY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.x, self.z, self.y)

    @property
    def yxzz(self) -> 'Vector4D':
        ''' Get the YXZZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.x, self.z, self.z)

    @property
    def yxzw(self) -> 'Vector4D':
        ''' Get the YXZW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.x, self.z, self.w)

    @yxzw.setter
    def yxzw(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 4)
                self.y = values[0]
                self.x = values[1]
                self.z = values[2]
                self.w = values[3]
            else:
                self.y = self.x = self.z = self.w = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def yxwx(self) -> 'Vector4D':
        ''' Get the YXWX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.x, self.w, self.x)

    @property
    def yxwy(self) -> 'Vector4D':
        ''' Get the YXWY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.x, self.w, self.y)

    @property
    def yxwz(self) -> 'Vector4D':
        ''' Get the YXWZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.x, self.w, self.z)

    @yxwz.setter
    def yxwz(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 4)
                self.y = values[0]
                self.x = values[1]
                self.w = values[2]
                self.z = values[3]
            else:
                self.y = self.x = self.w = self.z = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def yxww(self) -> 'Vector4D':
        ''' Get the YXWW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.x, self.w, self.w)

    @property
    def yyxx(self) -> 'Vector4D':
        ''' Get the YYXX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.y, self.x, self.x)

    @property
    def yyxy(self) -> 'Vector4D':
        ''' Get the YYXY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.y, self.x, self.y)

    @property
    def yyxz(self) -> 'Vector4D':
        ''' Get the YYXZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.y, self.x, self.z)

    @property
    def yyxw(self) -> 'Vector4D':
        ''' Get the YYXW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.y, self.x, self.w)

    @property
    def yyyx(self) -> 'Vector4D':
        ''' Get the YYYX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.y, self.y, self.x)

    @property
    def yyyy(self) -> 'Vector4D':
        ''' Get the YYYY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.y, self.y, self.y)

    @property
    def yyyz(self) -> 'Vector4D':
        ''' Get the YYYZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.y, self.y, self.z)

    @property
    def yyyw(self) -> 'Vector4D':
        ''' Get the YYYW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.y, self.y, self.w)

    @property
    def yyzx(self) -> 'Vector4D':
        ''' Get the YYZX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.y, self.z, self.x)

    @property
    def yyzy(self) -> 'Vector4D':
        ''' Get the YYZY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.y, self.z, self.y)

    @property
    def yyzz(self) -> 'Vector4D':
        ''' Get the YYZZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.y, self.z, self.z)

    @property
    def yyzw(self) -> 'Vector4D':
        ''' Get the YYZW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.y, self.z, self.w)

    @property
    def yywx(self) -> 'Vector4D':
        ''' Get the YYWX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.y, self.w, self.x)

    @property
    def yywy(self) -> 'Vector4D':
        ''' Get the YYWY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.y, self.w, self.y)

    @property
    def yywz(self) -> 'Vector4D':
        ''' Get the YYWZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.y, self.w, self.z)

    @property
    def yyww(self) -> 'Vector4D':
        ''' Get the YYWW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.y, self.w, self.w)

    @property
    def yzxx(self) -> 'Vector4D':
        ''' Get the YZXX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.z, self.x, self.x)

    @property
    def yzxy(self) -> 'Vector4D':
        ''' Get the YZXY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.z, self.x, self.y)

    @property
    def yzxz(self) -> 'Vector4D':
        ''' Get the YZXZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.z, self.x, self.z)

    @property
    def yzxw(self) -> 'Vector4D':
        ''' Get the YZXW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.z, self.x, self.w)

    @yzxw.setter
    def yzxw(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 4)
                self.y = values[0]
                self.z = values[1]
                self.x = values[2]
                self.w = values[3]
            else:
                self.y = self.z = self.x = self.w = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def yzyx(self) -> 'Vector4D':
        ''' Get the YZYX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.z, self.y, self.x)

    @property
    def yzyy(self) -> 'Vector4D':
        ''' Get the YZYY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.z, self.y, self.y)

    @property
    def yzyz(self) -> 'Vector4D':
        ''' Get the YZYZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.z, self.y, self.z)

    @property
    def yzyw(self) -> 'Vector4D':
        ''' Get the YZYW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.z, self.y, self.w)

    @property
    def yzzx(self) -> 'Vector4D':
        ''' Get the YZZX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.z, self.z, self.x)

    @property
    def yzzy(self) -> 'Vector4D':
        ''' Get the YZZY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.z, self.z, self.y)

    @property
    def yzzz(self) -> 'Vector4D':
        ''' Get the YZZZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.z, self.z, self.z)

    @property
    def yzzw(self) -> 'Vector4D':
        ''' Get the YZZW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.z, self.z, self.w)

    @property
    def yzwx(self) -> 'Vector4D':
        ''' Get the YZWX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.z, self.w, self.x)

    @yzwx.setter
    def yzwx(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 4)
                self.y = values[0]
                self.z = values[1]
                self.w = values[2]
                self.x = values[3]
            else:
                self.y = self.z = self.w = self.x = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def yzwy(self) -> 'Vector4D':
        ''' Get the YZWY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.z, self.w, self.y)

    @property
    def yzwz(self) -> 'Vector4D':
        ''' Get the YZWZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.z, self.w, self.z)

    @property
    def yzww(self) -> 'Vector4D':
        ''' Get the YZWW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.z, self.w, self.w)

    @property
    def ywxx(self) -> 'Vector4D':
        ''' Get the YWXX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.w, self.x, self.x)

    @property
    def ywxy(self) -> 'Vector4D':
        ''' Get the YWXY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.w, self.x, self.y)

    @property
    def ywxz(self) -> 'Vector4D':
        ''' Get the YWXZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.w, self.x, self.z)

    @ywxz.setter
    def ywxz(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 4)
                self.y = values[0]
                self.w = values[1]
                self.x = values[2]
                self.z = values[3]
            else:
                self.y = self.w = self.x = self.z = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def ywxw(self) -> 'Vector4D':
        ''' Get the YWXW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.w, self.x, self.w)

    @property
    def ywyx(self) -> 'Vector4D':
        ''' Get the YWYX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.w, self.y, self.x)

    @property
    def ywyy(self) -> 'Vector4D':
        ''' Get the YWYY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.w, self.y, self.y)

    @property
    def ywyz(self) -> 'Vector4D':
        ''' Get the YWYZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.w, self.y, self.z)

    @property
    def ywyw(self) -> 'Vector4D':
        ''' Get the YWYW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.w, self.y, self.w)

    @property
    def ywzx(self) -> 'Vector4D':
        ''' Get the YWZX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.w, self.z, self.x)

    @ywzx.setter
    def ywzx(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 4)
                self.y = values[0]
                self.w = values[1]
                self.z = values[2]
                self.x = values[3]
            else:
                self.y = self.w = self.z = self.x = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def ywzy(self) -> 'Vector4D':
        ''' Get the YWZY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.w, self.z, self.y)

    @property
    def ywzz(self) -> 'Vector4D':
        ''' Get the YWZZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.w, self.z, self.z)

    @property
    def ywzw(self) -> 'Vector4D':
        ''' Get the YWZW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.w, self.z, self.w)

    @property
    def ywwx(self) -> 'Vector4D':
        ''' Get the YWWX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.w, self.w, self.x)

    @property
    def ywwy(self) -> 'Vector4D':
        ''' Get the YWWY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.w, self.w, self.y)

    @property
    def ywwz(self) -> 'Vector4D':
        ''' Get the YWWZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.w, self.w, self.z)

    @property
    def ywww(self) -> 'Vector4D':
        ''' Get the YWWW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.y, self.w, self.w, self.w)

    @property
    def zxxx(self) -> 'Vector4D':
        ''' Get the ZXXX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.x, self.x, self.x)

    @property
    def zxxy(self) -> 'Vector4D':
        ''' Get the ZXXY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.x, self.x, self.y)

    @property
    def zxxz(self) -> 'Vector4D':
        ''' Get the ZXXZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.x, self.x, self.z)

    @property
    def zxxw(self) -> 'Vector4D':
        ''' Get the ZXXW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.x, self.x, self.w)

    @property
    def zxyx(self) -> 'Vector4D':
        ''' Get the ZXYX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.x, self.y, self.x)

    @property
    def zxyy(self) -> 'Vector4D':
        ''' Get the ZXYY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.x, self.y, self.y)

    @property
    def zxyz(self) -> 'Vector4D':
        ''' Get the ZXYZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.x, self.y, self.z)

    @property
    def zxyw(self) -> 'Vector4D':
        ''' Get the ZXYW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.x, self.y, self.w)

    @zxyw.setter
    def zxyw(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 4)
                self.z = values[0]
                self.x = values[1]
                self.y = values[2]
                self.w = values[3]
            else:
                self.z = self.x = self.y = self.w = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def zxzx(self) -> 'Vector4D':
        ''' Get the ZXZX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.x, self.z, self.x)

    @property
    def zxzy(self) -> 'Vector4D':
        ''' Get the ZXZY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.x, self.z, self.y)

    @property
    def zxzz(self) -> 'Vector4D':
        ''' Get the ZXZZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.x, self.z, self.z)

    @property
    def zxzw(self) -> 'Vector4D':
        ''' Get the ZXZW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.x, self.z, self.w)

    @property
    def zxwx(self) -> 'Vector4D':
        ''' Get the ZXWX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.x, self.w, self.x)

    @property
    def zxwy(self) -> 'Vector4D':
        ''' Get the ZXWY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.x, self.w, self.y)

    @zxwy.setter
    def zxwy(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 4)
                self.z = values[0]
                self.x = values[1]
                self.w = values[2]
                self.y = values[3]
            else:
                self.z = self.x = self.w = self.y = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def zxwz(self) -> 'Vector4D':
        ''' Get the ZXWZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.x, self.w, self.z)

    @property
    def zxww(self) -> 'Vector4D':
        ''' Get the ZXWW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.x, self.w, self.w)

    @property
    def zyxx(self) -> 'Vector4D':
        ''' Get the ZYXX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.y, self.x, self.x)

    @property
    def zyxy(self) -> 'Vector4D':
        ''' Get the ZYXY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.y, self.x, self.y)

    @property
    def zyxz(self) -> 'Vector4D':
        ''' Get the ZYXZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.y, self.x, self.z)

    @property
    def zyxw(self) -> 'Vector4D':
        ''' Get the ZYXW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.y, self.x, self.w)

    @zyxw.setter
    def zyxw(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 4)
                self.z = values[0]
                self.y = values[1]
                self.x = values[2]
                self.w = values[3]
            else:
                self.z = self.y = self.x = self.w = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def zyyx(self) -> 'Vector4D':
        ''' Get the ZYYX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.y, self.y, self.x)

    @property
    def zyyy(self) -> 'Vector4D':
        ''' Get the ZYYY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.y, self.y, self.y)

    @property
    def zyyz(self) -> 'Vector4D':
        ''' Get the ZYYZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.y, self.y, self.z)

    @property
    def zyyw(self) -> 'Vector4D':
        ''' Get the ZYYW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.y, self.y, self.w)

    @property
    def zyzx(self) -> 'Vector4D':
        ''' Get the ZYZX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.y, self.z, self.x)

    @property
    def zyzy(self) -> 'Vector4D':
        ''' Get the ZYZY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.y, self.z, self.y)

    @property
    def zyzz(self) -> 'Vector4D':
        ''' Get the ZYZZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.y, self.z, self.z)

    @property
    def zyzw(self) -> 'Vector4D':
        ''' Get the ZYZW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.y, self.z, self.w)

    @property
    def zywx(self) -> 'Vector4D':
        ''' Get the ZYWX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.y, self.w, self.x)

    @zywx.setter
    def zywx(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 4)
                self.z = values[0]
                self.y = values[1]
                self.w = values[2]
                self.x = values[3]
            else:
                self.z = self.y = self.w = self.x = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def zywy(self) -> 'Vector4D':
        ''' Get the ZYWY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.y, self.w, self.y)

    @property
    def zywz(self) -> 'Vector4D':
        ''' Get the ZYWZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.y, self.w, self.z)

    @property
    def zyww(self) -> 'Vector4D':
        ''' Get the ZYWW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.y, self.w, self.w)

    @property
    def zzxx(self) -> 'Vector4D':
        ''' Get the ZZXX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.z, self.x, self.x)

    @property
    def zzxy(self) -> 'Vector4D':
        ''' Get the ZZXY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.z, self.x, self.y)

    @property
    def zzxz(self) -> 'Vector4D':
        ''' Get the ZZXZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.z, self.x, self.z)

    @property
    def zzxw(self) -> 'Vector4D':
        ''' Get the ZZXW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.z, self.x, self.w)

    @property
    def zzyx(self) -> 'Vector4D':
        ''' Get the ZZYX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.z, self.y, self.x)

    @property
    def zzyy(self) -> 'Vector4D':
        ''' Get the ZZYY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.z, self.y, self.y)

    @property
    def zzyz(self) -> 'Vector4D':
        ''' Get the ZZYZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.z, self.y, self.z)

    @property
    def zzyw(self) -> 'Vector4D':
        ''' Get the ZZYW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.z, self.y, self.w)

    @property
    def zzzx(self) -> 'Vector4D':
        ''' Get the ZZZX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.z, self.z, self.x)

    @property
    def zzzy(self) -> 'Vector4D':
        ''' Get the ZZZY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.z, self.z, self.y)

    @property
    def zzzz(self) -> 'Vector4D':
        ''' Get the ZZZZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.z, self.z, self.z)

    @property
    def zzzw(self) -> 'Vector4D':
        ''' Get the ZZZW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.z, self.z, self.w)

    @property
    def zzwx(self) -> 'Vector4D':
        ''' Get the ZZWX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.z, self.w, self.x)

    @property
    def zzwy(self) -> 'Vector4D':
        ''' Get the ZZWY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.z, self.w, self.y)

    @property
    def zzwz(self) -> 'Vector4D':
        ''' Get the ZZWZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.z, self.w, self.z)

    @property
    def zzww(self) -> 'Vector4D':
        ''' Get the ZZWW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.z, self.w, self.w)

    @property
    def zwxx(self) -> 'Vector4D':
        ''' Get the ZWXX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.w, self.x, self.x)

    @property
    def zwxy(self) -> 'Vector4D':
        ''' Get the ZWXY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.w, self.x, self.y)

    @zwxy.setter
    def zwxy(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 4)
                self.z = values[0]
                self.w = values[1]
                self.x = values[2]
                self.y = values[3]
            else:
                self.z = self.w = self.x = self.y = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def zwxz(self) -> 'Vector4D':
        ''' Get the ZWXZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.w, self.x, self.z)

    @property
    def zwxw(self) -> 'Vector4D':
        ''' Get the ZWXW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.w, self.x, self.w)

    @property
    def zwyx(self) -> 'Vector4D':
        ''' Get the ZWYX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.w, self.y, self.x)

    @zwyx.setter
    def zwyx(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 4)
                self.z = values[0]
                self.w = values[1]
                self.y = values[2]
                self.x = values[3]
            else:
                self.z = self.w = self.y = self.x = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def zwyy(self) -> 'Vector4D':
        ''' Get the ZWYY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.w, self.y, self.y)

    @property
    def zwyz(self) -> 'Vector4D':
        ''' Get the ZWYZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.w, self.y, self.z)

    @property
    def zwyw(self) -> 'Vector4D':
        ''' Get the ZWYW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.w, self.y, self.w)

    @property
    def zwzx(self) -> 'Vector4D':
        ''' Get the ZWZX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.w, self.z, self.x)

    @property
    def zwzy(self) -> 'Vector4D':
        ''' Get the ZWZY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.w, self.z, self.y)

    @property
    def zwzz(self) -> 'Vector4D':
        ''' Get the ZWZZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.w, self.z, self.z)

    @property
    def zwzw(self) -> 'Vector4D':
        ''' Get the ZWZW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.w, self.z, self.w)

    @property
    def zwwx(self) -> 'Vector4D':
        ''' Get the ZWWX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.w, self.w, self.x)

    @property
    def zwwy(self) -> 'Vector4D':
        ''' Get the ZWWY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.w, self.w, self.y)

    @property
    def zwwz(self) -> 'Vector4D':
        ''' Get the ZWWZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.w, self.w, self.z)

    @property
    def zwww(self) -> 'Vector4D':
        ''' Get the ZWWW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.z, self.w, self.w, self.w)

    @property
    def wxxx(self) -> 'Vector4D':
        ''' Get the WXXX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.x, self.x, self.x)

    @property
    def wxxy(self) -> 'Vector4D':
        ''' Get the WXXY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.x, self.x, self.y)

    @property
    def wxxz(self) -> 'Vector4D':
        ''' Get the WXXZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.x, self.x, self.z)

    @property
    def wxxw(self) -> 'Vector4D':
        ''' Get the WXXW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.x, self.x, self.w)

    @property
    def wxyx(self) -> 'Vector4D':
        ''' Get the WXYX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.x, self.y, self.x)

    @property
    def wxyy(self) -> 'Vector4D':
        ''' Get the WXYY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.x, self.y, self.y)

    @property
    def wxyz(self) -> 'Vector4D':
        ''' Get the WXYZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.x, self.y, self.z)

    @wxyz.setter
    def wxyz(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 4)
                self.w = values[0]
                self.x = values[1]
                self.y = values[2]
                self.z = values[3]
            else:
                self.w = self.x = self.y = self.z = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def wxyw(self) -> 'Vector4D':
        ''' Get the WXYW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.x, self.y, self.w)

    @property
    def wxzx(self) -> 'Vector4D':
        ''' Get the WXZX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.x, self.z, self.x)

    @property
    def wxzy(self) -> 'Vector4D':
        ''' Get the WXZY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.x, self.z, self.y)

    @wxzy.setter
    def wxzy(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 4)
                self.w = values[0]
                self.x = values[1]
                self.z = values[2]
                self.y = values[3]
            else:
                self.w = self.x = self.z = self.y = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def wxzz(self) -> 'Vector4D':
        ''' Get the WXZZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.x, self.z, self.z)

    @property
    def wxzw(self) -> 'Vector4D':
        ''' Get the WXZW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.x, self.z, self.w)

    @property
    def wxwx(self) -> 'Vector4D':
        ''' Get the WXWX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.x, self.w, self.x)

    @property
    def wxwy(self) -> 'Vector4D':
        ''' Get the WXWY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.x, self.w, self.y)

    @property
    def wxwz(self) -> 'Vector4D':
        ''' Get the WXWZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.x, self.w, self.z)

    @property
    def wxww(self) -> 'Vector4D':
        ''' Get the WXWW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.x, self.w, self.w)

    @property
    def wyxx(self) -> 'Vector4D':
        ''' Get the WYXX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.y, self.x, self.x)

    @property
    def wyxy(self) -> 'Vector4D':
        ''' Get the WYXY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.y, self.x, self.y)

    @property
    def wyxz(self) -> 'Vector4D':
        ''' Get the WYXZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.y, self.x, self.z)

    @wyxz.setter
    def wyxz(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 4)
                self.w = values[0]
                self.y = values[1]
                self.x = values[2]
                self.z = values[3]
            else:
                self.w = self.y = self.x = self.z = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def wyxw(self) -> 'Vector4D':
        ''' Get the WYXW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.y, self.x, self.w)

    @property
    def wyyx(self) -> 'Vector4D':
        ''' Get the WYYX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.y, self.y, self.x)

    @property
    def wyyy(self) -> 'Vector4D':
        ''' Get the WYYY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.y, self.y, self.y)

    @property
    def wyyz(self) -> 'Vector4D':
        ''' Get the WYYZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.y, self.y, self.z)

    @property
    def wyyw(self) -> 'Vector4D':
        ''' Get the WYYW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.y, self.y, self.w)

    @property
    def wyzx(self) -> 'Vector4D':
        ''' Get the WYZX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.y, self.z, self.x)

    @wyzx.setter
    def wyzx(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 4)
                self.w = values[0]
                self.y = values[1]
                self.z = values[2]
                self.x = values[3]
            else:
                self.w = self.y = self.z = self.x = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def wyzy(self) -> 'Vector4D':
        ''' Get the WYZY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.y, self.z, self.y)

    @property
    def wyzz(self) -> 'Vector4D':
        ''' Get the WYZZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.y, self.z, self.z)

    @property
    def wyzw(self) -> 'Vector4D':
        ''' Get the WYZW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.y, self.z, self.w)

    @property
    def wywx(self) -> 'Vector4D':
        ''' Get the WYWX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.y, self.w, self.x)

    @property
    def wywy(self) -> 'Vector4D':
        ''' Get the WYWY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.y, self.w, self.y)

    @property
    def wywz(self) -> 'Vector4D':
        ''' Get the WYWZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.y, self.w, self.z)

    @property
    def wyww(self) -> 'Vector4D':
        ''' Get the WYWW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.y, self.w, self.w)

    @property
    def wzxx(self) -> 'Vector4D':
        ''' Get the WZXX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.z, self.x, self.x)

    @property
    def wzxy(self) -> 'Vector4D':
        ''' Get the WZXY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.z, self.x, self.y)

    @wzxy.setter
    def wzxy(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 4)
                self.w = values[0]
                self.z = values[1]
                self.x = values[2]
                self.y = values[3]
            else:
                self.w = self.z = self.x = self.y = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def wzxz(self) -> 'Vector4D':
        ''' Get the WZXZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.z, self.x, self.z)

    @property
    def wzxw(self) -> 'Vector4D':
        ''' Get the WZXW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.z, self.x, self.w)

    @property
    def wzyx(self) -> 'Vector4D':
        ''' Get the WZYX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.z, self.y, self.x)

    @wzyx.setter
    def wzyx(self, value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_set(value, 4)
                self.w = values[0]
                self.z = values[1]
                self.y = values[2]
                self.x = values[3]
            else:
                self.w = self.z = self.y = self.x = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_MESSAGE) from None

    @property
    def wzyy(self) -> 'Vector4D':
        ''' Get the WZYY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.z, self.y, self.y)

    @property
    def wzyz(self) -> 'Vector4D':
        ''' Get the WZYZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.z, self.y, self.z)

    @property
    def wzyw(self) -> 'Vector4D':
        ''' Get the WZYW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.z, self.y, self.w)

    @property
    def wzzx(self) -> 'Vector4D':
        ''' Get the WZZX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.z, self.z, self.x)

    @property
    def wzzy(self) -> 'Vector4D':
        ''' Get the WZZY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.z, self.z, self.y)

    @property
    def wzzz(self) -> 'Vector4D':
        ''' Get the WZZZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.z, self.z, self.z)

    @property
    def wzzw(self) -> 'Vector4D':
        ''' Get the WZZW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.z, self.z, self.w)

    @property
    def wzwx(self) -> 'Vector4D':
        ''' Get the WZWX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.z, self.w, self.x)

    @property
    def wzwy(self) -> 'Vector4D':
        ''' Get the WZWY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.z, self.w, self.y)

    @property
    def wzwz(self) -> 'Vector4D':
        ''' Get the WZWZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.z, self.w, self.z)

    @property
    def wzww(self) -> 'Vector4D':
        ''' Get the WZWW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.z, self.w, self.w)

    @property
    def wwxx(self) -> 'Vector4D':
        ''' Get the WWXX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.w, self.x, self.x)

    @property
    def wwxy(self) -> 'Vector4D':
        ''' Get the WWXY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.w, self.x, self.y)

    @property
    def wwxz(self) -> 'Vector4D':
        ''' Get the WWXZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.w, self.x, self.z)

    @property
    def wwxw(self) -> 'Vector4D':
        ''' Get the WWXW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.w, self.x, self.w)

    @property
    def wwyx(self) -> 'Vector4D':
        ''' Get the WWYX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.w, self.y, self.x)

    @property
    def wwyy(self) -> 'Vector4D':
        ''' Get the WWYY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.w, self.y, self.y)

    @property
    def wwyz(self) -> 'Vector4D':
        ''' Get the WWYZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.w, self.y, self.z)

    @property
    def wwyw(self) -> 'Vector4D':
        ''' Get the WWYW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.w, self.y, self.w)

    @property
    def wwzx(self) -> 'Vector4D':
        ''' Get the WWZX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.w, self.z, self.x)

    @property
    def wwzy(self) -> 'Vector4D':
        ''' Get the WWZY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.w, self.z, self.y)

    @property
    def wwzz(self) -> 'Vector4D':
        ''' Get the WWZZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.w, self.z, self.z)

    @property
    def wwzw(self) -> 'Vector4D':
        ''' Get the WWZW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.w, self.z, self.w)

    @property
    def wwwx(self) -> 'Vector4D':
        ''' Get the WWWX components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.w, self.w, self.x)

    @property
    def wwwy(self) -> 'Vector4D':
        ''' Get the WWWY components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.w, self.w, self.y)

    @property
    def wwwz(self) -> 'Vector4D':
        ''' Get the WWWZ components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.w, self.w, self.z)

    @property
    def wwww(self) -> 'Vector4D':
        ''' Get the WWWW components of the vector

        Returns:
            'Vector4D'
        '''

        return Vector4D(self.w, self.w, self.w, self.w)

    @classmethod
    def zero() -> 'Vector4D':
        ''' Returns a Vector4D filled with 0s

        Returns:
            Vector4D
        '''

        return Vector4D.broadcast(0)

    @classmethod
    def one() -> 'Vector4D':
        ''' Returns a Vector4D filled with 1s

        Returns:
            Vector4D
        '''

        return Vector4D.broadcast(1)

    @classmethod
    def _force_dim(cls, v: Union[NUM, Iterable[NUM]]) -> Tuple[NUM]:
        b = hasattr(v, '__iter__')

        if b and len(v) != 4:
            raise VectorException(ERROR_4D_MESSAGE)
        elif not b:
            v = (v, v, v, v)

        return tuple(v)

    @classmethod
    def _make_vec(cls, v: Union[NUM, Iterable[NUM]]) -> 'Vector3D':
        return Vector4D.from_iterable(cls._force_dim(v))

    def __add__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector4D':
        other = Vector4D._force_dim(other)

        x = self.x + other[0]
        y = self.y + other[1]
        z = self.z + other[2]
        w = self.w + other[3]
        return Vector4D(x, y, z, w)

    def __radd__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector4D':
        other = Vector4D._force_dim(other)

        x = other[0] + self.x
        y = other[1] + self.y
        z = other[2] + self.z
        w = other[3] + self.w
        return Vector4D(x, y, z, w)

    def __sub__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector4D':
        other = Vector4D._force_dim(other)

        x = self.x - other[0]
        y = self.y - other[1]
        z = self.z - other[2]
        w = self.w - other[3]
        return Vector4D(x, y, z, w)

    def __rsub__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector4D':
        other = Vector4D._force_dim(other)

        x = other[0] - self.x
        y = other[1] - self.y
        z = other[2] - self.z
        w = other[3] - self.w
        return Vector4D(x, y, z, w)

    def __mul__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector4D':
        other = Vector4D._force_dim(other)

        x = self.x * other[0]
        y = self.y * other[1]
        z = self.z * other[2]
        w = self.w * other[3]
        return Vector4D(x, y, z, w)

    def __rmul__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector4D':
        other = Vector4D._force_dim(other)

        x = other[0] * self.x
        y = other[1] * self.y
        z = other[2] * self.z
        w = other[3] * self.w
        return Vector4D(x, y, z, w)

    def __matmul__(self, other: Union[NUM, Iterable[NUM]]) -> float:
        return Vector4D.dot(self, other)

    def __rmatmul__(self, other: Union[NUM, Iterable[NUM]]) -> float:
        return Vector4D.dot(other, self)

    def __truediv__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector4D':
        other = Vector4D._force_dim(other)

        x = self.x / other[0]
        y = self.y / other[1]
        z = self.z / other[2]
        w = self.w / other[3]
        return Vector4D(x, y, z, w)

    def __rtruediv__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector4D':
        other = Vector4D._force_dim(other)

        x = other[0] / self.x
        y = other[1] / self.y
        z = other[2] / self.z
        w = other[3] / self.w
        return Vector4D(x, y, z, w)

    def __floordiv__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector4D':
        other = Vector4D._force_dim(other)

        x = self.x // other[0]
        y = self.y // other[1]
        z = self.z // other[2]
        w = self.w // other[3]
        return Vector4D(x, y, z, w)

    def __rfloordiv__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector4D':
        other = Vector4D._force_dim(other)

        x = other[0] // self.x
        y = other[1] // self.y
        z = other[2] // self.z
        w = other[3] // self.w
        return Vector4D(x, y, z, w)

    def __abs__(self) -> 'Vector4D':
        x = abs(self.x)
        y = abs(self.y)
        z = abs(self.z)
        w = abs(self.w)
        return Vector4D(x, y, z, w)

    def __mod__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector4D':
        other = Vector4D._force_dim(other)

        x = self.x % other[0]
        y = self.y % other[1]
        z = self.z % other[2]
        w = self.w % other[3]
        return Vector4D(x, y, z, w)

    def __rmod__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector4D':
        other = Vector4D._force_dim(other)

        x = other[0] % self.x
        y = other[1] % self.y
        z = other[2] % self.z
        w = other[3] % self.w
        return Vector4D(x, y, z, w)

    def __pow__(self, other: Union[NUM, Iterable[NUM]]) -> 'Vector4D':
        return Vector4D.pow(self, other)

    def __pos__(self) -> 'Vector4D':
        return Vector4D(+self.x, +self.y, +self.z, +self.w)

    def __neg__(self) -> 'Vector4D':
        return Vector4D(-self.x, -self.y, -self.z, -self.w)

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
            w = scalar.approximately_equal(v0[3], v1[3], e)

            return x, y, z, w

        return safe_vector4_op(_approximately_equals, v0, v1, epsilon)

    @classmethod
    def min(
            cls,
            v0: Iterable[NUM],
            v1: Union[NUM, Iterable[NUM]]) -> 'Vector4D':
        ''' Component-wise min.

        Args:
            v0 (Iterable[NUM]): First vector to compare
            v1 (Union[NUM, Iterable[NUM]]): Second value to compare

        Returns:
            Vector4D
        '''

        def _min(v0, v1):
            v0 = tuple(v0)
            v1 = cls._force_dim(v1)

            x = min(v0[0], v1[0])
            y = min(v0[1], v1[1])
            z = min(v0[2], v1[2])
            w = min(v0[3], v1[3])

            return Vector4D(x, y, z, w)

        return safe_vector4_op(_min, v0, v1)

    @classmethod
    def max(
            cls,
            v0: Iterable[NUM],
            v1: Union[NUM, Iterable[NUM]]) -> 'Vector4D':
        ''' Component-wise max.

        Args:
            v0 (Iterable[NUM]): First vector to compare
            v1 (Union[NUM, Iterable[NUM]]): Second value to compare

        Returns:
            Vector4D
        '''

        def _max(v0, v1):
            v0 = tuple(v0)
            v1 = cls._force_dim(v1)

            x = max(v0[0], v1[0])
            y = max(v0[1], v1[1])
            z = max(v0[2], v1[2])
            w = max(v0[3], v1[3])

            return Vector4D(x, y, z, w)

        return safe_vector4_op(_max, v0, v1)

    @classmethod
    def clamp(
            cls,
            v: Iterable[NUM],
            vmin: Union[NUM, Iterable[NUM]],
            vmax: Union[NUM, Iterable[NUM]]) -> 'Vector4D':
        ''' Component-wise clamp.

        Equivalent to min(vmax, max(vmin, v))

        Args:
            v (Iterable[NUM]): Vector to clamp
            vmin (Union[NUM, Iterable[NUM]]):
                Lower end of the range into which to constrain v
            vmax (Union[NUM, Iterable[NUM]]):
                Upper end of the range into which to constrain v

        Returns:
            Vector4D
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
            w = scalar.clamp(v[3], vmin[3], vmax[3])

            return Vector4D(x, y, z, w)

        return safe_vector4_op(_clamp, v, vmin, vmax)

    @classmethod
    def interpolate(
            cls,
            v0: Iterable[NUM],
            v1: Iterable[NUM],
            i: Union[NUM, Iterable[NUM]]) -> 'Vector4D':
        ''' Component-wise interpolation.

        Equivalent to v0 * (1.0 - i) + v1 * i

        Args:
            v0 (Iterable[NUM]): Start of the range in which to interpolate
            v1 (Iterable[NUM]): End of the range in which to interpolate
            i (Union[NUM, Iterable[NUM]]):
                Value to use to interpolate between v0 and v1

        Returns:
            Vector4D
        '''

        v0 = cls._make_vec(v0)
        v1 = cls._make_vec(v1)
        i = cls._make_vec(i)

        return v0 * (1.0 - i) + v1 * i

    @classmethod
    def sign(cls, v: Iterable[NUM]) -> 'Vector4D':
        ''' Component-wise extraction of the sign.

        Returns -1.0 if v is less than 0.0, 0.0 if v is equal to 0.0,
        and +1.0 if v is greater than 0.0.

        Args:
            v (Iterable[NUM]): Vector from which to extract the sign.

        Returns:
            Vector4D
        '''

        def _sign(v):
            v = tuple(v)

            x = scalar.sign(v[0])
            y = scalar.sign(v[1])
            z = scalar.sign(v[2])
            w = scalar.sign(v[3])
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_sign, v)

    @classmethod
    def floor(cls, v: Iterable[NUM]) -> 'Vector4D':
        ''' Component-wise floor.

        Args:
            v (Iterable[NUM]): Vector to floor.

        Returns:
            Vector4D
        '''

        def _floor(v):
            v = tuple(v)

            x = math.floor(v[0])
            y = math.floor(v[1])
            z = math.floor(v[2])
            w = math.floor(v[3])
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_floor, v)

    @classmethod
    def ceil(cls, v: Iterable[NUM]) -> 'Vector4D':
        ''' Component-wise ceil.

        Args:
            v (Iterable[NUM]): Vector to ceil.

        Returns:
            Vector4D
        '''

        def _ceil(v):
            v = tuple(v)

            x = math.ceil(v[0])
            y = math.ceil(v[1])
            z = math.ceil(v[2])
            w = math.ceil(v[3])
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_ceil, v)

    @classmethod
    def fract(cls, v: Iterable[NUM]) -> 'Vector4D':
        ''' Component-wise extraction of the fractional part of the parameter.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector4D
        '''

        def _fract(v):
            v = tuple(v)

            x = scalar.fract(v[0])
            y = scalar.fract(v[1])
            z = scalar.fract(v[2])
            w = scalar.fract(v[3])
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_fract, v)

    @classmethod
    def step(
            cls,
            edge: Union[NUM, Iterable[NUM]],
            v: Iterable[NUM]) -> 'Vector4D':
        ''' Component-wise step.

        For each index i, 0.0 is returned if v[i] < edge[i], and 1.0 is
        returned otherwise.

        Args:
            edge (Union[NUM, Iterable[NUM]]): Edge of the step function.
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector4D
        '''

        def _step(edge, v):
            v = tuple(v)
            edge = cls._force_dim(edge)

            x = scalar.step(edge[0], v[0])
            y = scalar.step(edge[1], v[1])
            z = scalar.step(edge[2], v[2])
            w = scalar.step(edge[3], v[3])
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_step, edge, v)

    @classmethod
    def smoothstep(
            cls,
            edge0: Union[NUM, Iterable[NUM]],
            edge1: Union[NUM, Iterable[NUM]],
            v: Iterable[NUM]) -> 'Vector4D':
        ''' Component-wise hermite interpolation between two values.

        Args:
            edge0 (Union[NUM, Iterable[NUM]]):
                Lower edge of the hermite function.
            edge1 (Union[NUM, Iterable[NUM]]):
                Upper edge of the hermite function.
            v (Iterable[NUM]): Vector to interpolate.

        Returns:
            Vector4D
        '''

        def _smoothstep(edge0, edge1, v):
            v = tuple(v)
            edge0 = cls._force_dim(edge0)
            edge1 = cls._force_dim(edge1)

            x = scalar.smoothstep(edge0[0], edge1[0], v[0])
            y = scalar.smoothstep(edge0[1], edge1[1], v[1])
            z = scalar.smoothstep(edge0[2], edge1[2], v[2])
            w = scalar.smoothstep(edge0[3], edge1[3], v[3])
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_smoothstep, edge0, edge1, v)

    @classmethod
    def sqrt(cls, v: Iterable[NUM]) -> 'Vector4D':
        ''' Component-wise square root.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector4D
        '''

        def _sqrt(v):
            v = tuple(v)

            x = math.sqrt(v[0])
            y = math.sqrt(v[1])
            z = math.sqrt(v[2])
            w = math.sqrt(v[3])
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_sqrt, v)

    @classmethod
    def inverse_sqrt(cls, v: Iterable[NUM]) -> 'Vector4D':
        ''' Component-wise inverse square root.

        This is equivalent to 1.0 / Vector4D.sqrt(v).

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector4D
        '''

        def _inverse_sqrt(v):
            v = tuple(v)

            x = 1.0 / math.sqrt(v[0])
            y = 1.0 / math.sqrt(v[1])
            z = 1.0 / math.sqrt(v[2])
            w = 1.0 / math.sqrt(v[3])
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_inverse_sqrt, v)

    @classmethod
    def pow(cls, v: Iterable[NUM], w: Union[NUM, Iterable[NUM]]) -> 'Vector4D':
        ''' Component-wise power.

        Args:
            v (Iterable[NUM]): Vector to evaluate.
            w (Union[NUM, Iterable[NUM]]): Power to which to raise v.

        Returns:
            Vector4D
        '''

        def _pow(v, w):
            v = tuple(v)
            w = cls._force_dim(w)

            x = v[0] ** w[0]
            y = v[1] ** w[1]
            z = v[2] ** w[2]
            w = v[3] ** w[3]
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_pow, v, w)

    @classmethod
    def exp(cls, v: Iterable[NUM]) -> 'Vector4D':
        ''' Component-wise natural exponential.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector4D
        '''

        def _exp(v):
            v = tuple(v)

            x = math.exp(v[0])
            y = math.exp(v[1])
            z = math.exp(v[2])
            w = math.exp(v[3])
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_exp, v)

    @classmethod
    def exp2(cls, v: Iterable[NUM]) -> 'Vector4D':
        ''' Component-wise. 2 raised to the power of the parameter.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector4D
        '''

        def _exp2(v):
            v = tuple(v)

            x = 2 ** v[0]
            y = 2 ** v[1]
            z = 2 ** v[2]
            w = 2 ** v[3]
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_exp2, v)

    @classmethod
    def exp10(cls, v: Iterable[NUM]) -> 'Vector4D':
        ''' Component-wise. 10 raised to the power of the parameter.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector4D
        '''

        def _exp10(v):
            v = tuple(v)

            x = 10 ** v[0]
            y = 10 ** v[1]
            z = 10 ** v[2]
            w = 10 ** v[3]
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_exp10, v)

    @classmethod
    def log(cls, v: Iterable[NUM]) -> 'Vector4D':
        ''' Component-wise natural logarithm.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector4D
        '''

        def _log(v):
            v = tuple(v)

            x = math.log(v[0])
            y = math.log(v[1])
            z = math.log(v[2])
            w = math.log(v[3])
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_log, v)

    @classmethod
    def log2(cls, v: Iterable[NUM]) -> 'Vector4D':
        ''' Component-wise base-2 logarithm.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector4D
        '''

        def _log2(v):
            v = tuple(v)

            x = math.log2(v[0])
            y = math.log2(v[1])
            z = math.log2(v[2])
            w = math.log2(v[3])
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_log2, v)

    @classmethod
    def log10(cls, v: Iterable[NUM]) -> 'Vector4D':
        ''' Component-wise base-10 logarithm.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector4D
        '''

        def _log10(v):
            v = tuple(v)

            x = math.log10(v[0])
            y = math.log10(v[1])
            z = math.log10(v[2])
            w = math.log10(v[3])
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_log10, v)

    @classmethod
    def radians(cls, v: Iterable[NUM]) -> 'Vector4D':
        ''' Component-wise conversion from degrees to radians.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector4D
        '''

        def _radians(v):
            v = tuple(v)

            x = math.radians(v[0])
            y = math.radians(v[1])
            z = math.radians(v[2])
            w = math.radians(v[3])
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_radians, v)

    @classmethod
    def degrees(cls, v: Iterable[NUM]) -> 'Vector4D':
        ''' Component-wise conversion from radians to degrees.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector4D
        '''

        def _degrees(v):
            v = tuple(v)

            x = math.degrees(v[0])
            y = math.degrees(v[1])
            z = math.degrees(v[2])
            w = math.degrees(v[3])
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_degrees, v)

    @classmethod
    def sin(cls, v: Iterable[NUM]) -> 'Vector4D':
        ''' Component-wise sine.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector4D
        '''

        def _sin(v):
            v = tuple(v)

            x = math.sin(v[0])
            y = math.sin(v[1])
            z = math.sin(v[2])
            w = math.sin(v[3])
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_sin, v)

    @classmethod
    def cos(cls, v: Iterable[NUM]) -> 'Vector4D':
        ''' Component-wise cosine.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector4D
        '''

        def _cos(v):
            v = tuple(v)

            x = math.cos(v[0])
            y = math.cos(v[1])
            z = math.cos(v[2])
            w = math.cos(v[3])
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_cos, v)

    @classmethod
    def tan(cls, v: Iterable[NUM]) -> 'Vector4D':
        ''' Component-wise tangent.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector4D
        '''

        def _tan(v):
            v = tuple(v)

            x = math.tan(v[0])
            y = math.tan(v[1])
            z = math.tan(v[2])
            w = math.tan(v[3])
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_tan, v)

    @classmethod
    def sinh(cls, v: Iterable[NUM]) -> 'Vector4D':
        ''' Component-wise hyperbolic sine.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector4D
        '''

        def _sinh(v):
            v = tuple(v)

            x = math.sinh(v[0])
            y = math.sinh(v[1])
            z = math.sinh(v[2])
            w = math.sinh(v[3])
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_sinh, v)

    @classmethod
    def cosh(cls, v: Iterable[NUM]) -> 'Vector4D':
        ''' Component-wise hyperbolic cosine.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector4D
        '''

        def _cosh(v):
            v = tuple(v)

            x = math.cosh(v[0])
            y = math.cosh(v[1])
            z = math.cosh(v[2])
            w = math.cosh(v[3])
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_cosh, v)

    @classmethod
    def tanh(cls, v: Iterable[NUM]) -> 'Vector4D':
        ''' Component-wise hyperbolic tangent.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector4D
        '''

        def _tanh(v):
            v = tuple(v)

            x = math.tanh(v[0])
            y = math.tanh(v[1])
            z = math.tanh(v[2])
            w = math.tanh(v[3])
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_tanh, v)

    @classmethod
    def asin(cls, v: Iterable[NUM]) -> 'Vector4D':
        ''' Component-wise arc-sine.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector4D
        '''

        def _asin(v):
            v = tuple(v)

            x = math.asin(v[0])
            y = math.asin(v[1])
            z = math.asin(v[2])
            w = math.asin(v[3])
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_asin, v)

    @classmethod
    def acos(cls, v: Iterable[NUM]) -> 'Vector4D':
        ''' Component-wise arc-cosine.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector4D
        '''

        def _acos(v):
            v = tuple(v)

            x = math.acos(v[0])
            y = math.acos(v[1])
            z = math.acos(v[2])
            w = math.acos(v[3])
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_acos, v)

    @classmethod
    def atan(cls, v: Iterable[NUM]) -> 'Vector4D':
        ''' Component-wise arc-tangent.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector4D
        '''

        def _atan(v):
            v = tuple(v)

            x = math.atan(v[0])
            y = math.atan(v[1])
            z = math.atan(v[2])
            w = math.atan(v[3])
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_atan, v)

    @classmethod
    def atan2(
            cls, v: Iterable[NUM], w: Union[NUM, Iterable[NUM]]) -> 'Vector4D':
        ''' Component-wise arc-tangent with separable numerator
        and denominator.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector4D
        '''

        def _atan2(v, w):
            v = tuple(v)
            w = cls._force_dim(w)

            x = math.atan2(v[0], w[0])
            y = math.atan2(v[1], w[1])
            z = math.atan2(v[2], w[2])
            w = math.atan2(v[3], w[3])
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_atan2, v, w)

    @classmethod
    def asinh(cls, v: Iterable[NUM]) -> 'Vector4D':
        ''' Component-wise hyperbolic arc-sine.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector4D
        '''

        def _asinh(v):
            v = tuple(v)

            x = math.asinh(v[0])
            y = math.asinh(v[1])
            z = math.asinh(v[2])
            w = math.asinh(v[3])
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_asinh, v)

    @classmethod
    def acosh(cls, v: Iterable[NUM]) -> 'Vector4D':
        ''' Component-wise hyperbolic arc-cosine.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector4D
        '''

        def _acosh(v):
            v = tuple(v)

            x = math.acosh(v[0])
            y = math.acosh(v[1])
            z = math.acosh(v[2])
            w = math.acosh(v[3])
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_acosh, v)

    @classmethod
    def atanh(cls, v: Iterable[NUM]) -> 'Vector4D':
        ''' Component-wise hyperbolic arc-tangent.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector4D
        '''

        def _atanh(v):
            v = tuple(v)

            x = math.atanh(v[0])
            y = math.atanh(v[1])
            z = math.atanh(v[2])
            w = math.atanh(v[3])
            return Vector4D(x, y, z, w)

        return safe_vector4_op(_atanh, v)

    @classmethod
    def _dot(cls, v0: 'Vector4D', v1: 'Vector4D') -> float:
        return v0[0] * v1[0] + v0[1] * v1[1] + v0[2] * v1[2] + v0[3] * v1[3]

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

        return safe_vector4_op(_d, v0, v1)

    @classmethod
    def _length(cls, v: 'Vector4D') -> float:
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
    def normalize(cls, v: Iterable[NUM]) -> 'Vector4D':
        ''' Vector normalization.

        Args:
            v (Iterable[NUM]): Vector to evaluate.

        Returns:
            Vector4D
        '''

        v = cls._make_vec(v)

        return v / cls._length(v)

    @classmethod
    def face_forward(
            cls,
            v: Iterable[NUM],
            i: Iterable[NUM],
            vref: Iterable[NUM]) -> 'Vector4D':
        ''' Return a vector pointing in the same direction as another.

        If dot(vref, i) < 0.0, returns v. Otherwise returns -v.

        Args:
            v (Iterable[NUM]): Vector to orient.
            i (Iterable[NUM]): Incident vector.
            vref (Iterable[NUM]): Reference vector.

        Returns:
            Vector4D
        '''

        v = cls._make_vec(v)
        i = cls._make_vec(i)
        vref = cls._make_vec(vref)

        return v if cls._dot(vref, i) < 0.0 else -v

    @classmethod
    def reflect(cls, i: Iterable[NUM], n: Iterable[NUM]) -> 'Vector4D':
        ''' Reflection direction of an incident vector.

        Note:
            n should be normalized.

        Args:
            i (Iterable[NUM]): Incident vector.
            n (Iterable[NUM]): Normal vector.

        Returns:
            Vector4D
        '''

        i = cls._make_vec(i)
        n = cls._make_vec(n)

        return i - 2.0 * cls._dot(n, i) * n

    @classmethod
    def refract(
            cls, i: Iterable[NUM], n: Iterable[NUM], r: float) -> 'Vector4D':
        ''' Refraction direction of an incident vector.

        Note:
            i and n should be normalized.

        Args:
            i (Iterable[NUM]): Incident vector.
            n (Iterable[NUM]): Normal vector.
            r (float): Ratio of indices of refraction.

        Returns:
            Vector4D
        '''

        i = cls._make_vec(i)
        n = cls._make_vec(n)

        ndoti = cls._dot(n, i)
        d = 1.0 - r * r * (1.0 - ndoti * ndoti)

        # Total internal reflection
        if d < 0.0:
            return 0.0

        return r * i - (r * ndoti + math.sqrt(d)) * n
