# *********************************************************************
# This Original Work is copyright of 51 Degrees Mobile Experts Limited.
# Copyright 2019 51 Degrees Mobile Experts Limited, 5 Charlotte Close,
# Caversham, Reading, Berkshire, United Kingdom RG4 7BY.
#
# This Original Work is licensed under the European Union Public Licence (EUPL)
# v.1.2 and is subject to its terms as set out below.
#
# If a copy of the EUPL was not distributed with this file, You can obtain
# one at https://opensource.org/licenses/EUPL-1.2.
#
# The 'Compatible Licences' set out in the Appendix to the EUPL (as may be
# amended by the European Commission) shall be deemed incompatible for
# the purposes of the Work and the provisions of the compatibility
# clause in Article 5 of the EUPL shall not apply.
#
# If using the Work as, or as part of, a network application, by
# including the attribution notice(s) required under Article 5 of the EUPL
# in the end user terms of the application under an appropriate heading,
# such notice(s) shall fulfill the requirements of that article.
# ********************************************************************

from datetime import datetime
import logging

class Logger:
    
    """!
    Logging for a Pipeline

    """

    def __init__(self, min_level="error", settings = {}):

        """!
        Create a logger

        @type minLevel: str|list
        @param minLevel: Logging level ("debug", "info", "warning", "error", "critical")

        """

        self.allowed_levels = ["debug", "info", "warning", "error", "critical"]

        self.min_level = min_level

        # enable this level in logging to be output (system default is 'warning')

        logging.basicConfig(level=getattr(logging, min_level.upper()))

        self.min_level = self.allowed_levels.index(str(min_level).lower())
        
        self.settings = settings

    def log(self, level, message):

        """!
        Log a message

        @type level: string
        @param level: The level of log message

        @type message: string
        @param message: The content of log message

        """

        level_index = self.allowed_levels.index(str(level).lower())

        if level_index >= self.min_level:
            now = datetime.now()

            log = {"time": now.strftime("%Y-%m-%d, %H:%M:%S"), "level": level, "message": message}
            self.log_internal(level, log)


    def log_internal(self, level, log):

        """!
        Internal logging function overridden by specific loggers

        @type level: string
        @param level: The level of log message

        @type log: dict
        @param log: The body of log entry
        
        """

        if level == 'debug':
            logging.debug(log)

        elif level == 'info':
            logging.info(log)

        elif level == 'warning':
            logging.warning(log)

        elif level == 'error':
            logging.error(log)

        elif level == 'critical':
            logging.critical(log)

        return
