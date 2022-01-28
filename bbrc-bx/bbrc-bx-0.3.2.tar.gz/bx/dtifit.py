from bx.command import Command
from bx import download as dl


class DTIFITCommand(Command):
    """Processing of Diffusion-weighted Imaging data

    Available subcommands:
    maps:\t\tdownload parametric maps (FA, MD, AxD, RD)
    files:\t\tdownload all outputs from the `DTIFIT` pipeline (up to parametric maps)
    report:\t\tdownload the validation report issued by `DTIFITValidator`
    snapshot:\t\tdownload a snapshot with FA map, RGB tensor and TOPUP distortion correction map
    tests:\t\tcreate an Excel table with all automatic tests outcomes from bbrc-validator


    Usage:
     bx dtifit <subcommand> <resource_id>
    """
    nargs = 2
    resource_name = 'TOPUP_DTIFIT'
    subcommands = ['files', 'report', 'snapshot', 'tests', 'maps']
    validator = 'DTIFITValidator'

    def __init__(self, *args, **kwargs):
        super(DTIFITCommand, self).__init__(*args, **kwargs)

    def parse(self):
        subcommand = self.args[0]
        id = self.args[1]  # should be a project or an experiment_id

        if subcommand in ['files', 'report', 'snapshot', 'maps']:
            self.run_id(id, dl.download, resource_name=self.resource_name,
                        validator=self.validator, destdir=self.destdir,
                        subcommand=subcommand)

        elif subcommand == 'tests':
            version = ['*', '4e37c9d0']
            from bx import validation as val
            df = self.run_id(id, val.validation_scores,
                             validator=self.validator,
                             version=version, max_rows=25)
            self.to_excel(df)
