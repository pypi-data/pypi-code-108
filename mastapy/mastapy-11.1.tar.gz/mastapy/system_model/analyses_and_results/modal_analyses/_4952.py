'''_4952.py

WhineWaterfallReferenceValues
'''


from typing import Generic, TypeVar

from mastapy._internal import constructor
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.system_model.analyses_and_results.modal_analyses import _4953
from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_WHINE_WATERFALL_REFERENCE_VALUES = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses', 'WhineWaterfallReferenceValues')


__docformat__ = 'restructuredtext en'
__all__ = ('WhineWaterfallReferenceValues',)


TMeasurement = TypeVar('TMeasurement', bound='_1398.MeasurementBase')


class WhineWaterfallReferenceValues(_4953.WhineWaterfallReferenceValuesBase, Generic[TMeasurement]):
    '''WhineWaterfallReferenceValues

    This is a mastapy class.

    Generic Types:
        TMeasurement
    '''

    TYPE = _WHINE_WATERFALL_REFERENCE_VALUES

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WhineWaterfallReferenceValues.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def decibel_reference(self) -> 'float':
        '''float: 'DecibelReference' is the original name of this property.'''

        return self.wrapped.DecibelReference

    @decibel_reference.setter
    def decibel_reference(self, value: 'float'):
        self.wrapped.DecibelReference = float(value) if value else 0.0

    @property
    def minimum(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'Minimum' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.Minimum) if self.wrapped.Minimum is not None else None

    @minimum.setter
    def minimum(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.Minimum = value

    @property
    def maximum(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'Maximum' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.Maximum) if self.wrapped.Maximum is not None else None

    @maximum.setter
    def maximum(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.Maximum = value
