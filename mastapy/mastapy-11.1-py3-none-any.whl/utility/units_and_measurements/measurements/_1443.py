'''_1443.py

Index
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_INDEX = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'Index')


__docformat__ = 'restructuredtext en'
__all__ = ('Index',)


class Index(_1398.MeasurementBase):
    '''Index

    This is a mastapy class.
    '''

    TYPE = _INDEX

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Index.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
