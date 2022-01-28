from bx.command import Command
from bx import download as dl


class BAMOSCommand(Command):
    """BAMOS (Bayesian MOdel Selection for white matter lesion segmentation)

    Available subcommands:
     files:\t\tdownload all `BAMOS` outputs
     volumes:\t\tcreate an Excel table with global lesion volumes
     layers:\t\tdownload `layer` (i.e. depth) maps
     lobes:\t\tdownload lobar segmentation maps
     stats:\t\tcreate an Excel table with lesions stats per lobe and depth
     snapshot:\t\tdownload a snapshot from the `BAMOS` pipeline
     report:\t\tdownload the validation report issued by `BAMOSValidator`
     tests:\t\tcreate an Excel table with all automatic tests outcomes from bbrc-validator


    Usage:
     bx bamos <subcommand> <resource_id>

    References:
    - Sudre et al., IEEE TMI, 2015
    """
    nargs = 2
    resource_name = 'BAMOS'
    subcommands = ['volumes', 'files', 'layers', 'lobes', 'stats', 'snapshot',
                   'report', 'tests']
    validator = 'BAMOSValidator'

    def __init__(self, *args, **kwargs):
        super(BAMOSCommand, self).__init__(*args, **kwargs)

    def parse(self, test=False):
        subcommand = self.args[0]
        id = self.args[1]

        if subcommand in ['files', 'report', 'snapshot', 'layers', 'lobes']:
            self.run_id(id, dl.download, resource_name=self.resource_name,
                        validator=self.validator, destdir=self.destdir,
                        subcommand=subcommand)

        elif subcommand in ['volumes', 'stats']:
            sf = 'bamos_%s' % subcommand
            df = self.run_id(id, dl.measurements, subfunc=sf,
                             resource_name=self.resource_name, max_rows=10)
            self.to_excel(df)
        elif subcommand == 'tests':
            version = ['*', '4e37c9d0']
            from bx import validation as val
            df = self.run_id(id, val.validation_scores,
                             validator=self.validator,
                             version=version, max_rows=25)
            self.to_excel(df)
