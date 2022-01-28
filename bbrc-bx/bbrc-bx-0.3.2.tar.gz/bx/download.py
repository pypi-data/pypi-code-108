import os
import os.path as op
import logging as log
from tqdm import tqdm


def download(x, experiments, resource_name, validator, destdir, subcommand):
    """Collect resources from a given set of experiments, given a resource
    name, a validator name, a destination folder and a subcommand.

    Examples of subcommand are: files, report, snapshot, rc, layers/lobes,
    maps"""

    if len(experiments) > 1:
        log.warning('Now initiating download for %s experiments.'
                    % len(experiments))
        experiments = tqdm(experiments)
    for e in experiments:
        log.debug(e)
        try:
            kwargs = {'session_id': e['ID'],
                      'subject_label': e['subject_label'],
                      'validator': validator,
                      'debug': False}
            pattern = '%s_' % subcommand.capitalize()
            kwargs['pattern'] = pattern

            subcommands = {'files': __dl_files__,
                           'report': __dl_report__,
                           'snapshot': __dl_snap__,
                           'rc': __dl_rc__,
                           'maps': __dl_maps__,
                           'layers': __dl_bamos__,
                           'lobes': __dl_bamos__}

            if subcommand in subcommands.keys():
                fp = __download__(x, e, resource_name, destdir,
                                  subcommands[subcommand], **kwargs)
            else:
                raise Exception('Invalid subcommand (%s).' % subcommand)

        except KeyboardInterrupt:
            return

    if len(experiments) == 1 and fp is not None:
        log.info('Saving it in %s' % fp)


def __download__(x, e, resource_name, destdir, func, **kwargs):
    debug = kwargs.get('debug', False)
    e_id = e['ID']
    log.debug(e_id)
    e = x.select.experiment(e_id)
    r = e.resource(resource_name)
    if not r.exists():
        log.error('%s has no %s resource' % (e_id, resource_name))
        return
    if debug:
        fp = func(e, r, destdir, **kwargs)
    else:
        try:
            fp = func(e, r, destdir, **kwargs)
        except Exception as exc:
            log.error('%s failed. Skipping (%s).' % (e_id, exc))
            return
    return fp


def __dl_report__(e, r, destdir, **kwargs):
    v = e.resource('BBRC_VALIDATOR')
    f = v.pdf(kwargs['validator'])
    fp = op.join(destdir, f.label())
    f.get(dest=fp)
    return fp


def __dl_files__(e, r, destdir, **kwargs):
    e_id = kwargs['session_id']
    validator = kwargs['validator']

    dd = op.join(destdir, e_id)
    if op.isdir(dd):
        msg = '%s (%s) already exists. Skipping folder creation.' % (dd, e_id)
        log.error(msg)
    else:
        os.mkdir(dd)
    r.get(dest_dir=dd)

    kwargs['validator'] = validator
    __dl_report__(e, r, dd, **kwargs)

    return destdir


def __dl_maps__(e, r, destdir, **kwargs):
    r.download_maps(destdir)
    return destdir


def __dl_snap__(e, r, destdir, **kwargs):
    e_id = kwargs['session_id']
    r = e.resource('BBRC_VALIDATOR')
    fp = op.join(destdir, '%s.jpg' % e_id)
    fp = r.download_snapshot(kwargs['validator'], fp)
    return ', '.join(fp)


def __dl_rc__(e, r, destdir, **kwargs):
    subject_label = kwargs['subject_label']
    e_id = kwargs['session_id']
    validator = kwargs['validator']

    r.download_rc(destdir)
    v = e.resource('BBRC_VALIDATOR')
    if v.exists():
        fp = op.join(destdir, '%s_%s.jpg' % (subject_label, e_id))
        try:
            v.download_snapshot(validator, fp)
        except Exception as exc:
            log.error('%s has no %s (%s)' % (e_id, validator, exc))
    else:
        log.warning('%s has not %s' % (e, validator))
    return destdir


def __dl_bamos__(e, r, destdir, **kwargs):
    pattern = kwargs['pattern']
    subject_label = kwargs['subject_label']
    e_id = kwargs['session_id']
    f = list(r.files('%s*' % pattern))[0]
    pattern = pattern.lower().rstrip('_')
    fp = op.join(destdir,
                 '%s_%s_%s.nii.gz' % (subject_label, e_id, pattern))
    f.get(fp)
    return fp


