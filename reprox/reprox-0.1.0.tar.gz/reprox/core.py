"""Shared common methods for reprocessing, not useful in itself"""

import argparse
import configparser
import importlib
import logging
import os
import grp
import json
import typing
import inspect

reprox_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

if 'REPROX_CONFIG' in os.environ:
    config_path = os.environ['REPROX_CONFIG']
else:
    config_path = os.path.join(reprox_dir, 'reprocessing.ini')
    print(f'Using {config_path}-config. Overwrite by setting "REPROX_CONFIG" '
          f'as an environment variable')

if not os.path.exists(config_path):
    raise FileNotFoundError(f'{config_path} does not exist')

config = configparser.ConfigParser()
config.sections()
config.read(config_path)
logging.basicConfig(
    level=getattr(logging, config['processing']['logging_level'].upper()),
    format=('%(asctime)s '
            '| %(name)-12s '
            '| %(levelname)-8s '
            '| %(message)s '
            '| %(funcName)s (l. %(lineno)d)'
            ),
    datefmt='%m-%d %H:%M')

log = logging.getLogger('reprocessing')

command = """
cd {base_folder}
straxer \
    {run_name} \
    --target {target} \
    --context {context} \
    --package {package} \
    --timeout {timeout} 
    {extra_options}
echo Processing job ended
"""

log_folder = os.path.join(config['context']['base_folder'], 'job_logs')
log_fn = os.path.join(log_folder, '{run_id}.txt')
runs_csv = os.path.join(config['context']['base_folder'], config['context']['runs_to_do'])

if not os.path.exists(os.path.split(log_fn)[0]):
    os.mkdir(os.path.split(log_fn)[0])


def get_context(package=config['context']['package'],
                context=config['context']['context'],
                output_folder=os.path.join(config['context']['base_folder'], 'strax_data'),
                config_kwargs: typing.Union[None, dict] = None,
                _minimum_run_number=int(config['context']['minimum_run_number']),
                _maximum_run_number=None,
                ):
    module = importlib.import_module(f'{package}.contexts')
    st = getattr(module, context)(output_folder=output_folder,
                                  _minimum_run_number=_minimum_run_number,
                                  _maximum_run_number=_maximum_run_number,
                                  )
    if config_kwargs is not None:
        log.warning(f'Updating the context with the following config {config_kwargs}')
        st.set_config(config_kwargs)
    st.context_config['check_available'] = []
    return st


def parse_args(description='nton reprocessing on dali',
               include_find_args=False,
               include_processing_args=False,
               include_workflow_args=False,
               ):
    """Parse arguments to return to the user"""
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '--package',
        default=config['context']['package'],
        choices=['straxen', 'cutax'],
        type=str,
        help="Package to get context from"
    )
    parser.add_argument(
        '--context',
        default=config['context']['context'],
        type=str,
        help="Name of the context (should be in the package specified with --package)"
    )
    parser.add_argument(
        '--context-kwargs', '--context_kwargs', '--config',
        dest='context_kwargs',
        type=json.loads,
        default=None,
        help='Overwrite st.config settings using a json file. For example:'
             '--context_kwargs '
             '\'{'
             '"s1_min_coincidence": 2,'
             '"s2_min_pmts": 10'
             '}\''
    )
    parser.add_argument(
        '--config-kwargs', '--config_kwargs',
        dest='context_config_kwargs',
        type=json.loads,
        default={},
        help='overwrite st.context_config settings using a json file. For example:'
             '--config-kwargs '
             '\'{'
             '"output_folder": "./strax_data",'
             '}\''
    )
    parser.add_argument(
        '--targets', '--target',
        default=['event_info', 'event_pattern_fit'],
        nargs='*',
        help='Target final data type to produce. Can be a list for multicore mode.'
    )
    parser.add_argument(
        '--force-non-admin', '--force_non_admin',
        action='store_true',
        dest='force_non_admin',
        help='Allow non admin users to use this script.'
    )
    if include_find_args:
        parser = _include_find_args(parser)
    if include_processing_args:
        parser = _include_processing_args(parser)
    if include_workflow_args:
        parser = _include_workflow_args(parser)

    args = parser.parse_args()
    if hasattr(args, 'cmt_version') and args.cmt_version == 'False':
        args.cmt_version = False
    if not args.force_non_admin and not check_user_is_admin():
        raise PermissionError(
            f'{os.getlogin()}, you are not an admin so you probably don\'t'
            f' want to do a full reprocessing. In case you know what you are'
            f' doing add the "--force-non-admin" flag to you instructions')
    return args


def _include_find_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Add arguments for finding data to the parser"""
    parser.add_argument(
        '--detectors', '--consider_detectors', '--consider-detectors',
        default=['tpc'],
        nargs='*',
        help='Data of detectors to process, choose one or more of "tpc, neutron_veto, muon_veto"'
    )
    parser.add_argument(
        '--cmt-version', '--cmt_version', '--check_cmt_version', '--check-cmt-version',
        default=config['context']['cmt_version'],
        type=str,
        dest='cmt_version',
        help='Specify CMT version if we should exclude runs that cannot be '
             '(fully) processed with this CMT version. Set to False if you '
             'don\'t want to run this check'
    )
    return parser


def _include_workflow_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Add arguments for running the entire workflow to the parser"""
    parser.add_argument(
        '--move-after-workflow', '--move_after_workflow', '--move',
        action='store_true',
        dest='move_after_workflow',
        help='After running the workflow, move the data into the production folder'
    )
    parser.add_argument(
        '--skip-find', '--skip_find',
        action='store_true',
        dest='skip_find',
        help='If set, skip finding the data and just use the CSV file also previously used.'
    )
    return parser


def _include_processing_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Add arguments for processing data to the parser"""
    parser.add_argument(
        '--ram', '--RAM',
        default=config['processing']['ram'],
        type=int,
        help='RAM [MB] per CPU to request'
    )
    parser.add_argument(
        '--cpu', '--cpu_per_job', '--cpu-per-job',
        default=config['processing']['cpus_per_job'],
        type=int,
        help='Number of CPUs per job to request'
    )
    parser.add_argument(
        '--submit-only', '--submit_only',
        default=config['processing']['submit_only'],
        type=int,
        help='Limits the total number of jobs to submit. Useful for testing. '
    )
    parser.add_argument(
        '--tag', '--container',
        default=config['processing']['container_tag'],
        type=str,
        help='Container to use for the reprocessing. '
    )
    parser.add_argument(
        '--clear_logs', '--clear-logs',
        dest='clear_logs',
        action='store_true',
        help='When submitting new jobs, first clear the logs'
    )
    return parser


def check_user_is_admin(admin_group='xenon1t-admins'):
    """Check that the user is an xenon1t-admin"""
    return admin_group in [grp.getgrgid(g).gr_name for g in os.getgroups()]


def log_versions():
    """Log versions (nested import makes the arg parsing quick)"""
    import straxen
    log.warning(straxen.print_versions(return_string=True),
                )


if __name__ == '__main__':
    raise ValueError('core.py is not run on it\'s own, you are looking for run_workflow.py instead')
