from argparse import ArgumentParser


def super():
    pass


class ArgParser(ArgumentParser):

    def __init__(self):
        """

        Instantiate an argument parser.

        """
        super().__init__(help="Use this option if you'd like the most output from the program into the console you "
                               "can get")

        self.add_argument("--no-alerts", required=False, action='store_true', default=False,
                          help="If you use this flag it will set")

        self.add_argument('--mode', required=False, help='Not used')

        self.add_argument('--port', required=False, action='store', default=None, help='Not used')


def run():
    """

    The main driver for the arguments package, this will call on the ArgParser class and parse our arguments for us

    Returns:
        ArgsParser (object): A parsed ArgParser object which will have the namespace for the program's options.

    """

    # Instantiate our argument parser
    parser = ArgParser()

    # Parse the arguments that were received on session start
    args = parser.parse_args()

    return args

run()
