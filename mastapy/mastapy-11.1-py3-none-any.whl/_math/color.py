from typing import Optional, Iterable, Any, Union, Iterator

from mastapy._math.vector_base import VectorException, NUM, ERROR_SET_PROPERTY
from mastapy._math.vector_4d import Vector4D


class Color(Vector4D):
    '''Create a Color from R, G and B and A components

    Args:
        r: NUM
        g: NUM
        b: NUM
        a: NUM

    Returns:
        Color
    '''

    def __init__(self, r: NUM, g: NUM, b: NUM, a: Optional[NUM] = 255):
        super().__init__(float(r), float(g), float(b), float(a))

    @classmethod
    def broadcast(cls, value: NUM) -> 'Color':
        ''' Create a Color by broadcasting a value to all of its dimensions

        Args:
            value: NUM

        Returns:
            Color
        '''

        return cls(value, value, value, value)

    @classmethod
    def from_iterable(cls, t: Iterable[NUM]) -> 'Color':
        ''' Create a Color from an Iterable

        Args:
            t: Iterable[NUM]

        Returns:
            Color
        '''

        t = tuple(t)

        try:
            return cls(t[0], t[1], t[2], t[3])
        except (KeyError, TypeError, AttributeError):
            raise VectorException(
                'Tuple must be of at least length 4.') from None

    @classmethod
    def wrap(cls, value: Any) -> 'Color':
        try:
            new_vector = cls(value.R, value.G, value.B, value.A)
            return new_vector
        except AttributeError:
            raise VectorException(
                'Value to wrap has no R, G, B or A component.')

    @property
    def r(self) -> int:
        ''' Get the red component of the color

        Returns:
            int
        '''

        return int(self[0])

    @r.setter
    def r(self, value: NUM):
        self[0] = float(value)
        if self.wrapped:
            raise VectorException(ERROR_SET_PROPERTY) from None

    @property
    def g(self) -> int:
        ''' Get the green component of the color

        Returns:
            int
        '''

        return int(self[1])

    @g.setter
    def g(self, value: NUM):
        self[1] = float(value)
        if self.wrapped:
            raise VectorException(ERROR_SET_PROPERTY) from None

    @property
    def b(self) -> int:
        ''' Get the blue component of the color

        Returns:
            int
        '''

        return int(self[2])

    @b.setter
    def b(self, value: NUM):
        self[2] = float(value)
        if self.wrapped:
            raise VectorException(ERROR_SET_PROPERTY) from None

    @property
    def a(self) -> int:
        ''' Get the alpha component of the color

        Returns:
            int
        '''

        return int(self[3])

    @a.setter
    def a(self, value: NUM):
        self[3] = float(value)
        if self.wrapped:
            raise VectorException(ERROR_SET_PROPERTY) from None

    def __getitem__(self, index: Union[int, slice]) -> int:
        return int(self._values[index])

    def __iter__(self) -> Iterator[int]:
        return map(int, self._values)

    def __format__(self, format_spec: str) -> str:
        return '({})'.format(', '.join(
            map(lambda x: format(x, format_spec), map(int, self._values))))

    def __repr__(self) -> str:
        return '{}({})'.format(
            self.__class__.__qualname__, ', '.join(
                (str(int(x)) for x in self._values)))
