from bx.command import Command
from bx import download as dl


class ANTSCommand(Command):
    """ANTS - Advanced Normalization Tools

    Available subcommands:
     files:\t\tdownload all `ANTS` outputs
     snapshot:\t\tdownload a snapshot from the `ANTS` pipeline
     report:\t\tdownload the validation report issued by `ANTSValidator`
     tests:\t\tcreates an Excel table with all automatic tests outcomes from `ANTSValidator`

    Usage:
     bx ants <subcommand> <resource_id>
    """
    nargs = 2
    resource_name = 'ANTS'
    subcommands = ['files', 'report', 'snapshot', 'tests']
    validator = 'ANTSValidator'

    def __init__(self, *args, **kwargs):
        super(ANTSCommand, self).__init__(*args, **kwargs)

    def parse(self):
        subcommand = self.args[0]
        id = self.args[1]  # should be a project or an experiment_id

        if subcommand in ['files', 'report', 'snapshot']:
            self.run_id(id, dl.download, resource_name=self.resource_name,
                        validator=self.validator, destdir=self.destdir,
                        subcommand=subcommand)

        elif subcommand == 'tests':
            version = ['*', '0390c55f']

            from bx import validation as val
            df = self.run_id(id, val.validation_scores,
                             validator=self.validator,
                             version=version, max_rows=25)
            self.to_excel(df)
