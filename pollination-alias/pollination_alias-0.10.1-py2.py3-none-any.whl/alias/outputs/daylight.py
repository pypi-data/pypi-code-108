from pollination_dsl.alias import OutputAlias
from queenbee.io.common import IOAliasHandler


"""Alias for daylight factor recipe output."""
daylight_factor_results = [
    OutputAlias.any(
        name='results',
        description='Daylight factor values. These can be plugged into the "LB '
        'Spatial Heatmap" component along with meshes of the sensor grids to '
        'visualize results.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='read_df_from_folder'
            )
        ]
    ),

    # Revit alias
    OutputAlias.any(
        name='results',
        description='Daylight factor values.',
        platform=['revit'],
        handler=[
            IOAliasHandler(
                language='csharp',
                module='Pollination.RevitHandlers',
                function='ReadDaylightFactorResultsFromFolder'
            ),

            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='read_df_from_folder'
            )
        ]
    ),

    # Rhino alias
    OutputAlias.linked(
        name='results',
        platform=['rhino'],
        handler=[
            # Preload results 
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='read_df_from_folder'
            ),
            # load preloaded outputs to Rhino with following method
            IOAliasHandler(
                language='csharp', module='Pollination.RhinoHandlers',
                function='LoadMeshBasedResultsToRhino'
            )
        ]
    )
]


"""Alias for sky view recipe output."""
sky_view_results = [
    OutputAlias.any(
        name='results',
        description='Numbers for the sky view or sky exposure at each sensor. These '
        'can be plugged into the "LB Spatial Heatmap" component along with meshes of '
        'the sensor grids to visualize results. Values are in percent (between 0 '
        'and 100).',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='read_df_from_folder'
            )
        ]
    )
]


"""Point-in-time grid-based results."""
point_in_time_grid_results = [
    OutputAlias.any(
        name='results',
        description='Numbers for the point-in-time value at each sensor. These can be '
        'plugged into the "LB Spatial Heatmap" component along with meshes of the '
        'sensor grids to visualize results. Values are in the standard SI '
        'units of the requested input metric.\n* illuminance = lux'
        '\n* irradiance = W/m2\n* luminance = cd/m2\n* radiance = W/m2-sr',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='read_pit_from_folder'
            )
        ]
    )
]


"""Point-in-time view-based results."""
point_in_time_view_results = [
    OutputAlias.any(
        name='results',
        description='High Dynamic Range (HDR) images for each View in the model. These '
        'can be plugged into the Ladybug "Image Viewer" component to preview the image. '
        'They can also be plugged into the "HB False Color" component to convert '
        'the image into a false color version. Lastly, it can be connected to '
        'the "HB HDR to GIF" component to get a GIF image that is more portable '
        'and easily previewed by different software. Pixel values are '
        'in the standard SI units of the requested input metric.\n* illuminance = lux'
        '\n* irradiance = W/m2\n* luminance = cd/m2\n* radiance = W/m2-sr',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='read_images_from_folder'
            )
        ]
    )
]


"""Cumulative sun hours output from the direct sun hours recipe."""
cumulative_sun_hour_results = [
    OutputAlias.any(
        name='hours',
        description='The cumulative number of timesteps that each sensor sees the sun. '
        'If the input wea timestep is 1 (the default), then this is the number of '
        'direct sun hours for each sensor. These can be plugged into the "LB '
        'Spatial Heatmap" component along with meshes of the sensor grids to '
        'visualize results.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='read_hours_from_folder'
            )
        ]
    )
]


"""Direct sun hours recipe output."""
direct_sun_hours_results = [
    OutputAlias.any(
        name='results',
        description='Raw result files (.ill) that contain the number of timesteps '
        'that each sensor is exposed to sun. The units are the timestep of '
        'input wea file. For an hourly wea, each value corresponds to an hour '
        'of direct sun.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='sort_ill_from_folder'
            )
        ]
    )
]


"""Annual daylight recipe output."""
annual_daylight_results = [
    OutputAlias.any(
        name='results',
        description='Raw result files (.ill) that contain illuminance matrices.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='sort_ill_from_folder'
            )
        ]
    )
]


annual_daylight_direct_results = [
    OutputAlias.any(
        name='results_direct',
        description='Raw result files (.ill) that contain matrices for just '
        'the direct illuminance.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='sort_ill_from_folder'
            )
        ]
    )
]


daylight_autonomy_results = [
    OutputAlias.any(
        name='DA',
        description='Daylight autonomy values for each sensor. These can be plugged '
        'into the "LB Spatial Heatmap" component along with meshes of the sensor '
        'grids to visualize results.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='read_da_from_folder'
            )
        ]
    ),
    # Rhino alias
    OutputAlias.linked(
        name='DA Results',
        platform=['rhino'],
        handler=[
            # Preload results 
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='read_da_from_folder'
            ),
            # load preloaded outputs to Rhino with following method
            IOAliasHandler(
                language='csharp', module='Pollination.RhinoHandlers',
                function='LoadMeshBasedResultsToRhino'
            )
        ]
    )
]


continuous_daylight_autonomy_results = [
    OutputAlias.any(
        name='cDA',
        description='Continuous daylight autonomy values for each sensor. These can '
        'be plugged into the "LB Spatial Heatmap" component along with meshes of '
        'the sensor grids to visualize results.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='read_cda_from_folder'
            )
        ]
    ),
    # Rhino alias
    OutputAlias.linked(
        name='cDA Results',
        platform=['rhino'],
        handler=[
            # Preload results 
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='read_cda_from_folder'
            ),
            # load preloaded outputs to Rhino with following method
            IOAliasHandler(
                language='csharp', module='Pollination.RhinoHandlers',
                function='LoadMeshBasedResultsToRhino'
            )
        ]
    )
]


