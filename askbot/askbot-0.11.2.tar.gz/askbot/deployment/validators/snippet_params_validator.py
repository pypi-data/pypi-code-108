

class SnippetParamsValidator:
    def __init__(self, console, parser):
        self.console = console
        self.parser = parser
        self.options = parser.parse_args()

