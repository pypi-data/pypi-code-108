'''_81.py

SparseNodalMatrix
'''


from mastapy.nodal_analysis import _44
from mastapy._internal.python_net import python_net_import

_SPARSE_NODAL_MATRIX = python_net_import('SMT.MastaAPI.NodalAnalysis', 'SparseNodalMatrix')


__docformat__ = 'restructuredtext en'
__all__ = ('SparseNodalMatrix',)


class SparseNodalMatrix(_44.AbstractNodalMatrix):
    '''SparseNodalMatrix

    This is a mastapy class.
    '''

    TYPE = _SPARSE_NODAL_MATRIX

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SparseNodalMatrix.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
