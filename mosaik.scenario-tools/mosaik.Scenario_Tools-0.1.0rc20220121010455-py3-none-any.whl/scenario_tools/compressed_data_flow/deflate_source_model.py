class DeflateSourceModel(object):
    def __init__(self, eid):
        self._data: dict = {}
        self._eid: str = eid

    @property
    def eid(self):
        return self._eid

    def step(self) -> None:
        self._data: dict = {
            'bool': [True] * 10,
            'float': [3.14] * 10,
            'int': [42] * 10,
            'str': ['foo'] * 10,
            'dict': [{'bar': 'foobar'}] * 10,
            'None': [None] * 10,
        }

    def get_data(self) -> dict:
        return self._data
