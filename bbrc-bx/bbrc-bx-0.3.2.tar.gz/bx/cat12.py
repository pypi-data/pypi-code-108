from bx.command import Command
from bx import download as dl


class CAT12Command(Command):
    """CAT12 - Gray/white matter segmentation

    Available subcommands:
     files:\t\tdownload all `CAT12` outputs (segmentation maps, warp fields, everything...)
     volumes:\t\tcreates an Excel table with GM/WM/CSF volumes
     snapshot:\t\tdownload a snapshot from the segmentation results
     report:\t\tdownload the validation report issued by `CAT12Validator`
     tests:\t\tcreates an Excel table with all automatic tests outcomes from `CAT12Validator`

    Usage:
     bx cat12 <subcommand> <resource_id>
    """
    nargs = 2
    resource_name = 'CAT12_SEGMENT'
    subcommands = ['volumes', 'files', 'report', 'snapshot', 'tests', 'rc']
    validator = 'CAT12SegmentValidator'

    def __init__(self, *args, **kwargs):
        super(CAT12Command, self).__init__(*args, **kwargs)

    def parse(self):
        subcommand = self.args[0]
        id = self.args[1]

        if subcommand in ['files', 'report', 'snapshot']:
            self.run_id(id, dl.download, resource_name=self.resource_name,
                        validator=self.validator, destdir=self.destdir,
                        subcommand=subcommand)

        elif subcommand in ['rc']:
            self.run_id(id, dl.download, resource_name=self.resource_name,
                        validator=self.validator, destdir=self.destdir,
                        subcommand='rc')

        elif subcommand == 'volumes':
            df = self.run_id(id, dl.measurements, subfunc=subcommand,
                             resource_name=self.resource_name)
            self.to_excel(df)

        elif subcommand == 'tests':
            version = ['*']
            from bx import validation as val
            df = self.run_id(id, val.validation_scores,
                             validator=self.validator,
                             version=version, max_rows=25)
            self.to_excel(df)
