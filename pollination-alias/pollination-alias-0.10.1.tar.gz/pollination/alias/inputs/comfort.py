from pollination_dsl.alias import InputAlias
from queenbee.io.common import IOAliasHandler


"""Alias for thermal map air speeds."""
air_speed_input = [
    InputAlias.any(
        name='air_speed',
        description='A single number for air speed in m/s or an hourly data collection '
        'of air speeds that align with the input run_period. This will be '
        'used for all indoor comfort evaluation. Note that the EPW wind speed '
        'will be used for any outdoor sensors. (Default: 0.1).',
        default='0.1',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.inputs.data',
                function='value_or_data_to_str'
            )
        ]
    )
]


"""Alias for thermal map wind speeds."""
wind_speed_input = [
    InputAlias.any(
        name='wind_speed',
        description='A single number for meteorological wind speed in m/s or an hourly '
        'data collection of wind speeds that align with the input run period. '
        'This will be used for all outdoor comfort evaluation. Note that all '
        'sensors on the indoors will always use a wind speed of 0.5 m/s, '
        'which is the lowest acceptable value for the UTCI model. If '
        'unspecified, the EPW wind speed will be used for all outdoor sensors.',
        default='None',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.inputs.data',
                function='value_or_data_to_str'
            )
        ]
    )
]


"""Alias for thermal map metabolic rates."""
met_rate_input = [
    InputAlias.any(
        name='met_rate',
        description='A single number for metabolic rate in met or an hourly data '
        'collection of met rates that align with the run period. (Default: 1.1, for '
        'seated, typing).',
        default='1.1',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.inputs.data',
                function='value_or_data_to_str'
            )
        ]
    )
]


"""Alias for thermal map clothing levels."""
clo_value_input = [
    InputAlias.any(
        name='clo_value',
        description='A single number for clothing level in clo or an hourly data '
        'collection of clothing levels that align with the run period. (Default: 0.7, '
        'for pants and a long sleeve shirt).',
        default='0.7',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.inputs.data',
                function='value_or_data_to_str'
            )
        ]
    )
]


"""Alias for PMV comfort parameters."""
pmv_comfort_par_input = [
    InputAlias.str(
        name='comfort_par',
        description='Optional comfort parameters from the "LB PMV Comfort Parameters" '
        'component to specify the criteria under which conditions are '
        'considered acceptable/comfortable. The default will assume a '
        'PPD threshold of 10 percent and no absolute humidity constraints.',
        default='--ppd-threshold 10',
        platform=['grasshopper']
    )
]


"""Alias for Adaptive comfort parameters."""
adaptive_comfort_par_input = [
    InputAlias.str(
        name='comfort_par',
        description='Optional comfort parameters from the "LB Adaptive Comfort '
        'Parameters" component to specify the criteria under which conditions are '
        'considered acceptable/comfortable. The default will use ASHRAE-55 '
        'adaptive comfort criteria.',
        default='--standard ASHRAE-55',
        platform=['grasshopper']
    )
]


"""Alias for UTCI comfort parameters."""
utci_comfort_par_input = [
    InputAlias.str(
        name='comfort_par',
        description='UTCIParameter string to customize the assumptions of '
        'the UTCI comfort model.',
        default='--cold 9 --heat 26',
        platform=['grasshopper']
    )
]


"""Alias for indoor SolarCal parameters."""
solar_body_par_indoor_input = [
    InputAlias.str(
        name='solar_body_par',
        description='Optional solar body parameters from the "LB Solar Body Parameters" '
        'object to specify the properties of the human geometry assumed in the '
        'shortwave MRT calculation. The default assumes average skin/clothing '
        'absorptivity and a human subject always has their back to the sun '
        'at a 45-degree angle (SHARP = 135).',
        default='--posture seated --sharp 135 --absorptivity 0.7 --emissivity 0.95',
        platform=['grasshopper']
    )
]


"""Alias for outdoor SolarCal parameters."""
solar_body_par_outdoor_input = [
    InputAlias.str(
        name='solar_body_par',
        description='Optional solar body parameters from the "LB Solar Body Parameters" '
        'object to specify the properties of the human geometry assumed in the '
        'shortwave MRT calculation. The default assumes average skin/clothing '
        'absorptivity and a human subject always has their back to the sun '
        'at a 45-degree angle (SHARP = 135).',
        default='--posture standing --sharp 135 --absorptivity 0.7 --emissivity 0.95',
        platform=['grasshopper']
    )
]
