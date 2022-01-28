from bx.command import Command
from bx import download as dl


class DONSURFCommand(Command):
    """DONSURF - Diffusion ON SURFace

    Available subcommands:
     files:\t\tdownload all `recon-all` outputs (segmentation maps, files, everything...)
     aparc:\t\tcreate an Excel table with all `aparc` measurements
     snapshot:\t\tdownload a snapshot from the `recon-all` pipeline
     report:\t\tdownload the validation report issued by bbrc-validator
     tests:\t\tcreate an Excel table with all automatic tests outcomes from bbrc-validator

    Usage:
     bx donsurf <subcommand> <resource_id>
    """
    nargs = 2
    resource_name = 'DONSURF'
    subcommands = ['aparc', 'snapshot', 'tests', 'report', 'files']
    validator = 'DONSURFValidator'

    def __init__(self, *args, **kwargs):
        super(DONSURFCommand, self).__init__(*args, **kwargs)

    def parse(self):
        subcommand = self.args[0]
        id = self.args[1]  # should be a project or an experiment_id

        if subcommand in ['aparc']:
            df = self.run_id(id, dl.measurements,
                             resource_name=self.resource_name,
                             subfunc=subcommand, max_rows=10)
            df = df.query('measurement == "ThickAvg"')
            self.to_excel(df)

        elif subcommand in ['files', 'report', 'snapshot']:
            self.run_id(id, dl.download, resource_name=self.resource_name,
                        validator=self.validator, destdir=self.destdir,
                        subcommand=subcommand)

        elif subcommand == 'tests':

            version = ['*']
            from bx import validation as val
            df = self.run_id(id, val.validation_scores,
                             validator=self.validator,
                             version=version, max_rows=25)
            self.to_excel(df)
