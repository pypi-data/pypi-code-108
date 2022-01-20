"""Run EPW weather data through comfort models."""
from dataclasses import dataclass
from pollination_dsl.function import Inputs, Outputs, Function, command


@dataclass
class PrevailingTemperature(Function):
    """Get Adaptive comfort Prevailing Outdoor Temperature from an EPW weather file."""

    epw = Inputs.file(
        description='Weather file used to obtain prevailing temperatures.',
        path='weather.epw', extensions=['epw']
    )

    comfort_par = Inputs.str(
        description='An AdaptiveParameter string to customize the assumptions of '
        'the Adaptive comfort model.', default='--standard ASHRAE-55'
    )

    run_period = Inputs.str(
        description='An AnalysisPeriod string to set the start and end dates of the '
        'analysis (eg. "6/21 to 9/21 between 8 and 16 @1"). If unspecified, results '
        'will be annual.', default=''
    )

    output_format = Inputs.str(
        description='A switch to note whether the output data should be in CSV or '
        'JSON format.', default='csv', spec={'type': 'string', 'enum': ['csv', 'json']}
    )

    order_by = Inputs.str(
        description='A switch to note whether whether the CSV should be written '
        'with rows or columns.', default='columns',
        spec={'type': 'string', 'enum': ['columns', 'rows']}
    )

    @command
    def get_prevailing_temperature(self):
        return 'ladybug-comfort epw prevailing weather.epw ' \
            '--comfort-par "{{self.comfort_par}}" --run-period "{{self.run_period}}" ' \
            '--{{self.output_format}} --{{self.order_by}} --output-file prevailing.csv'

    prevailing_temperature = Outputs.file(
        description='CSV or JSON file containing list of prevailing temperatures '
        'in celsius.', path='prevailing.csv'
    )


@dataclass
class AirSpeedJson(Function):
    """Get a JSON of air speeds that can be used as input for the mtx functions."""

    epw = Inputs.file(
        description='Weather file used to obtain prevailing temperatures.',
        path='weather.epw', extensions=['epw']
    )

    enclosure_info = Inputs.file(
        description='A JSON file containing information about the radiant '
        'enclosure that sensor points belong to.', path='enclosure_info.json',
        extensions=['json']
    )

    multiply_by = Inputs.float(
        description='A number to denote a factor that EPW wind speeds should be '
        'multipled by in order to represent air speeds at ground level.', default=0.5
    )

    indoor_air_speed = Inputs.str(
        description='A single number for air speed in m/s or a string of a JSON array '
        'with numbers that align with run period. This will be used for all '
        'indoor comfort evaluation.', default='0.1'
    )

    run_period = Inputs.str(
        description='An AnalysisPeriod string to set the start and end dates of the '
        'analysis (eg. "6/21 to 9/21 between 8 and 16 @1"). If unspecified, results '
        'will be annual.', default=''
    )

    @command
    def get_air_speed_json(self):
        return 'ladybug-comfort epw air-speed-json weather.epw enclosure_info.json ' \
            '--multiply-by {{self.multiply_by}} --indoor-air-speed ' \
            '"{{self.indoor_air_speed}}" --run-period "{{self.run_period}}" ' \
            '--output-file air_speed.json'

    air_speeds = Outputs.file(
        description='A JSON of air speeds that can be used as input for the mtx '
        'functions.', path='air_speed.json'
    )
