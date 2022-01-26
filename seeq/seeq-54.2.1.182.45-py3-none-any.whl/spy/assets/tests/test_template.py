import json
import re

import numpy as np
import pytest

from seeq import spy
from seeq.spy.assets import Asset, ItemGroup
from seeq.spy.assets._model import SPyRuntimeError
from seeq.spy.tests import test_common


def setup_module():
    test_common.initialize_sessions()


@pytest.mark.system
def test_missing_requirements():
    metadata_df = spy.search({
        'Path': 'Example >> Cooling Tower 1',
        'Asset': 'Area A'
    }, recursive=True, workbook=spy.GLOBALS_ONLY)

    spy.assets.prepare(metadata_df, root_asset_name='test_missing_requirements')

    # noinspection PyPep8Naming
    class HVAC_Missing_Property(Asset):
        @Asset.Requirement()
        def Missing_Prop(self, metadata):
            return {
                'Type': 'Property'
            }

    metadata_df['Build Template'] = 'HVAC_Missing_Property'
    with pytest.raises(SPyRuntimeError,
                       match=r'Requirement "Missing Prop" not found \(required by "HVAC_Missing_Property"\)'):
        spy.assets.build(HVAC_Missing_Property, metadata_df, errors='raise')

    build_df = spy.assets.build(HVAC_Missing_Property, metadata_df)
    status_df = build_df.spy.status.df

    assert len(build_df) == 0
    assert 'Requirement "Missing Prop" not found (required by "HVAC_Missing_Property")' in \
           status_df.iloc[0]['Build Result']

    # noinspection PyPep8Naming
    class HVAC_Missing_Attribute(Asset):
        @Asset.Requirement()
        def Missing_Attrib(self, metadata):
            return {
                'Type': 'Signal'
            }

    metadata_df['Build Template'] = 'HVAC_Missing_Attribute'
    with pytest.raises(SPyRuntimeError,
                       match=r'Requirement "Missing Attrib" not found \(required by "HVAC_Missing_Attribute"\)'):
        spy.assets.build(HVAC_Missing_Attribute, metadata_df, errors='raise')

    build_df = spy.assets.build(HVAC_Missing_Attribute, metadata_df)
    status_df = build_df.spy.status.df

    assert len(build_df) == 0
    assert 'Requirement "Missing Attrib" not found (required by "HVAC_Missing_Attribute")' in \
           status_df.iloc[0]['Build Result']

    # noinspection PyPep8Naming
    class HVAC_Missing_Optional_Parameter(Asset):
        @Asset.Requirement()
        def Missing_Optional_Requirement(self, metadata):
            return {
                'Type': 'Signal',
                'Optional': True
            }

        @Asset.Attribute()
        def Bad_Parameter(self, metadata):
            return {
                'Type': 'Signal',
                'Formula': '$missing',
                'Formula Parameters': {
                    '$missing': self.Missing_Optional_Requirement()
                }
            }

    metadata_df['Build Template'] = 'HVAC_Missing_Optional_Parameter'

    with pytest.raises(SPyRuntimeError, match=r'Formula Parameter "\$missing" not found\.'):
        spy.assets.build(HVAC_Missing_Optional_Parameter, metadata_df, errors='raise')


# noinspection PyPep8Naming
class HVAC_Monitoring_Requirements(Asset):

    @Asset.Requirement()
    def HVAC_Group(self, metadata):
        """
        An identifier for the group of HVACs that are all working in the same
        enclosure.
        """
        return {
            'Type': 'Property'
        }

    @Asset.Requirement()
    def Compressor_Power(self, metadata):
        """
        Compressor Power as measured at the power supply of the equipment
        itself.
        """
        return {
            'Type': 'Signal',
            'Unit Of Measure Family': 'kW'
        }

    @Asset.Requirement()
    def Compressor_Power_High_Limit(self, metadata):
        """
        The high power operating limit for the compressor
        """
        return {
            'Type': 'Property'
        }

    @Asset.Requirement()
    def Temperature_High_Limit(self, metadata):
        """
        The high temperature operating limit for the compressor
        """
        return {
            'Type': 'Scalar',
            'Unit Of Measure Family': 'F'
        }

    @Asset.Requirement()
    def Temperature(self, metadata):
        """
        The ambient *external* temperature as measured in a neutral location
        away from HVAC inlet/outlet sites.

        > Note that this value may be derived from equipment sensors with a
        > suitable coefficient to account for location bias.
        """
        return {
            'Type': 'Signal',
            'Unit Of Measure Family': 'F',
            'Optional': True
        }


