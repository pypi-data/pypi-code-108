'''_4184.py

BeltDriveCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2316, _2326
from mastapy._internal import constructor, conversion
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4037
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4272
from mastapy._internal.python_net import python_net_import

_BELT_DRIVE_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'BeltDriveCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('BeltDriveCompoundParametricStudyTool',)


class BeltDriveCompoundParametricStudyTool(_4272.SpecialisedAssemblyCompoundParametricStudyTool):
    '''BeltDriveCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _BELT_DRIVE_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BeltDriveCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2316.BeltDrive':
        '''BeltDrive: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2316.BeltDrive.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to BeltDrive. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2316.BeltDrive':
        '''BeltDrive: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2316.BeltDrive.TYPE not in self.wrapped.AssemblyDesign.__class__.__mro__:
            raise CastException('Failed to cast assembly_design to BeltDrive. Expected: {}.'.format(self.wrapped.AssemblyDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AssemblyDesign.__class__)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_4037.BeltDriveParametricStudyTool]':
        '''List[BeltDriveParametricStudyTool]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_4037.BeltDriveParametricStudyTool))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_4037.BeltDriveParametricStudyTool]':
        '''List[BeltDriveParametricStudyTool]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_4037.BeltDriveParametricStudyTool))
        return value
