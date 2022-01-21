'''_4156.py

StraightBevelPlanetGearParametricStudyTool
'''


from mastapy.system_model.part_model.gears import _2289
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4151
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_PLANET_GEAR_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools', 'StraightBevelPlanetGearParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelPlanetGearParametricStudyTool',)


class StraightBevelPlanetGearParametricStudyTool(_4151.StraightBevelDiffGearParametricStudyTool):
    '''StraightBevelPlanetGearParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_PLANET_GEAR_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelPlanetGearParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2289.StraightBevelPlanetGear':
        '''StraightBevelPlanetGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2289.StraightBevelPlanetGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None
