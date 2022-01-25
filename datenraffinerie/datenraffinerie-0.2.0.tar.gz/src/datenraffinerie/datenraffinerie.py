import sys
import multiprocessing
import click
import luigi
import yaml
from .valve_yard import ValveYard
from .config_utilities import ConfigFormatError
from .control_adapter import DAQConfigError
from .daq_coordination import coordinate_daq_access


@click.command()
@click.argument('netcfg', type=click.File('r'))
@click.argument('config', type=click.Path(exists=True))
@click.argument('procedure', type=str)
@click.argument('output', type=click.Path())
@click.option('-a', '--analysis_path', 'analysis_path', type=click.Path(exists=True))
@click.option('-w', '--workers', 'workers', type=int, default=1)
def cli(netcfg, config, procedure, workers, output, analysis_path):
    """ The command line interface to the datenraffinerie intended to
    be one of the primary interfaces for the users.
    """
    try:
        netcfg = yaml.safe_load(netcfg.read())
    except yaml.YAMLError as err:
        print('Error reading in the network config:\n'
              + str(err) + '\nexiting ..')
        sys.exit(1)
    daq_coordination_process = multiprocessing.Process(target=coordinate_daq_access, args=(netcfg, ))
    daq_coordination_process.start()
    try:
        run_result = luigi.build([ValveYard(
            click.format_filename(config),
            procedure,
            output,
            analysis_path,
            netcfg)],
            local_scheduler=True,
            workers=workers,
        )
        print(run_result)
    except ConfigFormatError as err:
        print(err.message)
    except DAQConfigError as err:
        print("The Configuration of one of the executed"
              " DAQ procedures is malformed: ")
        print(err.message)
    except Exception as err:
        print("An error occured that was not properly caught")
        print(err)
    finally:
        daq_coordination_process.kill()
        daq_coordination_process.join()
        sys.exit(1)
