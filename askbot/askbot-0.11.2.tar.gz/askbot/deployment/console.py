"""Class `Console` is responsible for printing the console output.
"""
from askbot.utils import console

PREAMBLE = """\nDeploying Askbot - Django Q&A forum application
Problems installing? -> please email support@askbot.com

To CANCEL - press Ctr-C.\n"""

def get_sqlite_db_path_prompt(project_dir):
    """Returns prompt string for the sqlite db path"""
    return 'Enter the ' + console.bold('SQLite database file path') + '.\n' + \
        ('If path is relative, %s will be prepended.\n' % project_dir) + \
        'Absolute path will be used as given.'

class Console:
    """Prints messages to the console.
    Before the first message prints a preamble.
    """

    def __init__(self):
        self.preamble_printed = False

    def simple_dialog(self, prompt, required=False, default=None):
        """Simple dialog, if necessary - preceded by the preamble"""
        if not self.preamble_printed:
            self.print_preamble()
            self.preamble_printed = True
        return console.simple_dialog(prompt, required=required, default=default)

    def choice_dialog(self, prompt, choices=None, default=None):
        """Choice dialog, if necessary - preceded by the preamble"""
        if not self.preamble_printed:
            self.print_preamble()
            self.preamble_printed = True
        return console.choice_dialog(prompt, choices=choices, default=default)

    def print_line(self, line):
        """Prints a line, preceded by the preamble,
        if necessary."""
        if not self.preamble_printed:
            self.print_preamble()
            self.preamble_printed = True
        print(line)

    def print_error(self, line):
        """Prints error, preceded by a preamble, if it is the first message"""
        if not self.preamble_printed:
            self.print_preamble()
            self.preamble_printed = True
        print(console.RED + line + console.RESET)

    @classmethod
    def print_preamble(cls):
        """Prints a deployer preamble"""
        print(console.YELLOW + PREAMBLE + console.RESET)

    @classmethod
    def print_postamble(cls, options):
        """Help text describing the next steps"""
        print("""Done. Please find further instructions at http://askbot.org/doc/
You will probably want to edit the settings.py file.""")

        if options['database_engine'] == 'postgresql_psycopg2':
            try:
                import psycopg2 #pylint: disable=import-outside-toplevel,unused-import
            except ImportError:
                print('\nNEXT STEPS: install python binding for postgresql')
                print('pip install psycopg2-binary\n')
        elif options['database_engine'] == 'mysql':
            try:
                import _mysql #pylint: disable=import-outside-toplevel,unused-import
            except ImportError:
                print('\nNEXT STEP: install python binding for mysql')
                print('pip install mysql-python\n')
