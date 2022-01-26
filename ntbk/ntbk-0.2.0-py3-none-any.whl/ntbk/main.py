"""Main entry point into the application"""

# system imports
import sys

# 3rd party imports
import colorama

# app imports
from ntbk import initialize
from ntbk.config import Config
from ntbk.dispatcher import Dispatcher
from ntbk.filesystem import Filesystem
from ntbk.exceptions import InvalidConfigException

def exit_with_err(err):
    """Print the error and exit the application"""
    print(err, file=sys.stderr)
    sys.exit(1)

def run():
    """Run the application"""
    try:
        config = Config()
        filesystem = Filesystem(config)
        colorama.init()
        initialize.init_app(config)
        Dispatcher(config, filesystem).run(sys.argv[1:])
    except InvalidConfigException as err:
        exit_with_err(err)
    except KeyboardInterrupt:
        sys.exit(0)
    # except Exception as err: #pylint: disable=broad-except
    #     exit_with_err(err)

if __name__ == '__main__':
    run()