# noinspection PyPep8Naming
class HVAC_Health_Monitoring(HVAC_Monitoring_Requirements):
    """
    Identifies conditions of poor or degraded health in all compressor types,
    including:

    * Karcher
    * Siemens
    * Johnson and Johnson
    """

    @Asset.Attribute()
    def Compressor_On_High(self, metadata):
        """
        Indicates that the compressor is about to blow. If other compressors are
        reporting low ambient temperature, then this HVAC's compressor power signal
        is ignored.
        """
        other_temperature_signals = ItemGroup([
            asset.Temperature() for asset in self.all_assets()
            if (asset is not self and isinstance(asset, HVAC_Monitoring_Requirements) and
                asset.HVAC_Group() == self.HVAC_Group())
        ])

        high_limit = self.Compressor_Power_High_Limit()
        if not high_limit:
            high_limit = '50 kW'

        if not self.Temperature_High_Limit():
            return None

        if len(other_temperature_signals) == 0:
            formula_parameters = {'$comp_pow': self.Compressor_Power()}
            formula = f'$comp_pow > {high_limit}'
        else:
            formula_parameters = other_temperature_signals.as_parameters()
            temperature_limits = ' and '.join([f'{p} < $temp_limit' for p in formula_parameters.keys()])
            formula_parameters['$comp_pow'] = self.Compressor_Power()
            formula_parameters['$temp_limit'] = self.Temperature_High_Limit()
            formula = f'$comp_pow > {high_limit} and ({temperature_limits})'

        return {
            'Type': 'Condition',
            'Formula': formula,
            'Formula Parameters': formula_parameters
        }


# noinspection PyPep8Naming
class HVAC_Health_Monitoring_RollUps(Asset):
    """
    Provides an overview of health of all compressors in the corresponding facility.
    """

    @Asset.Attribute()
    def At_Least_One_Compressor_On_High(self, metadata):
        """
        Indicates the at least one compressor in the facility is or has been operating outside of
        the manufacturer's specification.
        """
        return ItemGroup([
            asset.Compressor_On_High() for asset in self.all_assets()
            if isinstance(asset, HVAC_Health_Monitoring) and asset.is_descendant_of(self)
        ]).roll_up('union')

    @Asset.Requirement()
    def HVAC_Compressor_Health(self, metadata):
        return HVAC_Health_Monitoring


# noinspection PyPep8Naming
class HVAC_KPIs(
    HVAC_Health_Monitoring
):
    pass


# noinspection PyPep8Naming
class HVAC_RollUps(
    HVAC_Health_Monitoring_RollUps
):
    pass


