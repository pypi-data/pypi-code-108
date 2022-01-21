'''_820.py

CylindricalGearSetLoadDistributionAnalysis
'''


from typing import List

from mastapy.gears.rating.cylindrical import _428
from mastapy._internal import constructor, conversion
from mastapy.gears.gear_two_d_fe_analysis import _856
from mastapy.gears.ltca.cylindrical import _817
from mastapy.gears.ltca import _806
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_SET_LOAD_DISTRIBUTION_ANALYSIS = python_net_import('SMT.MastaAPI.Gears.LTCA.Cylindrical', 'CylindricalGearSetLoadDistributionAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearSetLoadDistributionAnalysis',)


class CylindricalGearSetLoadDistributionAnalysis(_806.GearSetLoadDistributionAnalysis):
    '''CylindricalGearSetLoadDistributionAnalysis

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_SET_LOAD_DISTRIBUTION_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearSetLoadDistributionAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def rating(self) -> '_428.CylindricalGearSetRating':
        '''CylindricalGearSetRating: 'Rating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_428.CylindricalGearSetRating)(self.wrapped.Rating) if self.wrapped.Rating is not None else None

    @property
    def tiff_analysis(self) -> '_856.CylindricalGearSetTIFFAnalysis':
        '''CylindricalGearSetTIFFAnalysis: 'TIFFAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_856.CylindricalGearSetTIFFAnalysis)(self.wrapped.TIFFAnalysis) if self.wrapped.TIFFAnalysis is not None else None

    @property
    def meshes(self) -> 'List[_817.CylindricalGearMeshLoadDistributionAnalysis]':
        '''List[CylindricalGearMeshLoadDistributionAnalysis]: 'Meshes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Meshes, constructor.new(_817.CylindricalGearMeshLoadDistributionAnalysis))
        return value
