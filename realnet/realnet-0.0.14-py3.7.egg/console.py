from pynecone import ProtoCmd


class Console(ProtoCmd):

    def __init__(self):
        super().__init__('console',
                         'realnet console')

    def add_arguments(self, parser):
        parser.add_argument('--json', help="specifies the output format to be json", action="store_true")

    def run(self, args):
        pass