from pollination_dsl.alias import OutputAlias
from queenbee.io.common import IOAliasHandler


"""Alias for Thermal Comfort Percent (TCP)"""
tcp_output = [
    OutputAlias.any(
        name='TCP',
        description='Lists of values between 0 and 100 for the Thermal Comfort Percent '
        '(TCP). These can be plugged into the "LB Spatial Heatmap" component along '
        'with meshes of the sensor grids to visualize spatial thermal comfort. '
        'TCP is the percentage of occupied time where thermal conditions are '
        'acceptable/comfortable. Occupied hours are determined from the '
        'occupancy schedules of each room (any time where the occupancy '
        'schedule is >= 0.1 will be considered occupied). Outdoor sensors '
        'are considered occupied at all times. More custom TCP studies can '
        'be done by post-processing the condition results.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.comfort',
                function='read_comfort_percent_from_folder'
            )
        ]
    ),
    # Rhino alias
    OutputAlias.linked(
        name='TCP',
        platform=['rhino'],
        handler=[
            # Preload results 
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.comfort',
                function='read_comfort_percent_from_folder'
            ),
            # load preloaded outputs to Rhino with following method
            IOAliasHandler(
                language='csharp', module='Pollination.RhinoHandlers',
                function='LoadMeshBasedResultsToRhino'
            )
        ]
    )
]


"""Alias for Heat Sensation Percent (HSP)"""
hsp_output = [
    OutputAlias.any(
        name='HSP',
        description='Lists of values between 0 and 100 for the Heat Sensation Percent '
        '(HSP). These can be plugged into the "LB Spatial Heatmap" component along with '
        'meshes of the sensor grids to visualize uncomfortably hot locations. '
        'HSP is the percentage of occupied time where thermal conditions are '
        'hotter than what is considered acceptable/comfortable. Occupied hours '
        'are determined from the occupancy schedules of each room (any time '
        'where the occupancy schedule is >= 0.1 will be considered occupied). '
        'Outdoor sensors are considered occupied at all times. More custom HSP '
        'studies can be done by post-processing the condition results.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.comfort',
                function='read_comfort_percent_from_folder'
            )
        ]
    ),
    # Rhino alias
    OutputAlias.linked(
        name='HSP',
        platform=['rhino'],
        handler=[
            # Preload results 
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.comfort',
                function='read_comfort_percent_from_folder'
            ),
            # load preloaded outputs to Rhino with following method
            IOAliasHandler(
                language='csharp', module='Pollination.RhinoHandlers',
                function='LoadMeshBasedResultsToRhino'
            )
        ]
    )
]


"""Alias for Cold Sensation Percent (CSP)."""
csp_output = [
    OutputAlias.any(
        name='CSP',
        description='Lists of values between 0 and 100 for the Cold Sensation Percent '
        '(CSP). These can be plugged into the "LB Spatial Heatmap" component along with '
        'meshes of the sensor grids to visualize uncomfortably cold locations. '
        'CSP is the percentage of occupied time where thermal conditions are '
        'colder than what is considered acceptable/comfortable. Occupied hours '
        'are determined from the occupancy schedules of each room (any time '
        'where the occupancy schedule is >= 0.1 will be considered occupied). '
        'Outdoor sensors are considered occupied at all times. More custom CSP '
        'studies can be done by post-processing the condition results.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.comfort',
                function='read_comfort_percent_from_folder'
            )
        ]
    ),
    # Rhino alias
    OutputAlias.linked(
        name='CSP',
        platform=['rhino'],
        handler=[
            # Preload results 
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.comfort',
                function='read_comfort_percent_from_folder'
            ),
            # load preloaded outputs to Rhino with following method
            IOAliasHandler(
                language='csharp', module='Pollination.RhinoHandlers',
                function='LoadMeshBasedResultsToRhino'
            )
        ]
    )
]


