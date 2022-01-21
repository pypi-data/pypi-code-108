'''_1948.py

MastaSettings
'''


from mastapy.bearings.bearing_results.rolling import _1728
from mastapy._internal import constructor
from mastapy.bearings import _1638, _1650
from mastapy.bolts import _1267, _1269, _1274
from mastapy.cycloidal import _1256, _1262
from mastapy.gears import _282, _283, _309
from mastapy.gears.gear_designs.cylindrical import (
    _968, _972, _973, _974
)
from mastapy.gears.gear_designs import _902, _908
from mastapy.gears.gear_set_pareto_optimiser import (
    _880, _881, _884, _885,
    _887, _888, _890, _891,
    _893, _894, _895, _896
)
from mastapy.gears.ltca.cylindrical import _815
from mastapy.gears.manufacturing.bevel import _760
from mastapy.gears.manufacturing.cylindrical.cutters import (
    _683, _689, _694, _695
)
from mastapy.gears.manufacturing.cylindrical import _575, _586
from mastapy.gears.materials import (
    _546, _548, _549, _550,
    _553, _556, _559, _560,
    _567
)
from mastapy.gears.rating.cylindrical import _425, _432
from mastapy.materials import (
    _218, _219, _238, _241
)
from mastapy.nodal_analysis import _45, _46, _64
from mastapy.nodal_analysis.geometry_modeller_link import _148
from mastapy.shafts import _25, _37
from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6298
from mastapy.system_model.analyses_and_results.harmonic_analyses import _5743
from mastapy.system_model.analyses_and_results.mbd_analyses import _5186
from mastapy.system_model.analyses_and_results.modal_analyses import _4900
from mastapy.system_model.analyses_and_results.power_flows import _3854, _3812
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.stability_analyses import _3604
from mastapy.system_model.analyses_and_results.static_loads import _6586
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses import _3343
from mastapy.system_model.analyses_and_results.system_deflections import _2561
from mastapy.system_model.drawing import _1993
from mastapy.system_model.optimization import _1973, _1982
from mastapy.system_model.part_model.gears.supercharger_rotor_set import _2304
from mastapy.system_model.part_model import _2211
from mastapy.utility.cad_export import _1600
from mastapy.utility.databases import _1595
from mastapy.utility import _1389, _1390
from mastapy.utility.scripting import _1513
from mastapy.utility.units_and_measurements import _1399
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_MASTA_SETTINGS = python_net_import('SMT.MastaAPI.SystemModel', 'MastaSettings')


__docformat__ = 'restructuredtext en'
__all__ = ('MastaSettings',)


