from bx.command import Command
from bx import download as dl
import os
import logging as log


class BASILCommand(Command):
    """BASIL - Bayesian Inference for Arterial Spin Labeling MRI
    Arterial Spin Labeling (ASL) MRI is a non-invasive method for
    the quantification of perfusion.

    Available subcommands:
     perfusion:\t\tcreates an Excel table with global perfusion and arrival-time values.
     stats:\t\tcreates an Excel table with regional perfusion values (in Harvard-Oxford atlas).
     aal:\t\tcreates an Excel table with regional perfusion values (in AAL atlas).
     maps:\t\tdownload the perfusion maps
     files:\t\tdownload all BASIL-ASL outputs (perfusion maps, files, everything...)
     snapshot:\t\tdownload a snapshot from the BASIL-ASL pipeline
     report:\t\tdownload the validation report issued by bbrc-validator
     tests:\t\tcreate an Excel table with all automatic tests outcomes from bbrc-validator

    Usage:
     bx basil <subcommand> <resource_id>

    References:
    - Chappell MA., IEEE Transactions on Signal Processing, 2009.
    """
    nargs = 2
    resource_name = 'BASIL'
    subcommands = ['perfusion', 'aal', 'stats', 'maps', 'files', 'report',
                   'snapshot', 'tests']
    validator = 'BASILValidator'

    def __init__(self, *args, **kwargs):
        super(BASILCommand, self).__init__(*args, **kwargs)

    def parse(self):
        subcommand = self.args[0]
        id = self.args[1]

        if subcommand in ['perfusion', 'stats', 'aal']:
            sf = 'basil_%s' % subcommand
            df = self.run_id(id, dl.measurements, subfunc=sf,
                             resource_name='BASIL', max_rows=10)
            self.to_excel(df)

        elif subcommand == 'maps':
            debug = os.environ.get('CI_TEST', None)
            fp = get_filepath(debug=debug)
            self.run_id(id, download_perfusion, resource_name=self.resource_name,
                        filename=fp, destdir=self.destdir,
                        subcommand=subcommand)

        elif subcommand in ['files', 'report', 'snapshot']:
            self.run_id(id, dl.download, resource_name=self.resource_name,
                        validator=self.validator, destdir=self.destdir,
                        subcommand=subcommand)

        elif subcommand == 'tests':

            version = ['##7f43c4c4', '*']
            from bx import validation as val
            df = self.run_id(id, val.validation_scores,
                             validator=self.validator,
                             version=version, max_rows=25)
            self.to_excel(df)


def get_filepath(debug=False):
    space = ''
    options = ['native_space', 'std_space', 'struct_space']
    msg = 'Which space?\n' \
          ' - native_space: native ASL space\n' \
          ' - std_space: MNI152 standard space \n' \
          ' - struct_space: structural T1 space\n'
    while not space in options and not debug:
        space = input(msg)
        if space not in options:
            m = 'Incorrect option (%s). Please try again.' % space
            print(m)
        else:
            space = space
    fp = '/{}/{}'.format(space, 'perfusion.nii.gz')
    return fp


def download_perfusion(x, experiments, resource_name, filename, destdir, subcommand):

    import os.path as op
    from tqdm import tqdm
    from pyxnat.core.errors import DataError

    for e in tqdm(experiments):
        log.debug('Experiment %s:' % e['ID'])

        r = x.select.experiment(e['ID']).resource(resource_name)
        f = r.file(filename)
        space = filename.split('/')[1]
        fn = '%s_%s_%s_%s_%s.nii.gz' % (e['subject_label'], e['label'], e['ID'], 'perfusion', space)
        try:
            f.get(op.join(destdir, fn))
        except DataError as exc:
            log.error('Failed for %s. Skipping it. (%s)' % (e, exc))
