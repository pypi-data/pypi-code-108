"""Run matrices of thermal conditions through comfort models."""
from dataclasses import dataclass
from pollination_dsl.function import Inputs, Outputs, Function, command


@dataclass
class PmvMtx(Function):
    """Get CSV files with matrices of PMV comfort from matrices of PMV inputs."""

    air_temperature_mtx = Inputs.file(
        description='A CSV file with with a matrix of air temperature values in '
        'celsius.', path='air_temperature.csv', extensions=['csv']
    )

    rel_humidity_mtx = Inputs.file(
        description='A CSV file with with a matrix of relative humidity values in '
        'percent.', path='rel_humidity.csv', extensions=['csv']
    )

    rad_temperature_mtx = Inputs.file(
        description='A CSV file with with a matrix of mean radiant temperature '
        'values in celsius.', path='rad_temperature.csv', extensions=['csv']
    )

    rad_delta_mtx = Inputs.file(
        description='A CSV file with with with a matrix of MRT deltas in celsius '
        'to be added to the base MRT values.', path='rad_delta.csv', extensions=['csv']
    )

    air_speed_json = Inputs.file(
        description='A JSON file conaining a simplified set of air speed values '
        'for each row of the matrix in m/s.', path='air_speed.json', extensions=['json']
    )

    met_rate = Inputs.str(
        description='A single number for metabolic rate in met or a string of a '
        'JSON array with numbers that align with the result-sql reporting period.',
        default='1.1'
    )

    clo_value = Inputs.str(
        description='A single number for clothing level in clo or a string of a JSON '
        'array with numbers that align with the result-sql reporting period.',
        default='0.7'
    )

    comfort_par = Inputs.str(
        description='A PMVParameter string to customize the assumptions of '
        'the PMV comfort model.', default='--ppd-threshold 10'
    )

    write_set_map = Inputs.str(
        description='A switch to note whether the output temperature CSV should '
        'record Operative Temperature or Standard Effective Temperature (SET). '
        'SET is relatively intense to compute and so only recording Operative '
        'Temperature can greatly reduce run time, particularly when air speeds '
        'are low. However, SET accounts for all 6 PMV model inputs and so is a '
        'more representative "feels-like" temperature for the PMV model.',
        default='write-op-map',
        spec={'type': 'string', 'enum': ['write-op-map', 'write-set-map']}
    )

    @command
    def run_pmv_mtx(self):
        return 'ladybug-comfort mtx pmv air_temperature.csv rel_humidity.csv ' \
            '--rad-temperature-mtx rad_temperature.csv --rad-delta-mtx rad_delta.csv ' \
            '--air-speed-json air_speed.json --met-rate "{{self.met_rate}}" ' \
            '--clo-value "{{self.clo_value}}" --comfort-par "{{self.comfort_par}}" ' \
            '--{{self.write_set_map}} --folder output'

    result_folder = Outputs.folder(
        description='Folder containing all of the output CSV files.', path='output'
    )

    temperature_map = Outputs.file(
        description='CSV file containing a map of Operative Temperature (To) or '
        'Standard Effective Temperature (SET) for each sensor and step of the analysis.'
        'The write-set-map input determines which of the two metrics this file '
        'contains.', path='output/temperature.csv'
    )

    condition_map = Outputs.file(
        description='CSV file containing a map of comfort conditions for each '
        'sensor and step of the analysis. -1 indicates unacceptably cold conditions. '
        '+1 indicates unacceptably hot conditions. 0 indicates neutral (comfortable) '
        'conditions.', path='output/condition.csv'
    )

    pmv_map = Outputs.file(
        description='CSV file containing the Predicted Mean Vote (PMV) for each '
        'sensor and step of the analysis. This can be used to understand not just '
        'whether conditions are acceptable but how uncomfortably hot or cold they are.',
        path='output/condition_intensity.csv'
    )


