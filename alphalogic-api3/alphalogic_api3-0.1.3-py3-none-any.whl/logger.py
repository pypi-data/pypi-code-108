# -*- coding: utf-8 -*-
import os
import sys
from logging import getLogger, StreamHandler, Formatter, getLevelName, CRITICAL
from logging.handlers import RotatingFileHandler
from alphalogic_api3 import options


class Logger(object):
    def __init__(self):
        log = getLogger('')

        if options.args.log_level == 'off':
            log.setLevel(CRITICAL)  # otherwise warning message 'no handlers'
        else:
            log.setLevel(getLevelName(options.args.log_level.upper()))

            if not os.path.isdir(options.args.log_directory):
                os.makedirs(options.args.log_directory)

            fh = RotatingFileHandler(os.path.join(options.args.log_directory, "stub.log"),
                                     maxBytes=options.args.log_max_file_size,
                                     backupCount=options.args.log_max_files)
            fh.setLevel(getLevelName(options.args.log_level.upper()))

            formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)

            log.addHandler(fh)

            # Use console for log output
            if not (options.args.noconsole or os.getenv('NOCONSOLE') == '1'):
                console = sys.stderr
                if console is not None:
                    # Logging to console and file both
                    console = StreamHandler(console)
                    console.setLevel(getLevelName(options.args.log_level.upper()))
                    console.setFormatter(formatter)
                    log.addHandler(console)


log = getLogger('')
