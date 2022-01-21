'''_4953.py

WhineWaterfallReferenceValuesBase
'''


from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_WHINE_WATERFALL_REFERENCE_VALUES_BASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses', 'WhineWaterfallReferenceValuesBase')


__docformat__ = 'restructuredtext en'
__all__ = ('WhineWaterfallReferenceValuesBase',)


class WhineWaterfallReferenceValuesBase(_0.APIBase):
    '''WhineWaterfallReferenceValuesBase

    This is a mastapy class.
    '''

    TYPE = _WHINE_WATERFALL_REFERENCE_VALUES_BASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WhineWaterfallReferenceValuesBase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def minimum_db(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MinimumDB' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MinimumDB) if self.wrapped.MinimumDB is not None else None

    @minimum_db.setter
    def minimum_db(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MinimumDB = value

    @property
    def maximum_db(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MaximumDB' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MaximumDB) if self.wrapped.MaximumDB is not None else None

    @maximum_db.setter
    def maximum_db(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MaximumDB = value