def __fix_volumes__(volumes):
    """Remove incorrect volumes by FREESURFER6_HIRES as mentioned in the
    following page.

    Reference: https://surfer.nmr.mgh.harvard.edu/fswiki/BrainVolStatsFixed
    """
    measurements = ['BrainSegVol', 'BrainSegVolNotVent', 'SupraTentorialVol',
                    'lhCerebralWhiteMatterVol', 'rhCerebralWhiteMatterVol',
                    'CerebralWhiteMatterVol', 'TotalGrayVol', 'SubCortGrayVol',
                    'SupraTentorialVolNotVent', 'MaskVol', 'MaskVol-to-eTIV',
                    'BrainSegVol-to-eTIV', 'lhCortexVol', 'rhCortexVol',
                    'CortexVol']
    volumes = volumes.drop(volumes.query('region.isin(@measurements)').index)
    return volumes


def __braak_fdg__(x, e_id, r):
    import bx
    import numpy as np
    import pandas as pd
    import tempfile
    import nibabel as nib
    resource_name = 'FDG_QUANTIFICATION'
    fh, fp = tempfile.mkstemp(suffix='.nii.gz')
    os.close(fh)
    r = x.select.experiment(e_id).resource(resource_name)
    f = r.file('woptimized_static_pet_scaled_vermis.nii.gz')
    f.get(fp)

    regions_dir = op.join(op.dirname(bx.__file__), 'data', 'braak')

    columns = ['Braak_I_II', 'Braak_III_IV', 'Braak_V_VI']
    df = pd.DataFrame(index=[e_id], columns=columns)
    for region in columns:
        atlas_fp = op.join(regions_dir, '%s.nii.gz' % region)
        atlas_im = nib.load(atlas_fp)
        atlas = np.array(atlas_im.dataobj)
        m = np.array(nib.load(fp).dataobj)
        assert (m.shape == atlas.shape)
        n_labels = list(np.unique(atlas))
        res = {label: np.mean(m[atlas == label]) for label in n_labels}
        df[region] = res[n_labels[1]]
    os.remove(fp)
    return df


def __perfusion__(x, e_id, r):
    import bx
    import numpy as np
    import pandas as pd
    import tempfile
    import nibabel as nib
    resource_name = 'BASIL'
    fh, fp = tempfile.mkstemp(suffix='.nii.gz')
    os.close(fh)
    r = x.select.experiment(e_id).resource(resource_name)
    f = r.file('/std_space/perfusion_calib.nii.gz')
    f.get(fp)
    regions = ['Background', 'Precentral_L', 'Precentral_R', 'Frontal_Sup_2_L',
               'Frontal_Sup_2_R', 'Frontal_Mid_2_L', 'Frontal_Mid_2_R',
               'Frontal_Inf_Oper_L', 'Frontal_Inf_Oper_R', 'Frontal_Inf_Tri_L',
               'Frontal_Inf_Tri_R', 'Frontal_Inf_Orb_2_L',
               'Frontal_Inf_Orb_2_R', 'Rolandic_Oper_L', 'Rolandic_Oper_R',
               'Supp_Motor_Area_L',	'Supp_Motor_Area_R', 'Olfactory_L',
               'Olfactory_R', 'Frontal_Sup_Medial_L', 'Frontal_Sup_Medial_R',
               'Frontal_Med_Orb_L',	'Frontal_Med_Orb_R', 'Rectus_L',
               'Rectus_R', 'OFCmed_L', 'OFCmed_R', 'OFCant_L', 'OFCant_R',
               'OFCpost_L',	'OFCpost_R', 'OFClat_L', 'OFClat_R', 'Insula_L',
               'Insula_R', 'Cingulate_Ant_L', 'Cingulate_Ant_R',
               'Cingulate_Mid_L', 'Cingulate_Mid_R', 'Cingulate_Post_L',
               'Cingulate_Post_R', 'Hippocampus_L', 'Hippocampus_R',
               'ParaHippocampal_L', 'ParaHippocampal_R', 'Amygdala_L',
               'Amygdala_R', 'Calcarine_L', 'Calcarine_R', 'Cuneus_L',
               'Cuneus_R', 'Lingual_L', 'Lingual_R', 'Occipital_Sup_L',
               'Occipital_Sup_R', 'Occipital_Mid_L', 'Occipital_Mid_R',
               'Occipital_Inf_L', 'Occipital_Inf_R', 'Fusiform_L',
               'Fusiform_R', 'Postcentral_L', 'Postcentral_R',
               'Parietal_Sup_L', 'Parietal_Sup_R', 'Parietal_Inf_L',
               'Parietal_Inf_R', 'SupraMarginal_L',	'SupraMarginal_R',
               'Angular_L',	'Angular_R', 'Precuneus_L',	'Precuneus_R',
               'Paracentral_Lobule_L', 'Paracentral_Lobule_R',	'Caudate_L',
               'Caudate_R', 'Putamen_L', 'Putamen_R', 'Pallidum_L',
               'Pallidum_R', 'Thalamus_L', 'Thalamus_R', 'Heschl_L',
               'Heschl_R', 'Temporal_Sup_L', 'Temporal_Sup_R',
               'Temporal_Pole_Sup_L', 'Temporal_Pole_Sup_R', 'Temporal_Mid_L',
               'Temporal_Mid_R', 'Temporal_Pole_Mid_L',	'Temporal_Pole_Mid_R',
               'Temporal_Inf_L', 'Temporal_Inf_R', 'Cerebelum_Crus1_L',
               'Cerebelum_Crus1_R', 'Cerebelum_Crus2_L', 'Cerebelum_Crus2_R',
               'Cerebelum_3_L', 'Cerebelum_3_R', 'Cerebelum_4_5_L',
               'Cerebelum_4_5_R', 'Cerebelum_6_L', 'Cerebelum_6_R',
               'Cerebelum_7b_L', 'Cerebelum_7b_R', 'Cerebelum_8_L',
               'Cerebelum_8_R', 'Cerebelum_9_L', 'Cerebelum_9_R',
               'Cerebelum_10_L', 'Cerebelum_10_R', 'Vermis_1_2', 'Vermis_3',
               'Vermis_4_5', 'Vermis_6', 'Vermis_7', 'Vermis_8', 'Vermis_9',
               'Vermis_10']

    df = pd.DataFrame()
    atlas_fp = op.join(op.dirname(bx.__file__), 'data', 'aal2', 'AAL2.nii')
    atlas_im = nib.load(atlas_fp)
    atlas = np.array(atlas_im.dataobj)
    m = np.array(nib.load(fp).dataobj)
    assert (m.shape == atlas.shape)
    n_labels = list(np.unique(atlas))
    df['region'] = regions
    df['ID'] = [e_id] * len(n_labels)
    perf_values = []
    for label in n_labels:
        perf_values.append(np.mean(m[atlas == label]))
    df['value'] = perf_values
    os.remove(fp)
    return df