"""Alias for thermal condition output."""
thermal_condition_output = [
    OutputAlias.any(
        name='condition',
        description='A folder containing CSV maps of comfort conditions for each '
        'sensor grid at each time step of the analysis. This can be connected to the '
        '"HB Read Thermal Matrix" component to parse detailed results into '
        'Grasshopper. -1 indicates unacceptably cold conditions. +1 indicates '
        'unacceptably hot conditions. 0 indicates neutral (comfortable) conditions.',
        platform=['grasshopper']
    )
]


"""Alias for operative temperature output."""
operative_temp_output = [
    OutputAlias.any(
        name='op_temp',
        description='A folder containing CSV maps of Operative Temperature for each '
        'sensor grid at each time step of the analysis. This can be connected to the '
        '"HB Read Thermal Matrix" component to parse detailed results into Grasshopper. '
        'Values are in Celsius.',
        platform=['grasshopper']
    )
]


"""Alias for degrees from neutral temperature output."""
degrees_neutral_output = [
    OutputAlias.any(
        name='deg_neut',
        description='A folder containing CSV maps of the degrees Celsius from the '
        'adaptive comfort neutral temperature for each sensor grid at each time step '
        'of the analysis. This can be connected to the "HB Read Thermal Matrix" '
        'component to parse detailed results into Grasshopper. This can be '
        'used to understand not just whether conditions are acceptable but '
        'how uncomfortably hot or cold they are.',
        platform=['grasshopper']
    )
]


"""Alias for operative temperature or SET output."""
operative_or_set_output = [
    OutputAlias.any(
        name='temperature',
        description='A folder containing CSV maps of Operative Temperature for each '
        'sensor grid at each time step of the analysis. Alternatively, if the '
        'write_set_map_ option is used, the CSV maps here will contain '
        'Standard Effective Temperature (SET). This can be connected to the '
        '"HB Read Thermal Matrix" component to parse detailed results into '
        'Grasshopper. Values are in Celsius.',
        platform=['grasshopper']
    )
]


"""Alias for Predicted Mean Vote output."""
pmv_output = [
    OutputAlias.any(
        name='pmv',
        description='A folder containing CSV maps of the Predicted Mean Vote (PMV) '
        'for each sensor grid at each time step of the analysis. This can be connected '
        'to the "HB Read Thermal Matrix" component to parse detailed results '
        'into Grasshopper. This can be used to understand not just whether '
        'conditions are acceptable but how uncomfortably hot or cold they are.',
        platform=['grasshopper']
    )
]


"""Alias for Universal Thermal Climate Index output."""
utci_output = [
    OutputAlias.any(
        name='utci',
        description='A folder containing CSV maps of Universal Thermal Climate Index '
        '(UTCI) temperatures for each sensor grid at each time step of the analysis. '
        'This can be connected to the "HB Read Thermal Matrix" component to '
        'parse detailed results into Grasshopper. Values are in Celsius.',
        platform=['grasshopper']
    )
]


"""Alias for UTCI Categories output."""
utci_category_output = [
    OutputAlias.any(
        name='category',
        description='A folder containing CSV maps of the heat/cold stress categories '
        'for each sensor grid at each time step of the analysis. This can be connected '
        'to the "HB Read Thermal Matrix" component to parse detailed results '
        'into Grasshopper. This can be used to understand not just whether '
        'conditions are acceptable but how uncomfortably hot or cold they '
        'are. Values indicate the following. '
        '-5 = extreme cold stress. '
        '-4 = very strong cold stress. '
        '-3 = strong cold stress. '
        '-2 = moderate cold stress. '
        '-1 = slight cold stress. '
        ' 0 = no thermal stress. '
        '+1 = slight heat stress. '
        '+2 = moderate heat stress. '
        '+3 = strong heat stress. '
        '+4 = very strong heat stress. '
        '+5 = extreme heat stress',
        platform=['grasshopper']
    )
]
