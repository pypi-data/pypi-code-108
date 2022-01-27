"""Copyright (C) 2015-2022 Stack Web Services LLC. All rights reserved."""
import os
import sys
import configparser

settings_file = os.getenv('CONFIG', '/etc/microservice/identity/config.ini')

# setting file read
configuration = configparser.ConfigParser()
if os.path.exists(settings_file):
    configuration.read(settings_file)
else:
    sys.exit('settings file not found CONFIG: %s' % settings_file)