def measurements(x, experiments, subfunc, resource_name='FREESURFER6',
                 debug=False):
    """ Collect measurements for a set of experiments by calling some specific
    pyxnat resource-based function (e.g. aseg, aparc, centiloids, etc)"""
    from tqdm import tqdm
    import pandas as pd

    table = []
    for e in tqdm(experiments):
        log.debug(e)
        try:
            s = e['subject_label']
            e_id = e['ID']
            r = x.select.experiment(e_id).resource(resource_name)
            if not r.exists():
                log.error('%s has no %s resource' % (e_id, resource_name))
                continue

            if subfunc == 'aparc':
                volumes = r.aparc()
                if resource_name.endswith('_HIRES'):
                    volumes = __fix_volumes__(volumes)
            elif subfunc == 'aseg':
                volumes = r.aseg()
                if resource_name.endswith('_HIRES'):
                    volumes = __fix_volumes__(volumes)
            elif subfunc == 'centiloids':
                c = r.centiloids(optimized=True)
                volumes = pd.DataFrame([c], columns=[subfunc])
            elif subfunc == 'landau':
                v1 = r.landau_signature(optimized=True,
                                        reference_region='vermis')
                v2 = r.landau_signature(optimized=True,
                                        reference_region='pons')
                volumes = pd.concat([v1, v2])
            elif subfunc == 'hippoSfVolumes':
                volumes = r.hippoSfVolumes(mode='T1')
            elif subfunc == 'amygNucVolumes':
                volumes = r.amygNucVolumes()
            elif subfunc == 'bamos_volumes':
                volumes = pd.DataFrame([r.volume()], columns=['volume'])
            elif subfunc == 'bamos_stats':
                volumes = r.stats()
            elif subfunc == 'volumes':
                volumes = r.volumes()
                if isinstance(volumes, dict):
                    volumes = pd.DataFrame(volumes, index=[s])
            elif subfunc == 'fdg':
                volumes = __braak_fdg__(x, e_id, r)
            elif subfunc == 'basil_perfusion':
                volumes = r.perfusion()
            elif subfunc == 'basil_stats':
                volumes = r.stats()
            elif subfunc == 'basil_aal':
                volumes = __perfusion__(x, e_id, r)
            elif subfunc in ['brainstem', 'thalamus', 'hypothalamus']:
                cmd = {'brainstem': 'brainstem_substructures_volumes',
                       'thalamus': 'thalamic_nuclei_volumes',
                       'hypothalamus': 'hypothalamic_subunits_volumes'}
                volumes = eval('r.{}()'.format(cmd[subfunc]))
            volumes['subject'] = s
            volumes['ID'] = e['ID']
            table.append(volumes)
        except KeyboardInterrupt:
            return pd.concat(table).set_index('ID').sort_index()
        except Exception as exc:
            if debug:
                raise exc
            else:
                log.error('Failed for %s. Skipping it. (%s)' % (e, exc))

    data = pd.concat(table).set_index('ID').sort_index()
    return data
