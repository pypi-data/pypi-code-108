"""phases
Usage:
  phases [-v] ...
  phases create [-f] [-p <projectfile>] [-o <outputdir>] [-v]
  phases run [-p <projectfile>] [-c <configfile>] [-o <outputdir>] [-v]
  phases run <phaseName> [-p <projectfile>] [-c <configfile>] [-g <gridfile>] [-r] [--csv <csvLogFile>] [-o <outputdir>] [--set <configvalues> ...] [-v]
  phases test [<testdir>] [-p <projectfile>] [-c <configfile>] [-o <outputdir>] [-tp <testpattern>] [-v] [-f]
  phases -h | --help
  phases --version
Options:
  -h --help                         Show this screen.
  --version                         Show version.
  -p <projectfile>                  project file [default: project.yaml]
  -o <outputdir>                    output directory [default: .]
  -f                                force to overwrite existing files
  -v                                verbose output
  -c <configfile>                   use userconfig (project.<configfile>.yaml)
  -g <gridfile>                     use a grid file
  -t <testdir>                      test directory [default: tests]
  -tp <testpattern>                 pattern to look for tests [default: test.py]
  --csv <csvLogFile>                path to an csvfile that should be used for logging
  --set <configvalues>              overwrite single config values
  -r                                resume grid search from last line in csvLogFile
Examples:
  phases --version
  phases create
  phases create -f
  phases create -f -o myOutput -p myProject.yaml
Help:
  For help using this tool, please open an issue on the Gitlab repository: https://gitlab.com/tud.ibmt/phases
"""

from inspect import getmembers, isclass
from docopt import docopt
from phases import __version__ as VERSION
import phases.commands
from phases.util.Logger import Logger, LogLevel
from phases.commands.Base import Base
import pyPhases

# import phases.commands as commands


def main():
    """Main CLI entrypoint."""
    options = docopt(__doc__, version=VERSION)

    if options["-v"]:
        Logger.verboseLevel = LogLevel.DEBUG
        pyPhases.util.Logger.verboseLevel = LogLevel.DEBUG

    Logger.log("Phases %s with pyPhases %s (Log level: %s)" % (VERSION, pyPhases.__version__, Logger.verboseLevel), "phases")

    # Here we'll try to dynamically match the command the user is trying to run
    # with a pre-defined command class we've already created.
    for (k, v) in options.items():
        if hasattr(phases.commands, k) and v:
            module = getattr(phases.commands, k)
            commands = getmembers(module, isclass)
            commands = list(filter(lambda c: c[0] != "Base" and issubclass(c[1], Base), commands))

            commandName, command = commands.pop()  # get last defined class to skip imports
            Logger.log("Run Command %s" % (commandName), "phases", LogLevel.DEBUG)
            command = command(options)
            command.run()
