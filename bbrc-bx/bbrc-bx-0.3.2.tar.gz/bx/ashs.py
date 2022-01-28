from bx.command import Command
from bx import download as dl


class ASHSCommand(Command):
    """ASHS (Hippocampal subfield segmentation)

    Available subcommands:
     files:\t\tdownload all `ASHS` outputs (segmentation maps, volumes, everything...)
     volumes:\t\tcreates an Excel table with all hippocampal subfield volumes
     snapshot:\t\tdownload a snapshot from the `ASHS` pipeline
     report:\t\tdownload the validation report issued by `ASHSValidator`
     tests:\t\tcreates an Excel table with all automatic tests outcomes from `ASHSValidator`

    Usage:
     bx ashs <subcommand> <resource_id>
    """
    nargs = 2
    resource_name = 'ASHS'
    subcommands = ['volumes', 'files', 'report', 'snapshot', 'tests']
    validator = 'ASHSValidator'

    def __init__(self, *args, **kwargs):
        super(ASHSCommand, self).__init__(*args, **kwargs)

    def parse(self):
        subcommand = self.args[0]
        id = self.args[1]  # should be a project or an experiment_id
        if subcommand in ['volumes']:
            df = self.run_id(id, dl.measurements, subfunc=subcommand,
                             resource_name=self.resource_name)
            self.to_excel(df)

        elif subcommand in ['files', 'report', 'snapshot']:
            self.run_id(id, dl.download, resource_name=self.resource_name,
                        validator=self.validator, destdir=self.destdir,
                        subcommand=subcommand)

        elif subcommand == 'tests':
            version = ['*', 'beed8758', 'f80f2b13']
            from bx import validation as val
            df = self.run_id(id, val.validation_scores,
                             validator=self.validator,
                             version=version, max_rows=25)
            self.to_excel(df)
