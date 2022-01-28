from bx.command import Command
from bx import download as dl


class FreeSurfer7Command(Command):
    """FreeSurfer v7.1.1

    Available subcommands:
     files:\t\t\t\tdownload all `recon-all` outputs (segmentation maps, files, everything...)
     aseg:\t\t\t\tcreate an Excel table with all `aseg` measurements
     aparc:\t\t\t\tcreate an Excel table with all `aparc` measurements
     hippoSfVolumes:\t\t\tsave an Excel table with hippocampal subfield volumes
     snapshot:\t\t\t\tdownload a snapshot from the `recon-all` pipeline
     report:\t\t\t\tdownload the validation report issued by bbrc-validator
     tests:\t\t\t\tcreate an Excel table with all automatic tests outcomes from bbrc-validator

    Usage:
     bx freesurfer7 <subcommand> <resource_id>
    """
    nargs = 2
    resource_name = 'FREESURFER7'
    subcommands = ['aparc', 'aseg', 'hippoSfVolumes', 'snapshot', 'tests',
                   'report', 'files']
    validator = 'FreeSurfer7Validator'

    def __init__(self, *args, **kwargs):
        fs7_subcmds = ['amygNucVolumes', 'brainstem', 'thalamus',
                       'hypothalamus']
        for cmd in fs7_subcmds:
            self.subcommands.append(cmd)
        if self.resource_name == 'FREESURFER7':
            s = 'amygNucVolumes:\t\t\tsave an Excel table with amygdalar volumes\n' \
                '     brainstem:\tsave an Excel table with brainstem substructures volumes\n'\
                '     thalamus:\t\tsave an Excel table with thalamic nuclei volumes\n'\
                '     hypothalamus:\tsave an Excel table with hypothalamic subunits volumes\n'\
                '     hippoSf'
            self.__doc__ = self.__doc__.replace('hippoSf', s)
        super(FreeSurfer7Command, self).__init__(*args, **kwargs)

    def parse(self):
        subcommand = self.args[0]
        id = self.args[1]  # should be a project or an experiment_id

        if subcommand in ['brainstem', 'thalamus', 'hypothalamus']:
            self.resource_name = 'FREESURFER7_EXTRAS'  # switch resource

        if subcommand in ['aparc', 'aseg', 'hippoSfVolumes', 'amygNucVolumes',
                          'brainstem', 'thalamus', 'hypothalamus']:
            import logging as log
            msg = 'FreeSurfer6 has a bug in the computation of some of the'\
                  ' global metrics when analyzing high resolution data'\
                  '(reported values are in voxels not mm3).'\
                  'For consistency those have been excluded from bx results. '\
                  'Source: https://surfer.nmr.mgh.harvard.edu/fswiki/BrainVolStatsFixed'
            if 'HIRES' in self.resource_name:
                log.warning(msg)
            df = self.run_id(id, dl.measurements,
                             resource_name=self.resource_name,
                             subfunc=subcommand, max_rows=10)
            self.to_excel(df)

        elif subcommand in ['files', 'report', 'snapshot']:
            self.subcommand_download()

        elif subcommand == 'tests':

            version = ['##0390c55f', '*']
            from bx import validation as val
            df = self.run_id(id, val.validation_scores,
                             validator=self.validator,
                             version=version, max_rows=25)
            self.to_excel(df)

    def subcommand_download(self):
        subcommand = self.args[0]
        id = self.args[1]

        resource_name = self.resource_name
        validator = self.validator
        if 'hires' in self.command:
            resource_name = 'FREESURFER6_HIRES'
            validator = 'FreeSurferHiresValidator'
        if 'extras' in self.command:
            resource_name = 'FREESURFER7_EXTRAS'
            validator = 'FreeSurfer7ExtrasValidator'

        from bx import download as dl
        self.run_id(id, dl.download, resource_name=resource_name,
                    validator=validator, destdir=self.destdir,
                    subcommand=subcommand)


class FreeSurfer6Command(FreeSurfer7Command):
    nargs = 2
    resource_name = 'FREESURFER6'
    validator = 'FreeSurferValidator'
    __doc__ = FreeSurfer7Command.__doc__.replace('7.1.1', '6.0.0')
    __doc__ = __doc__.replace('freesurfer7', 'freesurfer6')

    def __init__(self, *args, **kwargs):
        super(FreeSurfer6Command, self).__init__(*args, **kwargs)


class FreeSurfer6HiresCommand(FreeSurfer7Command):
    nargs = 2
    resource_name = 'FREESURFER6_HIRES'
    validator = 'FreeSurferHiresValidator'
    __doc__ = FreeSurfer7Command.__doc__.replace('7.1.1',
                                                 '6.0.0 (-hires option)')
    __doc__ = __doc__.replace('freesurfer7', 'freesurfer6hires')

    def __init__(self, *args, **kwargs):
        super(FreeSurfer6HiresCommand, self).__init__(*args, **kwargs)