@pytest.mark.system
def test_hvac_monitoring_template():
    metadata_df = spy.search({'Path': 'Example'},
                             recursive=True, workbook=spy.GLOBALS_ONLY)

    def _choose_template(_row):
        if re.match(r'.*Cooling Tower \d+$', _row['Name']):
            return 'HVAC_RollUps'
        elif _row['Asset'] == 'Example':
            return np.nan
        else:
            return 'HVAC_KPIs'

    metadata_df['Compressor Power High Limit'] = '35 kW'
    metadata_df.at[metadata_df['Name'] == 'Area B', 'Compressor Power High Limit'] = np.nan
    metadata_df.at[metadata_df['Name'] == 'Area C', 'Compressor Power High Limit'] = None
    metadata_df.at[metadata_df['Name'] == 'Area D', 'Compressor Power High Limit'] = '60 kW'

    metadata_df['Temperature High Limit'] = '70 F'
    metadata_df.at[metadata_df['Name'] == 'Area H', 'Temperature High Limit'] = np.nan
    metadata_df.at[metadata_df['Name'] == 'Area I', 'Temperature High Limit'] = None
    metadata_df.at[metadata_df['Name'] == 'Area J', 'Temperature High Limit'] = '60 F'

    # noinspection PyTypeChecker
    metadata_df['Build Template'] = metadata_df.apply(_choose_template, axis=1)
    spy.assets.prepare(metadata_df, root_asset_name='test_hvac_monitoring_template')

    try:
        spy.assets.build([HVAC_KPIs, HVAC_RollUps], metadata_df, errors='raise')
        assert False, 'No exception raised'
    except SPyRuntimeError as e:
        assert 'Requirement "Compressor Power High Limit" not found' in str(e)
        assert 'Requirement "HVAC Group" not found' in str(e)
        assert 'Requirement "Temperature High Limit" not found' in str(e)

    metadata_df['HVAC Group'] = 2
    metadata_df.at[metadata_df['Name'] == 'Area A', 'HVAC Group'] = 1
    metadata_df.at[metadata_df['Name'] == 'Area B', 'HVAC Group'] = 1
    metadata_df.at[metadata_df['Name'] == 'Area F', 'HVAC Group'] = 1  # This has a missing requirement

    metadata_df['Compressor Power High Limit'] = '35 kW'
    metadata_df.at[metadata_df['Name'] == 'Area D', 'Compressor Power High Limit'] = '60 kW'

    metadata_df['Temperature High Limit'] = '70 F'
    metadata_df.at[metadata_df['Name'] == 'Area J', 'Temperature High Limit'] = '60 F'

    build_df = spy.assets.build([HVAC_KPIs, HVAC_RollUps], metadata_df, errors='raise')

    context = build_df.spy.context

    assert context.objects['test_hvac_monitoring_template >> Cooling Tower 1', 'Area A', HVAC_KPIs].is_child_of(
        context.objects['test_hvac_monitoring_template', 'Cooling Tower 1', HVAC_RollUps]
    )

    assert context.objects['test_hvac_monitoring_template >> Cooling Tower 1', 'Area A', HVAC_KPIs].is_descendant_of(
        context.objects['test_hvac_monitoring_template', 'Cooling Tower 1', HVAC_RollUps]
    )

    assert context.objects['test_hvac_monitoring_template', 'Cooling Tower 1', HVAC_RollUps].is_parent_of(
        context.objects['test_hvac_monitoring_template >> Cooling Tower 1', 'Area A', HVAC_KPIs]
    )

    assert context.objects['test_hvac_monitoring_template', 'Cooling Tower 1', HVAC_RollUps].is_ancestor_of(
        context.objects['test_hvac_monitoring_template >> Cooling Tower 1', 'Area A', HVAC_KPIs]
    )

    expected_items = [('test_hvac_monitoring_template', 'Cooling Tower 1', 'At Least One Compressor On High'),
                      ('test_hvac_monitoring_template', 'Cooling Tower 2', 'At Least One Compressor On High'),
                      ('test_hvac_monitoring_template >> Cooling Tower 1', 'Area A', 'Compressor On High'),
                      ('test_hvac_monitoring_template >> Cooling Tower 2', 'Area D', 'Compressor On High'),
                      ('test_hvac_monitoring_template >> Cooling Tower 1', 'Area B', 'Compressor Power'),
                      ('test_hvac_monitoring_template >> Cooling Tower 2', 'Area F', 'Compressor Power'),
                      ('test_hvac_monitoring_template >> Cooling Tower 1', 'Area C', 'Temperature'),
                      ('test_hvac_monitoring_template >> Cooling Tower 2', 'Area E', 'Temperature')]

    for path, asset, name in expected_items:
        assert len(build_df[(build_df['Path'] == path) & (build_df['Asset'] == asset) &
                            (build_df['Name'] == name)]) == 1, f"Didn't find {path} >> {asset} >> {name}"

    unexpected_items = [
        ('test_hvac_monitoring_template >> Cooling Tower 2', 'Area H', 'Compressor On High'),
        ('test_hvac_monitoring_template >> Cooling Tower 2', 'Area I', 'Compressor On High')
    ]

    for path, asset, name in unexpected_items:
        assert len(build_df[(build_df['Path'] == path) & (build_df['Asset'] == asset) &
                            (build_df['Name'] == name)]) == 0, f"Unexpectedly found {path} >> {asset} >> {name}"

    # Make sure that the differing property requirements are honored
    expected_power_high_limits = {'A': '35 kW', 'B': '35 kW', 'C': '35 kW', 'D': '60 kW'}
    for area in expected_power_high_limits.keys():
        high_limit = expected_power_high_limits[area]
        compressor_on_high = build_df[(build_df['Asset'] == f'Area {area}') &
                                      (build_df['Name'] == 'Compressor On High')]
        compressor_on_high_formula = compressor_on_high.iloc[0]['Formula']
        assert f'$comp_pow > {high_limit}' in compressor_on_high_formula

    # Make sure that the differing scalar requirements are honored
    expected_temperature_high_limits = {'A': '70 F', 'J': '60 F'}
    for area in expected_temperature_high_limits.keys():
        high_limit = expected_temperature_high_limits[area]
        temperature_high_limit = build_df[(build_df['Asset'] == f'Area {area}') &
                                          (build_df['Name'] == 'Temperature High Limit')]
        temperature_high_limit_formula = temperature_high_limit.iloc[0]['Formula']
        assert temperature_high_limit_formula == high_limit

    # Make sure we can push without errors
    spy.push(metadata=build_df, workbook='test_hvac_monitoring_template', worksheet=None,
             datasource='test_hvac_monitoring_template')


