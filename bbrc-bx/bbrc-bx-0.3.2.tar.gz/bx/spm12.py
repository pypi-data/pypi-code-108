from bx.command import Command
from bx import download as dl


class SPM12Command(Command):
    """SPM12 - Gray/white matter segmentation

    Available subcommands:
     files:\t\tdownload all `SPM12` outputs (segmentation maps, warp fields, everything...)
     volumes:\t\tcreates an Excel table with GM/WM/CSF volumes
     snapshot:\t\tdownload a snapshot from the segmentation results
     report:\t\tdownload the validation report issued by `SPM12Validator`
     tests:\t\tcreates an Excel table with all automatic tests outcomes from `SPM12`
     rc:\t\tdownloads rc* files (DARTEL imports)

    Usage:
     bx spm12 <subcommand> <resource_id>
    """
    nargs = 2
    resource_name = 'SPM12_SEGMENT'
    subcommands = ['volumes', 'files', 'report', 'snapshot', 'tests', 'rc']
    validator = 'SPM12SegmentValidator'

    def __init__(self, *args, **kwargs):

        super(SPM12Command, self).__init__(*args, **kwargs)

        # SPM12Command is always provided with various arguments
        # We just check that the second (ie. the CLI actual args) has >1 item
        # The last one defines the type of segmentation (T1, T1T2) needed.
        last = args[1][-1] if len(args[1]) > 1 else []
        if isinstance(last, tuple) and len(last) == 2:
            (rn, vn) = last
            self.args.pop(-1)
            self.resource_name = rn
            self.validator = vn

    def parse(self, test=False):
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
                             resource_name=self.resource_name, max_rows=10)
            self.to_excel(df)

        elif subcommand == 'tests':
            version = ['*', '0390c55f']
            from bx import validation as val
            df = self.run_id(id, val.validation_scores,
                             validator=self.validator,
                             version=version, max_rows=25)
            self.to_excel(df)
