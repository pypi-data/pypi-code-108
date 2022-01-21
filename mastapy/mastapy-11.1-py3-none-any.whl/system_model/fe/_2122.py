'''_2122.py

FEStiffnessGeometry
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_FE_STIFFNESS_GEOMETRY = python_net_import('SMT.MastaAPI.SystemModel.FE', 'FEStiffnessGeometry')


__docformat__ = 'restructuredtext en'
__all__ = ('FEStiffnessGeometry',)


class FEStiffnessGeometry(_0.APIBase):
    '''FEStiffnessGeometry

    This is a mastapy class.
    '''

    TYPE = _FE_STIFFNESS_GEOMETRY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FEStiffnessGeometry.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.'''

        return self.wrapped.Name

    @name.setter
    def name(self, value: 'str'):
        self.wrapped.Name = str(value) if value else ''

    def delete_geometry(self):
        ''' 'DeleteGeometry' is the original name of this method.'''

        self.wrapped.DeleteGeometry()

    def reduce_file_size(self):
        ''' 'ReduceFileSize' is the original name of this method.'''

        self.wrapped.ReduceFileSize()
