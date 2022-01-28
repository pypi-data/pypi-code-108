from bx.command import Command
from tqdm import tqdm
import pandas as pd
from bx import download as dl
import bx
import logging as log


braak_I_II_ctx = ['entorhinal']
braak_III_IV_ctx = ['fusiform', 'lingual', 'parahippocampal', 'temporalpole',
                    'caudalanteriorcingulate', 'inferiortemporal', 'insula',
                    'isthmuscingulate', 'middletemporal', 'posteriorcingulate',
                    'rostralanteriorcingulate']
braak_V_VI_ctx = ['bankssts', 'caudalmiddlefrontal', 'cuneus',
                  'inferiorparietal', 'lateraloccipital',
                  'lateralorbitofrontal', 'medialorbitofrontal', 'paracentral',
                  'pericalcarine', 'postcentral', 'precentral', 'precuneus',
                  'rostralmiddlefrontal', 'superiorfrontal',
                  'superiorparietal', 'superiortemporal', 'frontalpole',
                  'transversetemporal']

braak_I_II = ['Right-Hippocampus', 'Left-Hippocampus']
braak_III_IV = ['Left-Amygdala', 'Right-Amygdala', 'Left-Thalamus-Proper',
                'Right-Thalamus-Proper']
braak_V_VI = ['Right-Caudate', 'Left-Caudate', 'Right-Putamen',
              'Left-Putamen', 'Right-Accumbens-area',
              'Left-Accumbens-area']


class BraakCommand(Command):
    """Extract morphometric/metabolic measurements based on Braak staging.

    Morphometric values are based on regional volumes or cortical thickness
    as estimated individually by FreeSurfer with respect to each specific stage
     (namely, Braak_I_II, Braak_III_IV and Braak_V_VI). For each of them, the
    mean value in all the regions related to the specific stage is returned.

    Metabolic data refer to FDG update associated with each stage as defined
    by their corresponding ROIs. Masks of each stage were defined based on the
    CerebrA atlas (Manera et al.).

    Available subcommands:
     volumes:\t\tcreates an Excel table with regional volumes for each stage
     thickness:\t\tcreates an Excel table with cortical thickness for each stage
     fdg:\t\tcreates an Excel table with the FDG uptake for each stage

    Usage:
     bx braak <subcommand> <resource_id>

    References:
    - Braak et al., Acta Neuropathol. 2006
    - Schöll et al., Neuron. 2016
    - Manera et al.,  Scientific Data. 2020
    """
    nargs = 2
    subcommands = ['volumes', 'thickness', 'fdg']

    def __init__(self, *args, **kwargs):
        super(BraakCommand, self).__init__(*args, **kwargs)

    def parse(self):
        subcommand = self.args[0]
        id = self.args[1]

        if subcommand in ['volumes', 'thickness']:
            experiments = bx.xnat.collect_experiments(self.xnat, id,
                                                      max_rows=10)
            func = getattr(bx.braak, subcommand)
            df = func(self.xnat, experiments, resource_name='FREESURFER6_HIRES')
            self.to_excel(df)
        elif subcommand == 'fdg':
            df = self.run_id(id, dl.measurements, subfunc=subcommand,
                             resource_name='FDG_QUANTIFICATION', max_rows=10)
            self.to_excel(df)


def volumes(x, experiments, resource_name='FREESURFER6_HIRES'):
    debug = False
    braak_regions = {'Braak_I_II': (braak_I_II, braak_I_II_ctx),
                     'Braak_III_IV': (braak_III_IV, braak_III_IV_ctx),
                     'Braak_V_VI': (braak_V_VI, braak_V_VI_ctx)}

    columns = ['ID', 'region', 'measurement', 'value', 'subject']
    table = []
    for e in tqdm(experiments):
        try:
            res = x.select.experiment(e['ID']).resource(resource_name)
            if not res.exists():
                msg = 'Skipping %s. %s not found.' % (e['ID'], resource_name)
                log.error(msg)
                continue
            aparc = res.aparc()
            sl = e['subject_label']
            aseg = res.aseg()
            for n, (regions, regions_ctx) in braak_regions.items():
                total = []
                for r in regions_ctx:
                    for s in ['left', 'right']:
                        query = 'region == "{region}" & side == "{side}" & \
                                               measurement == "{measurement}"'
                        q = query.format(region=r, side=s, measurement='GrayVol')
                        value = float(aparc.query(q)['value'])
                        total.append(value)
                for r in regions:
                    query = 'region == "{region}" & measurement == "{measurement}"'
                    q = query.format(region=r, measurement='Volume_mm3')
                    value = float(aseg.query(q)['value'])
                    total.append(value)
                row = [e['ID'], n, 'Volume_mm3', sum(total), sl]
                table.append(row)
        except KeyboardInterrupt:
            return pd.DataFrame(table, columns=columns).set_index('ID')
        except Exception as exc:
            if debug:
                raise exc
            else:
                log.error('Failed for %s. Skipping it. (%s)' % (e, exc))

    return pd.DataFrame(table, columns=columns).set_index('ID')


def thickness(x, experiments, resource_name='FREESURFER6_HIRES'):
    debug = False
    braak_regions = [braak_I_II_ctx, braak_III_IV_ctx, braak_V_VI_ctx]

    names = ['Braak_I_II', 'Braak_III_IV', 'Braak_V_VI']
    columns = ['ID', 'Braak region', 'measurement', 'value', 'subject']
    table = []
    for e in tqdm(experiments):
        try:
            res = x.select.experiment(e['ID']).resource(resource_name)
            sl = e['subject_label']
            aparc = res.aparc()
            query = 'region == "{region}" & side == "{side}" & \
                         measurement == "{measurement}"'
            for r, n in zip(braak_regions, names):
                total_surf_area = 0
                weighted_sum = 0
                for b in r:
                    for s in ['left', 'right']:
                        q = query.format(region=b, side=s, measurement='ThickAvg')
                        thickness = float(aparc.query(q)['value'])

                        q = query.format(region=b, side=s, measurement='SurfArea')
                        surf_area = int(aparc.query(q)['value'])

                        weighted_sum += thickness * surf_area
                        total_surf_area += surf_area
                final = weighted_sum / total_surf_area
                row = [e['ID'], n, 'ThickAvg', final, sl]
                table.append(row)
        except KeyboardInterrupt:
            return pd.DataFrame(table, columns=columns).set_index('ID')
        except Exception as exc:
            if debug:
                raise exc
            else:
                log.error('Failed for %s. Skipping it. (%s)' % (e, exc))

    return pd.DataFrame(table, columns=columns).set_index('ID')
