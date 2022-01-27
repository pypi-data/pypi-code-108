from __future__ import unicode_literals
import atexit
import errno
import logging
import os
import threading
import time

from appdynamics import config
from appdynamics.lang import str
from appdynamics.lib import default_log_formatter, mkdir
from appdynamics.agent.core import logs
from appdynamics.agent.models.frames import get_formatted_stack


class DiagnosticsService(threading.Thread):
    name = 'DiagnosticsService'
    daemon = True
    agent_logger = logs.setup_logger('appdynamics.agent')
    logger = logs.setup_logger('appdynamics.agent.diagnostics')

    commands = {
        'b': 'print_active_bts',
        'c': 'print_current_config',
        'd': 'toggle_debug',
        't': 'print_tracebacks',
    }

    def __init__(self, agent):
        super(DiagnosticsService, self).__init__()
        self.agent = agent

    def is_running(self):
        return True

    def run(self):
        try:
            path = os.path.join(config.AGENT_BASE_DIR, 'diagnostics', '%d' % os.getpid())  # process-specific path.
            mkdir(os.path.dirname(path))  # ensure the directory exists.
            self.open_fifo(path)
            self.configure_logger()

            fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
            atexit.register(os.close, fd)

            while self.is_running():
                time.sleep(0.5)  # this determines how fast we respond to commands vs how much work we do.

                try:
                    commands = str(os.read(fd, 10))  # this number denotes how many commands we can process at once.
                except OSError as exc:
                    if exc.errno == errno.EAGAIN:  # this occurs when the pipe is being written to.
                        continue
                    raise

                if commands:
                    self.parse_commands(commands)
        except:
            self.agent_logger.exception('Error in diagnostics service.  Diagnostic commands are disabled for this '
                                        'agent process.')

    def open_fifo(self, path):
        if os.path.exists(path):
            os.remove(path)  # `mkfifo` fails if the file exists.

        os.mkfifo(path)
        atexit.register(os.remove, path)

    def configure_logger(self):
        path = logs.get_log_filename() + '.diagnostics'
        filehandler = logging.FileHandler(path, delay=True)  # don't create the log file unless the fifo is used.
        filehandler.setLevel(logging.INFO)
        filehandler.setFormatter(default_log_formatter)

        self.logger.propagate = False
        self.logger.addHandler(filehandler)
        self.logger.setLevel(logging.INFO)

    def parse_commands(self, commands):
        for command in commands.rstrip():
            if command in self.commands:
                command_name = self.commands[command]
                try:
                    command_func = getattr(self, command_name)
                except AttributeError:
                    self.logger.error('Command failed; not implemented: %s' % command_name)
                else:
                    try:
                        command_func()
                    except:
                        self.logger.exception('Command failed with exception: %s' % command_name)
            else:
                self.logger.warning('Command does not exist: %s' % command)

    def print_tracebacks(self):
        output = ''
        for thread in threading.enumerate():
            output += 'Traceback for thread <%s(%s, %s%s)>:\n' % (thread.__class__.__name__, thread.name,
                                                                  'daemon ' if thread.daemon else '', thread.ident)
            output += ''.join(get_formatted_stack(thread.ident))
        self.logger.info(output)

    def toggle_debug(self):
        if logs.debug_enabled(self.agent_logger):
            logs.disable_debug(self.agent_logger)
            self.logger.info('Debug logging disabled.')
        else:
            logs.enable_debug(self.agent_logger)
            self.logger.info('Debug logging enabled.')

    def print_current_config(self):
        self.logger.info('Current config:\n%s' % self.agent.config_svc.config)

    def print_active_bts(self):
        active_bts = self.agent.active_bts
        if not active_bts:
            self.logger.info('No active BTs.')
            return

        output = 'Active BTs:\n'
        output += '\n'.join('On thread %s - %s' % (bt.thread, bt) for bt in active_bts)  # pylint: disable=no-member
        self.logger.info(output)
