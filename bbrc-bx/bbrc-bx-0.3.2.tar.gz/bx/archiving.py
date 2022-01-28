from bx.command import Command


class ArchivingCommand(Command):
    """Archiving - used to collect automatic tests from `ArchivingValidator`

    Available subcommands:
     tests:\t\tcreates an Excel table with all automatic tests outcomes from `ArchivingValidator`

    Usage:
     bx archiving <subcommand> <resource_id>
    """
    nargs = 2
    resource_name = 'ArchivingValidator'
    subcommands = ['tests']

    def __init__(self, *args, **kwargs):
        super(ArchivingCommand, self).__init__(*args, **kwargs)

    def parse(self):
        subcommand = self.args[0]
        id = self.args[1]
        if subcommand == 'tests':
            version = ['*', '0390c55f']

            from bx import validation as val
            df = self.run_id(id, val.validation_scores,
                             validator=self.resource_name,
                             version=version, max_rows=25)
            self.to_excel(df)