@pytest.mark.system
def test_brochure():
    brochure_dict = spy.assets.brochure([HVAC_Health_Monitoring, HVAC_Health_Monitoring_RollUps], 'dict')

    assert len(brochure_dict['Templates']) == 2

    comp_health_template = brochure_dict['Templates'][0]
    assert comp_health_template == {
        "Name": "HVAC Health Monitoring",
        "Description": "Identifies conditions of poor or degraded health in all compressor types,\nincluding:\n\n* "
                       "Karcher\n* Siemens\n* Johnson and Johnson",
        "Attributes": [
            {
                "Name": "Compressor On High",
                "Description": "Indicates that the compressor is about to blow. If other compressors are\nreporting "
                               "low ambient temperature, then this HVAC's compressor power signal\nis ignored."
            }
        ],
        "Components": [],
        "Displays": [],
        "Date Ranges": [],
        "Documents": [],
        "Plots": [],
        "Requirements": [
            {
                "Name": "Compressor Power",
                "Description": "Compressor Power as measured at the power supply of the equipment\nitself.",
                "Type": "Signal",
                "Unit Of Measure Family": "kW"
            },
            {
                "Name": "Compressor Power High Limit",
                "Description": "The high power operating limit for the compressor",
                "Type": "Property"
            },
            {
                "Name": "HVAC Group",
                "Description": "An identifier for the group of HVACs that are all working in the same\nenclosure.",
                "Type": "Property"
            },
            {
                "Name": "Temperature",
                "Description": "The ambient *external* temperature as measured in a neutral location\naway from HVAC "
                               "inlet/outlet sites.\n\n> Note that this value may be derived from equipment sensors "
                               "with a\n> suitable coefficient to account for location bias.",
                "Type": "Signal",
                "Unit Of Measure Family": "F",
                "Optional": True
            },
            {
                "Name": "Temperature High Limit",
                "Description": "The high temperature operating limit for the compressor",
                "Type": "Scalar",
                "Unit Of Measure Family": "F"
            }
        ]
    }

    comp_rollups_template = brochure_dict['Templates'][1]
    assert comp_rollups_template == {
        "Name": "HVAC Health Monitoring RollUps",
        "Description": "Provides an overview of health of all compressors in the corresponding facility.",
        "Attributes": [{
            "Name": "At Least One Compressor On High",
            "Description": "Indicates the at least one compressor in the facility is or has been operating outside "
                           "of\nthe manufacturer's specification."
        }],
        "Components": [],
        "Displays": [],
        "Date Ranges": [],
        "Documents": [],
        "Plots": [],
        "Requirements": [{
            "Name": "HVAC Health Monitoring",
            "Description": "Identifies conditions of poor or degraded health in all compressor types,\nincluding:\n\n"
                           "* Karcher\n* Siemens\n* Johnson and Johnson",
            "Type": "Template"
        }]
    }

    brochure_json = spy.assets.brochure([HVAC_Health_Monitoring, HVAC_Health_Monitoring_RollUps], 'json')
    brochure_json_dict = json.loads(brochure_json)
    assert brochure_dict == brochure_json_dict

    brochure_html = spy.assets.brochure([HVAC_Health_Monitoring, HVAC_Health_Monitoring_RollUps], 'html')
    brochure_html = brochure_html.replace('\r', '')

    assert '<h1>HVAC Health Monitoring</h1>' in brochure_html
    assert '<h1>HVAC Health Monitoring RollUps</h1>' in brochure_html
