'''tuple_with_name.py'''


from typing import Optional, Sequence, Any


class TupleWithName(tuple):
    '''Create a TupleWithName with any number of arguments and a name.

    Args:
        *args (Sequence[Any]): arguments for the tuple
        name (str, optional): An optional name for the tuple

    Note:
        The API's NamedTuple object is a tuple with a single name, which is
        different to Python's namedtuple. Therefore, this implementation
        has been named TupleWithName to make that more clear.
    '''

    def __new__(cls, *args: Sequence[Any], name: Optional[str] = None):
        return super(TupleWithName, cls).__new__(TupleWithName, args)

    def __init__(self, *args: Sequence[Any], name: Optional[str] = None):
        self._name = name

    @property
    def name(self) -> str:
        '''The name of the tuple

        Returns:
            str: the name
        '''
        return self._name

    def __str__(self):
        values = ', '.join(str(x) for x in self)
        return (
            '({}; {})'.format(self.name, values) if self.name
            else '({})'.format(values))

    def __repr__(self):
        return '{}({}, name=\'{}\')'.format(
            self.__class__.__qualname__,
            ', '.join(str(x) for x in self),
            self.name)

