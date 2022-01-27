"""sonusai

usage: sonusai [--version] [--help] <command> [<args>...]

The sonusai commands are:
   evaluate     Evaluate model performance
   genft        Generate feature and truth data
   genmix       Generate mixture and truth data
   genmixdb     Generate a mixture database
   gentcst      Generate target configuration from a subdirectory tree
   mkwav        Make WAV files from training data
   predict      Run predict on a trained model

Aaware Sound and Voice Machine Learning Framework. See 'sonusai help <command>'
for more information on a specific command.

"""
from subprocess import call

from docopt import docopt

import sonusai
from sonusai import logger
from sonusai.utils import trim_docstring


def main():
    try:
        command_list = 'evaluate genft genmix genmixdb gentcst mkwav predict'.split()

        args = docopt(trim_docstring(__doc__),
                      version=sonusai.version(),
                      options_first=True)

        command = args['<command>']
        argv = args['<args>']

        if command is None:
            exit(call([__file__, '--help']))
        elif command == 'help':
            if not argv:
                exit(call([__file__, '--help']))
            elif argv[0] in command_list:
                exit(call(['sonusai-{}'.format(argv[0]), '-h']))
            else:
                logger.error("{} is not a SonusAI command. See 'sonusai help'.".format(argv[0]))
                exit()
        elif command in command_list:
            exit(call(['sonusai-{}'.format(command), *argv]))

        logger.error("{} is not a SonusAI command. See 'sonusai help'.".format(command))
        exit()

    except KeyboardInterrupt:
        logger.info('Canceled due to keyboard interrupt')
        exit()


if __name__ == '__main__':
    main()
