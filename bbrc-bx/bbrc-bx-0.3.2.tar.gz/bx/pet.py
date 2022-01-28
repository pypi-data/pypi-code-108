from bx.command import Command
from bx import download as dl
import os
import logging as log


class FdgCommand(Command):
    """18F-fluorodeoxyglucose PET imaging data

    Available subcommands:
     landau:\t\tcreates an Excel table with the Landau's metaROI signature
     maps:\t\tdownload the normalized FDG maps
     tests:\t\tcollect all automatic tests outcomes from `FDGQuantiticationValidator`

    Usage:
     bx fdg <subcommand> <resource_id>

    Reference:
    - Landau et al., Ann Neurol., 2012
    """
    nargs = 2
    subcommands = ['tests', 'landau', 'maps']
    resource_name = 'FDG_QUANTIFICATION'

    def __init__(self, *args, **kwargs):
        super(FdgCommand, self).__init__(*args, **kwargs)

    def parse(self):
        subcommand = self.args[0]
        id = self.args[1]
        if subcommand == 'tests':
            resource_name = 'PetSessionValidator'

            version = ['*', '0390c55f']

            from bx import validation as val
            df = self.run_id(id, val.validation_scores,
                             validator=resource_name,
                             version=version, max_rows=25)
            self.to_excel(df)
        elif subcommand == 'landau':
            df = self.run_id(id, dl.measurements,
                             resource_name=self.resource_name,
                             subfunc=subcommand, max_rows=10)
            self.to_excel(df)
        elif subcommand == 'maps':
            fp = 'static_pet.nii.gz'
            debug = os.environ.get('CI_TEST', None)
            fp = get_filepath(self.resource_name, debug=debug)
            self.run_id(id, download_pet, resource_name=self.resource_name,
                        filename=fp, destdir=self.destdir,
                        subcommand=subcommand)


class FtmCommand(Command):
    """18F-flutemetamol PET imaging data

    Available subcommands:
     centiloids:\t\tcreates an Excel table with centiloid scales
     maps:\t\tdownload the normalized FTM maps
     tests:\t\tcollect all automatic tests outcomes from `FTMQuantiticationValidator`

    Usage:
     bx ftm <subcommand> <resource_id>

    References:
     - Klunk et al, Alzheimers Dement., 2015
    """
    nargs = 2
    subcommands = ['tests', 'centiloids', 'maps']
    resource_name = 'FTM_QUANTIFICATION'

    def __init__(self, *args, **kwargs):
        super(FtmCommand, self).__init__(*args, **kwargs)

    def parse(self):
        resource_name = 'PetSessionValidator'

        subcommand = self.args[0]
        id = self.args[1]
        if subcommand == 'tests':
            version = ['*', '0390c55f']

            from bx import validation as val
            df = self.run_id(id, val.validation_scores,
                             validator=resource_name,
                             version=version, max_rows=25)
            self.to_excel(df)
        elif subcommand == 'centiloids':
            df = self.run_id(id, dl.measurements,
                             resource_name=self.resource_name,
                             subfunc=subcommand, max_rows=10)
            self.to_excel(df)
        elif subcommand == 'maps':
            fp = 'static_pet.nii.gz'
            if not os.environ.get('CI_TEST', None):
                fp = get_filepath(self.resource_name)
            self.run_id(id, download_pet, resource_name=self.resource_name,
                        filename=fp, destdir=self.destdir,
                        subcommand=subcommand)


def get_filepath(resource_name, debug=False):
    s = 'n'
    while s not in ['Y', 'y', 'N', 'n', ''] and not debug:
        s = input('Optimized PET images? [Y]/n ')
    is_optimized = not(s in 'Nn')
    region = 'raw'
    options = ['cgm', 'pons', 'wcbs', 'wc', 'wm', 'raw']
    msg = 'Reference region?\n'\
          ' - cgm: Cerebellar gray matter\n'\
          ' - wcbs: Whole cerebellum + Brain stem\n'\
          ' - pons: Pons\n'\
          ' - wc: Whole cerebellum\n'\
          ' - wm: White matter\n'\
          ' - raw: Raw image (not scaled, not normalized)\n'
    if resource_name.startswith('FDG'):
        msg = msg.replace('Pons\n', 'Pons\n - vermis: Vermis\n')
        options.append('vermis')
    while region not in options and not debug:
        region = input(msg)
        if region not in options:
            m = 'Incorrect option (%s). Please try again.' % region
            print(m)

    fp = ''
    if region == 'raw':
        if is_optimized:
            fp = 'optimized_static_pet.nii.gz'
        else:
            fp = 'static_pet.nii.gz'
    else:
        fp = 'w'
        if is_optimized:
            fp += 'optimized_'
        fp += 'static_pet_scaled_' + region + '.nii.gz'

    return fp


def download_pet(x, experiments, resource_name, filename, destdir, subcommand):

    import os.path as op
    from tqdm import tqdm
    from pyxnat.core.errors import DataError

    for e in tqdm(experiments):
        log.debug('Experiment %s:' % e['ID'])

        r = x.select.experiment(e['ID']).resource(resource_name)
        f = r.file(filename)
        fn = '%s_%s_%s_%s.nii.gz' % (e['subject_label'], e['label'], e['ID'],
                                     filename)
        try:
            f.get(op.join(destdir, fn))
        except DataError as exc:
            log.error('Failed for %s. Skipping it. (%s)' % (e, exc))