class MastaSettings(_0.APIBase):
    '''MastaSettings

    This is a mastapy class.
    '''

    TYPE = _MASTA_SETTINGS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MastaSettings.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def iso14179_settings_database(self) -> '_1728.ISO14179SettingsDatabase':
        '''ISO14179SettingsDatabase: 'ISO14179SettingsDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1728.ISO14179SettingsDatabase)(self.wrapped.ISO14179SettingsDatabase) if self.wrapped.ISO14179SettingsDatabase is not None else None

    @property
    def bearing_settings(self) -> '_1638.BearingSettings':
        '''BearingSettings: 'BearingSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1638.BearingSettings)(self.wrapped.BearingSettings) if self.wrapped.BearingSettings is not None else None

    @property
    def rolling_bearing_database(self) -> '_1650.RollingBearingDatabase':
        '''RollingBearingDatabase: 'RollingBearingDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1650.RollingBearingDatabase)(self.wrapped.RollingBearingDatabase) if self.wrapped.RollingBearingDatabase is not None else None

    @property
    def bolt_geometry_database(self) -> '_1267.BoltGeometryDatabase':
        '''BoltGeometryDatabase: 'BoltGeometryDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1267.BoltGeometryDatabase)(self.wrapped.BoltGeometryDatabase) if self.wrapped.BoltGeometryDatabase is not None else None

    @property
    def bolt_material_database(self) -> '_1269.BoltMaterialDatabase':
        '''BoltMaterialDatabase: 'BoltMaterialDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1269.BoltMaterialDatabase)(self.wrapped.BoltMaterialDatabase) if self.wrapped.BoltMaterialDatabase is not None else None

    @property
    def clamped_section_material_database(self) -> '_1274.ClampedSectionMaterialDatabase':
        '''ClampedSectionMaterialDatabase: 'ClampedSectionMaterialDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1274.ClampedSectionMaterialDatabase)(self.wrapped.ClampedSectionMaterialDatabase) if self.wrapped.ClampedSectionMaterialDatabase is not None else None

    @property
    def cycloidal_disc_material_database(self) -> '_1256.CycloidalDiscMaterialDatabase':
        '''CycloidalDiscMaterialDatabase: 'CycloidalDiscMaterialDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1256.CycloidalDiscMaterialDatabase)(self.wrapped.CycloidalDiscMaterialDatabase) if self.wrapped.CycloidalDiscMaterialDatabase is not None else None

    @property
    def ring_pins_material_database(self) -> '_1262.RingPinsMaterialDatabase':
        '''RingPinsMaterialDatabase: 'RingPinsMaterialDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1262.RingPinsMaterialDatabase)(self.wrapped.RingPinsMaterialDatabase) if self.wrapped.RingPinsMaterialDatabase is not None else None

    @property
    def bevel_hypoid_gear_design_settings(self) -> '_282.BevelHypoidGearDesignSettings':
        '''BevelHypoidGearDesignSettings: 'BevelHypoidGearDesignSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_282.BevelHypoidGearDesignSettings)(self.wrapped.BevelHypoidGearDesignSettings) if self.wrapped.BevelHypoidGearDesignSettings is not None else None

    @property
    def bevel_hypoid_gear_rating_settings(self) -> '_283.BevelHypoidGearRatingSettings':
        '''BevelHypoidGearRatingSettings: 'BevelHypoidGearRatingSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_283.BevelHypoidGearRatingSettings)(self.wrapped.BevelHypoidGearRatingSettings) if self.wrapped.BevelHypoidGearRatingSettings is not None else None

    @property
    def cylindrical_gear_defaults(self) -> '_968.CylindricalGearDefaults':
        '''CylindricalGearDefaults: 'CylindricalGearDefaults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_968.CylindricalGearDefaults)(self.wrapped.CylindricalGearDefaults) if self.wrapped.CylindricalGearDefaults is not None else None

    @property
    def cylindrical_gear_design_constraints_database(self) -> '_972.CylindricalGearDesignConstraintsDatabase':
        '''CylindricalGearDesignConstraintsDatabase: 'CylindricalGearDesignConstraintsDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_972.CylindricalGearDesignConstraintsDatabase)(self.wrapped.CylindricalGearDesignConstraintsDatabase) if self.wrapped.CylindricalGearDesignConstraintsDatabase is not None else None

    @property
    def cylindrical_gear_design_constraint_settings(self) -> '_973.CylindricalGearDesignConstraintSettings':
        '''CylindricalGearDesignConstraintSettings: 'CylindricalGearDesignConstraintSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_973.CylindricalGearDesignConstraintSettings)(self.wrapped.CylindricalGearDesignConstraintSettings) if self.wrapped.CylindricalGearDesignConstraintSettings is not None else None

    @property
    def cylindrical_gear_design_settings(self) -> '_974.CylindricalGearDesignSettings':
        '''CylindricalGearDesignSettings: 'CylindricalGearDesignSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_974.CylindricalGearDesignSettings)(self.wrapped.CylindricalGearDesignSettings) if self.wrapped.CylindricalGearDesignSettings is not None else None

    @property
    def design_constraint_collection_database(self) -> '_902.DesignConstraintCollectionDatabase':
        '''DesignConstraintCollectionDatabase: 'DesignConstraintCollectionDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_902.DesignConstraintCollectionDatabase)(self.wrapped.DesignConstraintCollectionDatabase) if self.wrapped.DesignConstraintCollectionDatabase is not None else None

    @property
    def selected_design_constraints_collection(self) -> '_908.SelectedDesignConstraintsCollection':
        '''SelectedDesignConstraintsCollection: 'SelectedDesignConstraintsCollection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_908.SelectedDesignConstraintsCollection)(self.wrapped.SelectedDesignConstraintsCollection) if self.wrapped.SelectedDesignConstraintsCollection is not None else None

    @property
    def micro_geometry_gear_set_design_space_search_strategy_database(self) -> '_880.MicroGeometryGearSetDesignSpaceSearchStrategyDatabase':
        '''MicroGeometryGearSetDesignSpaceSearchStrategyDatabase: 'MicroGeometryGearSetDesignSpaceSearchStrategyDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_880.MicroGeometryGearSetDesignSpaceSearchStrategyDatabase)(self.wrapped.MicroGeometryGearSetDesignSpaceSearchStrategyDatabase) if self.wrapped.MicroGeometryGearSetDesignSpaceSearchStrategyDatabase is not None else None

    @property
    def micro_geometry_gear_set_duty_cycle_design_space_search_strategy_database(self) -> '_881.MicroGeometryGearSetDutyCycleDesignSpaceSearchStrategyDatabase':
        '''MicroGeometryGearSetDutyCycleDesignSpaceSearchStrategyDatabase: 'MicroGeometryGearSetDutyCycleDesignSpaceSearchStrategyDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_881.MicroGeometryGearSetDutyCycleDesignSpaceSearchStrategyDatabase)(self.wrapped.MicroGeometryGearSetDutyCycleDesignSpaceSearchStrategyDatabase) if self.wrapped.MicroGeometryGearSetDutyCycleDesignSpaceSearchStrategyDatabase is not None else None

    @property
    def pareto_cylindrical_gear_set_duty_cycle_optimisation_strategy_database(self) -> '_884.ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase':
        '''ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase: 'ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_884.ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase)(self.wrapped.ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase) if self.wrapped.ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase is not None else None

    @property
    def pareto_cylindrical_gear_set_optimisation_strategy_database(self) -> '_885.ParetoCylindricalGearSetOptimisationStrategyDatabase':
        '''ParetoCylindricalGearSetOptimisationStrategyDatabase: 'ParetoCylindricalGearSetOptimisationStrategyDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_885.ParetoCylindricalGearSetOptimisationStrategyDatabase)(self.wrapped.ParetoCylindricalGearSetOptimisationStrategyDatabase) if self.wrapped.ParetoCylindricalGearSetOptimisationStrategyDatabase is not None else None

    @property
    def pareto_face_gear_set_duty_cycle_optimisation_strategy_database(self) -> '_887.ParetoFaceGearSetDutyCycleOptimisationStrategyDatabase':
        '''ParetoFaceGearSetDutyCycleOptimisationStrategyDatabase: 'ParetoFaceGearSetDutyCycleOptimisationStrategyDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_887.ParetoFaceGearSetDutyCycleOptimisationStrategyDatabase)(self.wrapped.ParetoFaceGearSetDutyCycleOptimisationStrategyDatabase) if self.wrapped.ParetoFaceGearSetDutyCycleOptimisationStrategyDatabase is not None else None

    @property
    def pareto_face_gear_set_optimisation_strategy_database(self) -> '_888.ParetoFaceGearSetOptimisationStrategyDatabase':
        '''ParetoFaceGearSetOptimisationStrategyDatabase: 'ParetoFaceGearSetOptimisationStrategyDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_888.ParetoFaceGearSetOptimisationStrategyDatabase)(self.wrapped.ParetoFaceGearSetOptimisationStrategyDatabase) if self.wrapped.ParetoFaceGearSetOptimisationStrategyDatabase is not None else None

    @property
    def pareto_hypoid_gear_set_duty_cycle_optimisation_strategy_database(self) -> '_890.ParetoHypoidGearSetDutyCycleOptimisationStrategyDatabase':
        '''ParetoHypoidGearSetDutyCycleOptimisationStrategyDatabase: 'ParetoHypoidGearSetDutyCycleOptimisationStrategyDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_890.ParetoHypoidGearSetDutyCycleOptimisationStrategyDatabase)(self.wrapped.ParetoHypoidGearSetDutyCycleOptimisationStrategyDatabase) if self.wrapped.ParetoHypoidGearSetDutyCycleOptimisationStrategyDatabase is not None else None

    @property
    def pareto_hypoid_gear_set_optimisation_strategy_database(self) -> '_891.ParetoHypoidGearSetOptimisationStrategyDatabase':
        '''ParetoHypoidGearSetOptimisationStrategyDatabase: 'ParetoHypoidGearSetOptimisationStrategyDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_891.ParetoHypoidGearSetOptimisationStrategyDatabase)(self.wrapped.ParetoHypoidGearSetOptimisationStrategyDatabase) if self.wrapped.ParetoHypoidGearSetOptimisationStrategyDatabase is not None else None

    @property
    def pareto_spiral_bevel_gear_set_duty_cycle_optimisation_strategy_database(self) -> '_893.ParetoSpiralBevelGearSetDutyCycleOptimisationStrategyDatabase':
        '''ParetoSpiralBevelGearSetDutyCycleOptimisationStrategyDatabase: 'ParetoSpiralBevelGearSetDutyCycleOptimisationStrategyDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_893.ParetoSpiralBevelGearSetDutyCycleOptimisationStrategyDatabase)(self.wrapped.ParetoSpiralBevelGearSetDutyCycleOptimisationStrategyDatabase) if self.wrapped.ParetoSpiralBevelGearSetDutyCycleOptimisationStrategyDatabase is not None else None

    @property
    def pareto_spiral_bevel_gear_set_optimisation_strategy_database(self) -> '_894.ParetoSpiralBevelGearSetOptimisationStrategyDatabase':
        '''ParetoSpiralBevelGearSetOptimisationStrategyDatabase: 'ParetoSpiralBevelGearSetOptimisationStrategyDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_894.ParetoSpiralBevelGearSetOptimisationStrategyDatabase)(self.wrapped.ParetoSpiralBevelGearSetOptimisationStrategyDatabase) if self.wrapped.ParetoSpiralBevelGearSetOptimisationStrategyDatabase is not None else None

    @property
    def pareto_straight_bevel_gear_set_duty_cycle_optimisation_strategy_database(self) -> '_895.ParetoStraightBevelGearSetDutyCycleOptimisationStrategyDatabase':
        '''ParetoStraightBevelGearSetDutyCycleOptimisationStrategyDatabase: 'ParetoStraightBevelGearSetDutyCycleOptimisationStrategyDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_895.ParetoStraightBevelGearSetDutyCycleOptimisationStrategyDatabase)(self.wrapped.ParetoStraightBevelGearSetDutyCycleOptimisationStrategyDatabase) if self.wrapped.ParetoStraightBevelGearSetDutyCycleOptimisationStrategyDatabase is not None else None

    @property
    def pareto_straight_bevel_gear_set_optimisation_strategy_database(self) -> '_896.ParetoStraightBevelGearSetOptimisationStrategyDatabase':
        '''ParetoStraightBevelGearSetOptimisationStrategyDatabase: 'ParetoStraightBevelGearSetOptimisationStrategyDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_896.ParetoStraightBevelGearSetOptimisationStrategyDatabase)(self.wrapped.ParetoStraightBevelGearSetOptimisationStrategyDatabase) if self.wrapped.ParetoStraightBevelGearSetOptimisationStrategyDatabase is not None else None

    @property
    def cylindrical_gear_fe_settings(self) -> '_815.CylindricalGearFESettings':
        '''CylindricalGearFESettings: 'CylindricalGearFESettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_815.CylindricalGearFESettings)(self.wrapped.CylindricalGearFESettings) if self.wrapped.CylindricalGearFESettings is not None else None

    @property
    def manufacturing_machine_database(self) -> '_760.ManufacturingMachineDatabase':
        '''ManufacturingMachineDatabase: 'ManufacturingMachineDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_760.ManufacturingMachineDatabase)(self.wrapped.ManufacturingMachineDatabase) if self.wrapped.ManufacturingMachineDatabase is not None else None

    @property
    def cylindrical_formed_wheel_grinder_database(self) -> '_683.CylindricalFormedWheelGrinderDatabase':
        '''CylindricalFormedWheelGrinderDatabase: 'CylindricalFormedWheelGrinderDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_683.CylindricalFormedWheelGrinderDatabase)(self.wrapped.CylindricalFormedWheelGrinderDatabase) if self.wrapped.CylindricalFormedWheelGrinderDatabase is not None else None

    @property
    def cylindrical_gear_plunge_shaver_database(self) -> '_689.CylindricalGearPlungeShaverDatabase':
        '''CylindricalGearPlungeShaverDatabase: 'CylindricalGearPlungeShaverDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_689.CylindricalGearPlungeShaverDatabase)(self.wrapped.CylindricalGearPlungeShaverDatabase) if self.wrapped.CylindricalGearPlungeShaverDatabase is not None else None

    @property
    def cylindrical_gear_shaver_database(self) -> '_694.CylindricalGearShaverDatabase':
        '''CylindricalGearShaverDatabase: 'CylindricalGearShaverDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_694.CylindricalGearShaverDatabase)(self.wrapped.CylindricalGearShaverDatabase) if self.wrapped.CylindricalGearShaverDatabase is not None else None

    @property
    def cylindrical_worm_grinder_database(self) -> '_695.CylindricalWormGrinderDatabase':
        '''CylindricalWormGrinderDatabase: 'CylindricalWormGrinderDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_695.CylindricalWormGrinderDatabase)(self.wrapped.CylindricalWormGrinderDatabase) if self.wrapped.CylindricalWormGrinderDatabase is not None else None

    @property
    def cylindrical_hob_database(self) -> '_575.CylindricalHobDatabase':
        '''CylindricalHobDatabase: 'CylindricalHobDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_575.CylindricalHobDatabase)(self.wrapped.CylindricalHobDatabase) if self.wrapped.CylindricalHobDatabase is not None else None

    @property
    def cylindrical_shaper_database(self) -> '_586.CylindricalShaperDatabase':
        '''CylindricalShaperDatabase: 'CylindricalShaperDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_586.CylindricalShaperDatabase)(self.wrapped.CylindricalShaperDatabase) if self.wrapped.CylindricalShaperDatabase is not None else None

    @property
    def bevel_gear_iso_material_database(self) -> '_546.BevelGearIsoMaterialDatabase':
        '''BevelGearIsoMaterialDatabase: 'BevelGearIsoMaterialDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_546.BevelGearIsoMaterialDatabase)(self.wrapped.BevelGearIsoMaterialDatabase) if self.wrapped.BevelGearIsoMaterialDatabase is not None else None

    @property
    def bevel_gear_material_database(self) -> '_548.BevelGearMaterialDatabase':
        '''BevelGearMaterialDatabase: 'BevelGearMaterialDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_548.BevelGearMaterialDatabase)(self.wrapped.BevelGearMaterialDatabase) if self.wrapped.BevelGearMaterialDatabase is not None else None

    @property
    def cylindrical_gear_agma_material_database(self) -> '_549.CylindricalGearAGMAMaterialDatabase':
        '''CylindricalGearAGMAMaterialDatabase: 'CylindricalGearAGMAMaterialDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_549.CylindricalGearAGMAMaterialDatabase)(self.wrapped.CylindricalGearAGMAMaterialDatabase) if self.wrapped.CylindricalGearAGMAMaterialDatabase is not None else None

    @property
    def cylindrical_gear_iso_material_database(self) -> '_550.CylindricalGearISOMaterialDatabase':
        '''CylindricalGearISOMaterialDatabase: 'CylindricalGearISOMaterialDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_550.CylindricalGearISOMaterialDatabase)(self.wrapped.CylindricalGearISOMaterialDatabase) if self.wrapped.CylindricalGearISOMaterialDatabase is not None else None

    @property
    def cylindrical_gear_plastic_material_database(self) -> '_553.CylindricalGearPlasticMaterialDatabase':
        '''CylindricalGearPlasticMaterialDatabase: 'CylindricalGearPlasticMaterialDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_553.CylindricalGearPlasticMaterialDatabase)(self.wrapped.CylindricalGearPlasticMaterialDatabase) if self.wrapped.CylindricalGearPlasticMaterialDatabase is not None else None

    @property
    def gear_material_expert_system_factor_settings(self) -> '_556.GearMaterialExpertSystemFactorSettings':
        '''GearMaterialExpertSystemFactorSettings: 'GearMaterialExpertSystemFactorSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_556.GearMaterialExpertSystemFactorSettings)(self.wrapped.GearMaterialExpertSystemFactorSettings) if self.wrapped.GearMaterialExpertSystemFactorSettings is not None else None

    @property
    def isotr1417912001_coefficient_of_friction_constants_database(self) -> '_559.ISOTR1417912001CoefficientOfFrictionConstantsDatabase':
        '''ISOTR1417912001CoefficientOfFrictionConstantsDatabase: 'ISOTR1417912001CoefficientOfFrictionConstantsDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_559.ISOTR1417912001CoefficientOfFrictionConstantsDatabase)(self.wrapped.ISOTR1417912001CoefficientOfFrictionConstantsDatabase) if self.wrapped.ISOTR1417912001CoefficientOfFrictionConstantsDatabase is not None else None

    @property
    def klingelnberg_conical_gear_material_database(self) -> '_560.KlingelnbergConicalGearMaterialDatabase':
        '''KlingelnbergConicalGearMaterialDatabase: 'KlingelnbergConicalGearMaterialDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_560.KlingelnbergConicalGearMaterialDatabase)(self.wrapped.KlingelnbergConicalGearMaterialDatabase) if self.wrapped.KlingelnbergConicalGearMaterialDatabase is not None else None

    @property
    def raw_material_database(self) -> '_567.RawMaterialDatabase':
        '''RawMaterialDatabase: 'RawMaterialDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_567.RawMaterialDatabase)(self.wrapped.RawMaterialDatabase) if self.wrapped.RawMaterialDatabase is not None else None

    @property
    def pocketing_power_loss_coefficients_database(self) -> '_309.PocketingPowerLossCoefficientsDatabase':
        '''PocketingPowerLossCoefficientsDatabase: 'PocketingPowerLossCoefficientsDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_309.PocketingPowerLossCoefficientsDatabase)(self.wrapped.PocketingPowerLossCoefficientsDatabase) if self.wrapped.PocketingPowerLossCoefficientsDatabase is not None else None

    @property
    def cylindrical_gear_rating_settings(self) -> '_425.CylindricalGearRatingSettings':
        '''CylindricalGearRatingSettings: 'CylindricalGearRatingSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_425.CylindricalGearRatingSettings)(self.wrapped.CylindricalGearRatingSettings) if self.wrapped.CylindricalGearRatingSettings is not None else None

    @property
    def cylindrical_plastic_gear_rating_settings(self) -> '_432.CylindricalPlasticGearRatingSettings':
        '''CylindricalPlasticGearRatingSettings: 'CylindricalPlasticGearRatingSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_432.CylindricalPlasticGearRatingSettings)(self.wrapped.CylindricalPlasticGearRatingSettings) if self.wrapped.CylindricalPlasticGearRatingSettings is not None else None

    @property
    def bearing_material_database(self) -> '_218.BearingMaterialDatabase':
        '''BearingMaterialDatabase: 'BearingMaterialDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_218.BearingMaterialDatabase)(self.wrapped.BearingMaterialDatabase) if self.wrapped.BearingMaterialDatabase is not None else None

    @property
    def component_material_database(self) -> '_219.ComponentMaterialDatabase':
        '''ComponentMaterialDatabase: 'ComponentMaterialDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_219.ComponentMaterialDatabase)(self.wrapped.ComponentMaterialDatabase) if self.wrapped.ComponentMaterialDatabase is not None else None

    @property
    def lubrication_detail_database(self) -> '_238.LubricationDetailDatabase':
        '''LubricationDetailDatabase: 'LubricationDetailDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_238.LubricationDetailDatabase)(self.wrapped.LubricationDetailDatabase) if self.wrapped.LubricationDetailDatabase is not None else None

    @property
    def materials_settings(self) -> '_241.MaterialsSettings':
        '''MaterialsSettings: 'MaterialsSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_241.MaterialsSettings)(self.wrapped.MaterialsSettings) if self.wrapped.MaterialsSettings is not None else None

    @property
    def analysis_settings(self) -> '_45.AnalysisSettings':
        '''AnalysisSettings: 'AnalysisSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_45.AnalysisSettings)(self.wrapped.AnalysisSettings) if self.wrapped.AnalysisSettings is not None else None

    @property
    def analysis_settings_database(self) -> '_46.AnalysisSettingsDatabase':
        '''AnalysisSettingsDatabase: 'AnalysisSettingsDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_46.AnalysisSettingsDatabase)(self.wrapped.AnalysisSettingsDatabase) if self.wrapped.AnalysisSettingsDatabase is not None else None

    @property
    def fe_user_settings(self) -> '_64.FEUserSettings':
        '''FEUserSettings: 'FEUserSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_64.FEUserSettings)(self.wrapped.FEUserSettings) if self.wrapped.FEUserSettings is not None else None

    @property
    def geometry_modeller_settings(self) -> '_148.GeometryModellerSettings':
        '''GeometryModellerSettings: 'GeometryModellerSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_148.GeometryModellerSettings)(self.wrapped.GeometryModellerSettings) if self.wrapped.GeometryModellerSettings is not None else None

    @property
    def shaft_material_database(self) -> '_25.ShaftMaterialDatabase':
        '''ShaftMaterialDatabase: 'ShaftMaterialDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_25.ShaftMaterialDatabase)(self.wrapped.ShaftMaterialDatabase) if self.wrapped.ShaftMaterialDatabase is not None else None

    @property
    def shaft_settings(self) -> '_37.ShaftSettings':
        '''ShaftSettings: 'ShaftSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_37.ShaftSettings)(self.wrapped.ShaftSettings) if self.wrapped.ShaftSettings is not None else None

    @property
    def critical_speed_analysis_draw_style(self) -> '_6298.CriticalSpeedAnalysisDrawStyle':
        '''CriticalSpeedAnalysisDrawStyle: 'CriticalSpeedAnalysisDrawStyle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6298.CriticalSpeedAnalysisDrawStyle)(self.wrapped.CriticalSpeedAnalysisDrawStyle) if self.wrapped.CriticalSpeedAnalysisDrawStyle is not None else None

    @property
    def harmonic_analysis_draw_style(self) -> '_5743.HarmonicAnalysisDrawStyle':
        '''HarmonicAnalysisDrawStyle: 'HarmonicAnalysisDrawStyle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5743.HarmonicAnalysisDrawStyle)(self.wrapped.HarmonicAnalysisDrawStyle) if self.wrapped.HarmonicAnalysisDrawStyle is not None else None

    @property
    def mbd_analysis_draw_style(self) -> '_5186.MBDAnalysisDrawStyle':
        '''MBDAnalysisDrawStyle: 'MBDAnalysisDrawStyle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5186.MBDAnalysisDrawStyle)(self.wrapped.MBDAnalysisDrawStyle) if self.wrapped.MBDAnalysisDrawStyle is not None else None

    @property
    def modal_analysis_draw_style(self) -> '_4900.ModalAnalysisDrawStyle':
        '''ModalAnalysisDrawStyle: 'ModalAnalysisDrawStyle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_4900.ModalAnalysisDrawStyle)(self.wrapped.ModalAnalysisDrawStyle) if self.wrapped.ModalAnalysisDrawStyle is not None else None

    @property
    def power_flow_draw_style(self) -> '_3854.PowerFlowDrawStyle':
        '''PowerFlowDrawStyle: 'PowerFlowDrawStyle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _3854.PowerFlowDrawStyle.TYPE not in self.wrapped.PowerFlowDrawStyle.__class__.__mro__:
            raise CastException('Failed to cast power_flow_draw_style to PowerFlowDrawStyle. Expected: {}.'.format(self.wrapped.PowerFlowDrawStyle.__class__.__qualname__))

        return constructor.new_override(self.wrapped.PowerFlowDrawStyle.__class__)(self.wrapped.PowerFlowDrawStyle) if self.wrapped.PowerFlowDrawStyle is not None else None

    @property
    def stability_analysis_draw_style(self) -> '_3604.StabilityAnalysisDrawStyle':
        '''StabilityAnalysisDrawStyle: 'StabilityAnalysisDrawStyle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_3604.StabilityAnalysisDrawStyle)(self.wrapped.StabilityAnalysisDrawStyle) if self.wrapped.StabilityAnalysisDrawStyle is not None else None

    @property
    def electric_machine_detail_database(self) -> '_6586.ElectricMachineDetailDatabase':
        '''ElectricMachineDetailDatabase: 'ElectricMachineDetailDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6586.ElectricMachineDetailDatabase)(self.wrapped.ElectricMachineDetailDatabase) if self.wrapped.ElectricMachineDetailDatabase is not None else None

    @property
    def steady_state_synchronous_response_draw_style(self) -> '_3343.SteadyStateSynchronousResponseDrawStyle':
        '''SteadyStateSynchronousResponseDrawStyle: 'SteadyStateSynchronousResponseDrawStyle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_3343.SteadyStateSynchronousResponseDrawStyle)(self.wrapped.SteadyStateSynchronousResponseDrawStyle) if self.wrapped.SteadyStateSynchronousResponseDrawStyle is not None else None

    @property
    def system_deflection_draw_style(self) -> '_2561.SystemDeflectionDrawStyle':
        '''SystemDeflectionDrawStyle: 'SystemDeflectionDrawStyle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2561.SystemDeflectionDrawStyle)(self.wrapped.SystemDeflectionDrawStyle) if self.wrapped.SystemDeflectionDrawStyle is not None else None

    @property
    def model_view_options_draw_style(self) -> '_1993.ModelViewOptionsDrawStyle':
        '''ModelViewOptionsDrawStyle: 'ModelViewOptionsDrawStyle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1993.ModelViewOptionsDrawStyle)(self.wrapped.ModelViewOptionsDrawStyle) if self.wrapped.ModelViewOptionsDrawStyle is not None else None

    @property
    def conical_gear_optimization_strategy_database(self) -> '_1973.ConicalGearOptimizationStrategyDatabase':
        '''ConicalGearOptimizationStrategyDatabase: 'ConicalGearOptimizationStrategyDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1973.ConicalGearOptimizationStrategyDatabase)(self.wrapped.ConicalGearOptimizationStrategyDatabase) if self.wrapped.ConicalGearOptimizationStrategyDatabase is not None else None

    @property
    def optimization_strategy_database(self) -> '_1982.OptimizationStrategyDatabase':
        '''OptimizationStrategyDatabase: 'OptimizationStrategyDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1982.OptimizationStrategyDatabase)(self.wrapped.OptimizationStrategyDatabase) if self.wrapped.OptimizationStrategyDatabase is not None else None

    @property
    def supercharger_rotor_set_database(self) -> '_2304.SuperchargerRotorSetDatabase':
        '''SuperchargerRotorSetDatabase: 'SuperchargerRotorSetDatabase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2304.SuperchargerRotorSetDatabase)(self.wrapped.SuperchargerRotorSetDatabase) if self.wrapped.SuperchargerRotorSetDatabase is not None else None

    @property
    def planet_carrier_settings(self) -> '_2211.PlanetCarrierSettings':
        '''PlanetCarrierSettings: 'PlanetCarrierSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2211.PlanetCarrierSettings)(self.wrapped.PlanetCarrierSettings) if self.wrapped.PlanetCarrierSettings is not None else None

    @property
    def cad_export_settings(self) -> '_1600.CADExportSettings':
        '''CADExportSettings: 'CADExportSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1600.CADExportSettings)(self.wrapped.CADExportSettings) if self.wrapped.CADExportSettings is not None else None

    @property
    def database_settings(self) -> '_1595.DatabaseSettings':
        '''DatabaseSettings: 'DatabaseSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1595.DatabaseSettings)(self.wrapped.DatabaseSettings) if self.wrapped.DatabaseSettings is not None else None

    @property
    def program_settings(self) -> '_1389.ProgramSettings':
        '''ProgramSettings: 'ProgramSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1389.ProgramSettings)(self.wrapped.ProgramSettings) if self.wrapped.ProgramSettings is not None else None

    @property
    def pushbullet_settings(self) -> '_1390.PushbulletSettings':
        '''PushbulletSettings: 'PushbulletSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1390.PushbulletSettings)(self.wrapped.PushbulletSettings) if self.wrapped.PushbulletSettings is not None else None

    @property
    def scripting_setup(self) -> '_1513.ScriptingSetup':
        '''ScriptingSetup: 'ScriptingSetup' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1513.ScriptingSetup)(self.wrapped.ScriptingSetup) if self.wrapped.ScriptingSetup is not None else None

    @property
    def measurement_settings(self) -> '_1399.MeasurementSettings':
        '''MeasurementSettings: 'MeasurementSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1399.MeasurementSettings)(self.wrapped.MeasurementSettings) if self.wrapped.MeasurementSettings is not None else None
