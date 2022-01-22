from typing import List


class InflateSinkModel(object):
    def __init__(self, eid):
        self._eid: str = eid

    @property
    def eid(self):
        return self._eid

    def step(self, data) -> None:
        assert self

        if not isinstance(
            data['float']['DeflateSimulator-0.DeflateSourceModel-0'], List
        ):
            raise TypeError(
                'Expected List but got '
                f'{data["float"]["DeflateSimulator-0.DeflateSourceModel-0"]}.'
            )

        for value in data['float']['DeflateSimulator-0.DeflateSourceModel-0']:
            if not isinstance(value, float):
                raise TypeError()

        if not isinstance(
            data['bool']['DeflateSimulator-0.DeflateSourceModel-0'], List
        ):
            raise TypeError()

        for value in data['bool']['DeflateSimulator-0.DeflateSourceModel-0']:
            if not isinstance(value, bool):
                raise TypeError()

        if not isinstance(
            data['int']['DeflateSimulator-0.DeflateSourceModel-0'], List
        ):
            raise TypeError()

        for value in data['int']['DeflateSimulator-0.DeflateSourceModel-0']:
            if not isinstance(value, int):
                raise TypeError()

        if not isinstance(
            data['str']['DeflateSimulator-0.DeflateSourceModel-0'], List
        ):
            raise TypeError()

        for value in data['str']['DeflateSimulator-0.DeflateSourceModel-0']:
            if not isinstance(value, str):
                raise TypeError()

        if not isinstance(
            data['dict']['DeflateSimulator-0.DeflateSourceModel-0'], List
        ):
            raise TypeError()

        for value in data['dict']['DeflateSimulator-0.DeflateSourceModel-0']:
            if not isinstance(value, dict):
                raise TypeError()

        if not isinstance(
            data['None']['DeflateSimulator-0.DeflateSourceModel-0'], List
        ):
            raise TypeError()

        for value in data['None']['DeflateSimulator-0.DeflateSourceModel-0']:
            if not isinstance(value, type(None)):
                raise TypeError()

    def get_data(self) -> None:
        assert self

        raise NotImplementedError()
