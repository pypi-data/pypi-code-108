import logging as log
import os.path as op
import os
from bx.command import Command


class NiftiCommand(Command):
    """Download NIfTI images from a given sequence (`SeriesDesc`).

    Available subcommands:
     usable:\t\tdownload `usable` images (default)
     all:\t\tdownload all images found
    User is then asked for sequence name (ex: T1, T2, DWI). Has to match with
    the one in XNAT (wildcards accepted).

    Usage:
     bx nifti <subcommand> <resource_id>
    """
    nargs = 2
    subcommands = ['usable', 'all']

    def __init__(self, *args, **kwargs):
        super(NiftiCommand, self).__init__(*args, **kwargs)

    def parse(self):
        subcommand = self.args[0]
        id = self.args[1]
        self.sequence_name = 'T1_ALFA1'
        if not os.environ.get('CI_TEST', None):
            s = input('Enter Sequence Name (i.e. Series Description):')
            self.sequence_name = s
        log.info(self.sequence_name)
        self.run_id(id, download_sequence, sequence_name=self.sequence_name,
                    destdir=self.destdir, subcommand=subcommand)


def download_sequence(x, experiments, sequence_name, destdir, subcommand):

    import shutil
    from glob import glob
    import tempfile
    from tqdm import tqdm
    from fnmatch import fnmatch

    nii_extensions = ['nii.gz', 'bvec', 'bval']

    for e in tqdm(experiments):
        log.debug('Experiment %s:' % e['ID'])

        scans = x.select.experiment(e['ID']).scans()
        seq_scans = [s for s in scans if not s.label().startswith('0-') and \
                     fnmatch(s.attrs.get('type'), sequence_name)]
        if subcommand == 'usable':
            seq_scans = [s for s in seq_scans if s.attrs.get('quality') == 'usable']
        log.debug('Found following scans: %s' % seq_scans)

        for s in seq_scans:
            r = s.resource('NIFTI')
            if not r.exists():
                log.error('%s has no NIFTI' % e)
                continue
            wd = tempfile.mkdtemp()

            r.get(dest_dir=wd, extract=True)
            for ext in nii_extensions:
                fp = glob(op.join(wd, 'NIFTI', '*.%s' % ext))
                if len(fp) != 1:
                    if ext == 'nii.gz':
                        log.error('Multiple files found in archive. '
                                  'Skipping %s (%s) folder: %s'\
                                  % (e['ID'], s.label(), op.join(wd, 'NIFTI')))
                    continue
                fp = fp[0]
                fn = '%s_%s_%s_%s.%s' % (e['subject_label'], e['label'],
                                         s.label(), e['ID'], ext)
                log.debug('Saving %s...' % fn)
                shutil.move(fp, op.join(destdir, fn))
            shutil.rmtree(wd)