udi_results = [
    OutputAlias.any(
        name='UDI',
        description='Useful daylight autonomy values for each sensor. These can be '
        'plugged into the "LB Spatial Heatmap" component along with meshes of the '
        'sensor grids to visualize results.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='read_udi_from_folder'
            )
        ]
    ),
    # Rhino alias
    OutputAlias.linked(
        name='UDI Results',
        platform=['rhino'],
        handler=[
            # Preload results 
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='read_udi_from_folder'
            ),
            # load preloaded outputs to Rhino with following method
            IOAliasHandler(
                language='csharp', module='Pollination.RhinoHandlers',
                function='LoadMeshBasedResultsToRhino'
            )
        ]
    )
]


udi_lower_results = [
    OutputAlias.any(
        name='UDI_low',
        description='Values for the percent of time that is below the lower threshold '
        'of useful daylight illuminance. These can be plugged into the "LB '
        'Spatial Heatmap" component along with meshes of the sensor grids to '
        'visualize results.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='read_udi_from_folder'
            )
        ]
    ),
    # Rhino alias
    OutputAlias.linked(
        name='UDI low Results',
        platform=['rhino'],
        handler=[
            # Preload results 
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='read_udi_from_folder'
            ),
            # load preloaded outputs to Rhino with following method
            IOAliasHandler(
                language='csharp', module='Pollination.RhinoHandlers',
                function='LoadMeshBasedResultsToRhino'
            )
        ]
    )
]


udi_upper_results = [
    OutputAlias.any(
        name='UDI_up',
        description='Values for the percent of time that is above the upper threshold '
        'of useful daylight illuminance. These can be plugged into the "LB '
        'Spatial Heatmap" component along with meshes of the sensor grids to '
        'visualize results.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='read_udi_from_folder'
            )
        ]
    ),
    # Rhino alias
    OutputAlias.linked(
        name='UDI up Results',
        platform=['rhino'],
        handler=[
            # Preload results 
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='read_udi_from_folder'
            ),
            # load preloaded outputs to Rhino with following method
            IOAliasHandler(
                language='csharp', module='Pollination.RhinoHandlers',
                function='LoadMeshBasedResultsToRhino'
            )
        ]
    )
]


"""Total Irradiance results from the Annual Irradiance recipe."""
total_radiation_results = [
    OutputAlias.any(
        name='results',
        description='Raw result files (.ill) that contain irradiance matrices '
        'for the total radiation at each sensor and timestep.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='sort_ill_from_folder'
            )
        ]
    )
]


"""Direct Irradiance results from the Annual Irradiance recipe."""
direct_radiation_results = [
    OutputAlias.any(
        name='direct',
        description='Raw result files (.ill) that contain irradiance matrices '
        'for the direct radiation at each sensor and timestep.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='sort_ill_from_folder'
            )
        ]
    )
]


"""Average Irradiance from the Annual Irradiance recipe."""
average_irradiance_results = [
    OutputAlias.any(
        name='avg_irr',
        description='The average irradiance in W/m2 for each sensor over the Wea '
        'time period.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='read_pit_from_folder'
            )
        ]
    )
]


"""Peak Irradiance from the Annual Irradiance recipe."""
peak_irradiance_results = [
    OutputAlias.any(
        name='peak_irr',
        description='The highest irradiance value in W/m2 during the Wea time period. '
        'This is suitable for assessing the worst-case solar load of clear skies on '
        'cooling design days. It can also be used to determine the highest radiant '
        'temperatures that occupants might experience in over the time period of '
        'the Wea.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='read_pit_from_folder'
            )
        ]
    )
]


"""Peak Irradiance from the Annual Irradiance recipe."""
cumulative_radiation_results = [
    OutputAlias.any(
        name='radiation',
        description='The cumulative radiation in kWh/m2 over the Wea time period.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='read_pit_from_folder'
            )
        ]
    )
]


"""LEED Daylight Illuminance 9AM recipe output."""
illuminance_9am_results = [
    OutputAlias.any(
        name='ill_9am',
        description='Illuminance results for the 9AM simulation in lux.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='read_pit_from_folder'
            )
        ]
    )
]


"""LEED Daylight Illuminance 3PM recipe output."""
illuminance_3pm_results = [
    OutputAlias.any(
        name='ill_3pm',
        description='Illuminance results for the 3PM simulation in lux.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='read_pit_from_folder'
            )
        ]
    )
]


"""LEED Daylight Pass/Fail 9AM recipe output."""
pass_fail_9am_results = [
    OutputAlias.any(
        name='passing_9am',
        description='Pass/Fail results for the 9AM simulation as one/zero values.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='read_pit_from_folder'
            )
        ]
    )
]

"""LEED Daylight Pass/Fail 9AM recipe output."""
pass_fail_3pm_results = [
    OutputAlias.any(
        name='passing_3pm',
        description='Pass/Fail results for the 3PM simulation as one/zero values.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='read_pit_from_folder'
            )
        ]
    )
]


"""LEED Daylight Pass/Fail combined recipe output."""
pass_fail_comb_results = [
    OutputAlias.any(
        name='passing_comb',
        description='Pass/Fail results for the combined simulation as one/zero values.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='read_pit_from_folder'
            )
        ]
    )
]


"""LEED daylight illuminance credit summary output.

The result is a JSON with a summary of the credits achieved.
"""
leed_ill_credit_summary_results = [
    OutputAlias.any(
        name='credits',
        description='The number of LEED daylight credits achieved and a summary of the '
        'percentage of the sensor grid area that meets the LEED daylight criteria.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.daylight',
                function='ill_credit_json_from_path'
            )
        ]
    )
]
