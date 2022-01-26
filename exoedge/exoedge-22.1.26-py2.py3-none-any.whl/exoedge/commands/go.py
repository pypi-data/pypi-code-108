# pylint: disable=C0103,C0301,W1202
"""
Primary module to support edged tool.
"""
import os
import json
import time
import threading
import logging
import subprocess
from exoedge import logger
from exoedge.data_in import DataIn
from exoedge.data_queuing import Queuing
from exoedge.config_io import ConfigIO
from exoedge.configs import ConfigWatcher
from exoedge.config_applications import ConfigApplications
from exoedge.commands import Command
from exoedge.constants import OPTION_NAME_MAPPER, OPTION_TYPE_MAP, OPTION_PRECEDENCE, DEFAULTS

LOG = logger.getLogger(__name__)

class ExoCommand(Command):
    """
    Create and start ExoSense client.

    usage:
        go [options]

    options:
        -h --help           Show this screen.
    """
    Name = 'go'

    def execute(self):
        from murano_client.client import MuranoClient
        from exoedge.options_handler import OptionsHandler


        # --------------------------------------
        # OPTIONS HANDLING
        # --------------------------------------
        # The value of an option comes from, in
        # decreasing priority:
        #   1. CLI switches
        #   2. Environment variables
        #   3. INI file
        #   4. Defaults
        # --------------------------------------
        OH_ARGS = {
            'cli': self.global_args,
            'env': os.environ,
            'dft': DEFAULTS
        }

        # if not OH_ARGS['cli'].get('--queuing'):
            # OH_ARGS['cli']['--queuing'] = None
        # -----------------------------------------
        # Include INI?
        _INI_FP = OH_ARGS['cli'].get('--ini-file') or OH_ARGS['env'].get('EDGED_INI_FILE') or OH_ARGS['dft'].get('ini_file') or None
        _NO_FS = OH_ARGS['cli'].get('--no-filesystem') or OH_ARGS['env'].get('EDGED_NO_FILESYSTEM') or None
        _INI_FILE = _INI_FP and not _NO_FS
        if _INI_FILE:
            from murano_client.atomicconfigparser import atomicconfigparser as IniParser
            I = IniParser(allow_no_value=True)
            I.read(_INI_FP)

            INI_VALUES = {}
            for s in I.sections():
                LOG.info('INI section %s...', s)
                for o, v in I.items(s):
                    LOG.critical('INI option {}.{} = {}'.format(s, o, v))
                    INI_VALUES.update({o: v})
            if not ('murano_id' in INI_VALUES.keys()):
                try:
                    uuid = guess_serial_number()
                    INI_VALUES['murano_id'] = uuid
                except:
                    pass

            OH_ARGS.update({'ini': INI_VALUES})
        # -----------------------------------------


        OH = OptionsHandler(OPTION_PRECEDENCE,
                            OPTION_TYPE_MAP,
                            OPTION_NAME_MAPPER,
                            **OH_ARGS)
        PARAMETERS = OH.values
        # allow exoedge.configs module to determine these defaults.
        if '--config-io-file' not in OH_ARGS['cli'] and 'EDGED_CONFIG_IO_FILE' not in OH_ARGS['env']:
            PARAMETERS.pop('config_io_file')
        if '--config-applications-file' not in OH_ARGS['cli'] and 'EDGED_CONFIG_APPLICATIONS_FILE' not in OH_ARGS['env']:
            PARAMETERS.pop('config_applications_file')

        if PARAMETERS.get('debug'):
            LOG.critical(
                "Setting all exoedge logger levels to: {}"
                .format(PARAMETERS.get('debug'))
            )
            for lgr in logger.getExoEdgeLoggers():
                lgr.setLevel(
                    getattr(
                        logging,
                        PARAMETERS.get('debug').upper()
                        )
                    )

        LOG.info("Startup parameters: \n{}"
                 .format(json.dumps(PARAMETERS, indent=2)))

        # -----------------------------------------
        # Define MuranoClient object
        # -----------------------------------------
        device = MuranoClient(memory_queue=False, **PARAMETERS)
        device.client_activate()
        TOKEN = device.murano_token() or PARAMETERS.get('murano_token') or None
        if _INI_FILE:
            if 'device' not in I.sections():
                I.add_section('device')
            I.set('device', 'murano_token', TOKEN)
            I.write(_INI_FP)
            LOG.critical('TOKEN saved to %s', _INI_FP)
        LOG.critical('TOKEN: %s', TOKEN)

        # -----------------------------------------
        # Define resource management objects
        # -----------------------------------------
        LOG.info("Startup parameters: \n{}"
                 .format(json.dumps(PARAMETERS, indent=2)))
        config_io = ConfigIO(
            device=device,
            **PARAMETERS
        )
        LOG.critical("startup config_io_file: {}".format(config_io.config_file))
        data_queuing = None
        if PARAMETERS.get('queuing'):
            optional_temp = {
                'batch_amount': PARAMETERS.get('queuing_batch_amount'),
                'db_max_size': PARAMETERS.get('queuing_db_max_size'),
                'db_path': PARAMETERS.get('queuing_db_path'),
                'drop_strategy': PARAMETERS.get('queuing_drop_strategy'),
                'record_rate': PARAMETERS.get('queuing_record_rate'),
                'remove_unused_device': PARAMETERS.get('queuing_remove_unused_device')
            }

            # remove key when value is None
            optional = {k: v for k, v in optional_temp.items() if v is not None}
            data_queuing = Queuing(PARAMETERS["murano_host"], PARAMETERS["murano_id"], device, **optional)

        data_in = DataIn(
            config_io=config_io,
            device=device,
            data_queuing=data_queuing,
            **PARAMETERS)
        config_applications = ConfigApplications(
            device=device,
            restart_channels_event=config_io.event_new_config,
            **PARAMETERS
        )
        LOG.critical("startup config_applications_file: {}".format(config_applications.config_file))
        config_mgr_list = [
            config_io,
            config_applications
        ]

        # -----------------------------------------
        # Start Reporting
        # -----------------------------------------
        device.start_client()
        data_in.start()
        config_watcher = ConfigWatcher(
            device=device,
            config_mgr_list=config_mgr_list
        )
        config_watcher.start()

        CRITICAL_THREADS = [
            config_watcher,
            data_in,
        ]
        CRITICAL_THREADS += device.watch_threads
        CRITICAL_THREADS += config_mgr_list

        EDGED_TIMEOUT = self.global_args.get('--edged-timeout')
        def STOP_PROCESS():
            """ Callback for killing edged."""
            LOG.critical("Starting STOP_PROCESS")
            if _INI_FILE:
                ini_file = IniParser(allow_no_value=True)
                ini_file.read(_INI_FP)

                syncable_murano_client_opts = {
                    'murano_id': device.murano_id(),
                    'murano_host': device.murano_host(),
                    'murano_port': device.murano_port(),
                    'murano_token': device.murano_token(),
                    'watchlist': ','.join(DEFAULTS['watchlist'])
                }
                for sect in ini_file.sections():
                    LOG.critical('INI section {}...'.format(sect))
                    if sect == 'device':
                        for opt, val in syncable_murano_client_opts.items():
                            if not ini_file.has_option(sect, opt):
                                ini_file.set(sect, opt, val)
                                LOG.critical('Setting INI option {}.{} = {}'.format(sect, opt, val))
                            # make sure latest token is saved.
                            if opt == 'murano_token':
                                ini_file.set(sect, opt, val)

                syncable_edged_opts = {
                    'config_io_file': config_io.config_file,
                    'config_applications_file': config_applications.config_file
                }
                if not ini_file.has_section('edged'):
                    ini_file.add_section('edged')
                for opt, val in syncable_edged_opts.items():
                    if not ini_file.has_option('edged', opt):
                        ini_file.set('edged', opt, val)
                        LOG.critical('Setting INI option {}.{} = {}'.format('edged', opt, val))

                syncable_queuing_opts = {
                    'queuing_batch_amount': PARAMETERS.get('queuing_batch_amount') or DEFAULTS.get('queuing_batch_amount'),
                    'queuing_db_max_size': PARAMETERS.get('queuing_db_max_size') or DEFAULTS.get('queuing_db_max_size'),
                    'queuing_db_path': PARAMETERS.get('queuing_db_path') or DEFAULTS.get('queuing_db_path'),
                    'queuing_drop_strategy': PARAMETERS.get('queuing_drop_strategy') or DEFAULTS.get('queuing_drop_strategy'),
                    'queuing_record_rate': PARAMETERS.get('queuing_record_rate') or DEFAULTS.get('queuing_record_rate'),
                    'queuing_remove_unused_device': PARAMETERS.get('queuing_remove_unused_device') or DEFAULTS.get('queuing_remove_unused_device'),
                    'queuing': PARAMETERS.get('queuing') or 'False'
                }

                if not ini_file.has_section('queuing'):
                    ini_file.add_section('queuing')
                for opt, val in syncable_queuing_opts.items():
                    ini_file.set('queuing', opt, val)
                ini_file.write(_INI_FP)

            LOG.warning("stopping...")
            device.stop_all()
            config_watcher.stop()
            data_in.stop()
            if PARAMETERS.get('queuing'):
                data_queuing.disable_dequeue()
            running_threads = threading.enumerate()
            for thread in running_threads:
                if hasattr(thread, 'stop'):
                    LOG.critical("Stopping thread: {}".format(thread))
                    if hasattr(thread, 'is_stopped'):
                        if not thread.is_stopped():
                            thread.stop()

            for thread in running_threads:
                try:
                    thread.join(timeout=1.0)
                except RuntimeError:
                    pass
                except Exception:
                    pass

            LOG.critical('TOKEN: %s', TOKEN)
            exit(0)


        class CritWatcher(object):
            """ State holder for critical thread monitoring. """
            StartTime = None
            def critical_threads_ok(self, interval=5.0):
                """ Returns boolean of whether or not any critical thread has died. """
                if time.time() - self.StartTime >= interval:
                    self.StartTime = time.time()
                    for critical_thread in CRITICAL_THREADS:
                        LOG.info(
                            "{} is_alive: {}"
                            .format(critical_thread, critical_thread.is_alive()))
                        if not critical_thread.is_alive():
                            LOG.critical(
                                "\n{}\n\n\n\n{}\n\n\n\n{}\n"
                                .format(
                                    '%'*80,
                                    "\nCRITICAL THREAD <{}> HAS DIED!!!\n".format(critical_thread),
                                    '%'*80
                                    )
                                )
                            return False
                return True

        critwatcher = CritWatcher()
        critwatcher.StartTime = time.time()

        try:
            if EDGED_TIMEOUT:
                EDGED_TIMEOUT = float(EDGED_TIMEOUT)
                BEGINNING = time.time()
                while time.time() < BEGINNING + EDGED_TIMEOUT:
                    if not critwatcher.critical_threads_ok():
                        break
                    time.sleep(1)
                STOP_PROCESS()
            else:
                while True:
                    if not critwatcher.critical_threads_ok():
                        break
                    time.sleep(1)
                STOP_PROCESS()
        except KeyboardInterrupt:
            STOP_PROCESS()
        return

def guess_serial_number():
    try:
        return get_fwprintenv_serial_number()
    except:
        pass

def get_fwprintenv_serial_number():
    return subprocess.check_output("sudo fw_printenv serialnumber | awk -F= '{print $2}'", shell=True).rstrip().decode("utf-8")