@dataclass
class AdaptiveMtx(Function):
    """Get CSV files with matrices of Adaptive comfort from matrices of Adaptive inputs.
    """

    air_temperature_mtx = Inputs.file(
        description='A CSV file with with a matrix of air temperature values in '
        'celsius.', path='air_temperature.csv', extensions=['csv']
    )

    prevailing_temperature = Inputs.file(
        description='A CSV file with with a list of prevailing outdoor temperatures '
        'in a single row (one temperautre per column).',
        path='prevailing.csv', extensions=['csv']
    )

    rad_temperature_mtx = Inputs.file(
        description='A CSV file with with a matrix of mean radiant temperature '
        'values in celsius.', path='rad_temperature.csv', extensions=['csv']
    )

    rad_delta_mtx = Inputs.file(
        description='A CSV file with with with a matrix of MRT deltas in celsius '
        'to be added to the base MRT values.', path='rad_delta.csv', extensions=['csv']
    )

    air_speed_json = Inputs.file(
        description='A JSON file conaining a simplified set of air speed values '
        'for each row of the matrix in m/s.', path='air_speed.json', extensions=['json']
    )

    comfort_par = Inputs.str(
        description='An AdaptiveParameter string to customize the assumptions of '
        'the Adaptive comfort model.', default='--standard ASHRAE-55'
    )

    @command
    def run_adaptive_mtx(self):
        return 'ladybug-comfort mtx adaptive air_temperature.csv prevailing.csv ' \
            '--rad-temperature-mtx rad_temperature.csv --rad-delta-mtx rad_delta.csv ' \
            '--air-speed-json air_speed.json --comfort-par "{{self.comfort_par}}" ' \
            '--folder output'

    result_folder = Outputs.folder(
        description='Folder containing all of the output CSV files.', path='output'
    )

    temperature_map = Outputs.file(
        description='CSV file containing a map of Operative Temperature (To) for each '
        'sensor and step of the analysis.', path='output/temperature.csv'
    )

    condition_map = Outputs.file(
        description='CSV file containing a map of comfort conditions for each '
        'sensor and step of the analysis. -1 indicates unacceptably cold conditions. '
        '+1 indicates unacceptably hot conditions. 0 indicates neutral (comfortable) '
        'conditions.', path='output/condition.csv'
    )

    deg_from_neutral_map = Outputs.file(
        description='CSV file containing a map of the degrees Celsius from the '
        'adaptive comfort neutral temperature for each sensor and step of the '
        'analysis. This can be used to understand not just whether conditions are '
        'acceptable but how uncomfortably hot or cold they are.',
        path='output/condition_intensity.csv'
    )


@dataclass
class UtciMtx(Function):
    """Get CSV files with matrices of UTCI comfort from matrices of UTCI inputs."""

    air_temperature_mtx = Inputs.file(
        description='A CSV file with with a matrix of air temperature values in '
        'celsius.', path='air_temperature.csv', extensions=['csv']
    )

    rel_humidity_mtx = Inputs.file(
        description='A CSV file with with a matrix of relative humidity values in '
        'percent.', path='rel_humidity.csv', extensions=['csv']
    )

    rad_temperature_mtx = Inputs.file(
        description='A CSV file with with a matrix of mean radiant temperature '
        'values in celsius.', path='rad_temperature.csv', extensions=['csv']
    )

    rad_delta_mtx = Inputs.file(
        description='A CSV file with with with a matrix of MRT deltas in celsius '
        'to be added to the base MRT values.', path='rad_delta.csv', extensions=['csv']
    )

    wind_speed_json = Inputs.file(
        description='A JSON file conaining a simplified set of meteorological wind '
        'speed values for each row of the matrix in m/s.',
        path='wind_speed.json', extensions=['json']
    )

    comfort_par = Inputs.str(
        description='A UTCIParameter string to customize the assumptions of '
        'the UTCI comfort model.', default='--cold 9 --heat 26'
    )

    @command
    def run_utci_mtx(self):
        return 'ladybug-comfort mtx utci air_temperature.csv rel_humidity.csv ' \
            '--rad-temperature-mtx rad_temperature.csv --rad-delta-mtx rad_delta.csv ' \
            '--wind-speed-json wind_speed.json --comfort-par "{{self.comfort_par}}" ' \
            '--folder output'

    result_folder = Outputs.folder(
        description='Folder containing all of the output CSV files.', path='output'
    )

    temperature_map = Outputs.file(
        description='CSV file containing a map of Universal Thermal Climate Index '
        '(UTCI) temperatures for each sensor and step of the analysis.',
        path='output/temperature.csv'
    )

    condition_map = Outputs.file(
        description='CSV file containing a map of comfort conditions for each '
        'sensor and step of the analysis. -1 indicates unacceptably cold conditions. '
        '+1 indicates unacceptably hot conditions. 0 indicates neutral (comfortable) '
        'conditions.', path='output/condition.csv'
    )

    category_map = Outputs.file(
        description='CSV file containing a map of the heat/cold stress categories '
        'for each sensor and step of the analysis. -5 indicates extreme cold stress. '
        '+5 indicates extreme heat stress. 0 indicates no thermal stress. '
        'This can be used to understand not just whether conditions are '
        'acceptable but how uncomfortably hot or cold they are.',
        path='output/condition_intensity.csv'
    )
