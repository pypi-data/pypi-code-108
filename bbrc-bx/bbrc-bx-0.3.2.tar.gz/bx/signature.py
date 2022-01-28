from bx.command import Command
import logging as log
from nibabel.freesurfer import io
import os.path as op
import bx


class SignatureCommand(Command):
    """Download composite measurements labeled as 'signatures' of Alzheimer's Disease

    Available subcommands:
     jack:\t\tbased on FreeSurfer's cortical thickness and local cortical gray matter volumes
     dickerson:\t\tbased on Dickerson's cortical signatures (see references below)

    Usage:
     bx signature <subcommand> <resource_id>

    Jack's AD signature is calculated in two versions,
    weighted and not weighted. Weighted means that the formula has been
    applied by normalizing each ROI value by local surface area (as explained
    in the papers).
    Not-weighted versions correspond to mean values across regions.

    Examples:

    `bx signature jack` will return Jack's signature, based on thickness and grayvol values.
    `bx signature dickerson` will return AD and aging signatures, based only on
    thickness values as they do not have any "grayvol" version.

    References:
    - Jack et al., Alzheimers Dement. 2017
    - Dickerson et al., Neurology, 2011
    - Bakkour et al., NeuroImage, 2013
    """
    nargs = 2
    subcommands = ['jack', 'dickerson']

    def __init__(self, *args, **kwargs):
        super(SignatureCommand, self).__init__(*args, **kwargs)

    def parse(self):
        subcommand = self.args[0]
        id = self.args[1]  # should be a project or an experiment_id

        from bx import xnat
        experiments = xnat.collect_experiments(self.xnat, id, max_rows=10)

        if subcommand in ['jack']:
            df = signatures(self.xnat, experiments, subcommand,
                            resource_name='FREESURFER6_HIRES')
            self.to_excel(df)
        elif subcommand in ['dickerson']:
            df = signatures(self.xnat, experiments, subcommand,
                            resource_name='FREESURFER6_HIRES')
            q = 'signature == "ad" & weighted or signature == "aging" & weighted'
            self.to_excel(df.query(q))


def __jack_signature__(x, experiment_id, regions, weighted=True,
                       measurement='ThickAvg', resource_name='FREESURFER6_HIRES'):
    e = x.select.experiment(experiment_id)
    r = e.resource(resource_name)
    aparc = r.aparc()

    weighted_sum = 0
    total_surf_area = 0

    query = 'region == "{region}" & side == "{side}" & \
             measurement == "{measurement}"'

    for r in regions:
        for s in ['left', 'right']:
            q = query.format(region=r, side=s, measurement=measurement)
            thickness = float(aparc.query(q)['value'])

            q = query.format(region=r, side=s, measurement='SurfArea')
            surf_area = int(aparc.query(q)['value'])

            weighted_sum += thickness * surf_area if weighted else thickness
            total_surf_area += surf_area

    if weighted:
        final = weighted_sum / total_surf_area
    else:
        final = weighted_sum / (2 * len(regions))

    return final


def __signature__(x, experiment_id, rois_path, weighted=True,
                  resource_name='FREESURFER6_HIRES'):
    import tempfile
    import os
    from glob import glob

    fh, fp = tempfile.mkstemp(suffix='.thickness')
    os.close(fh)
    e = x.select.experiment(experiment_id)
    r = e.resource(resource_name)

    # Cortical thickness map
    f = list(r.files('*lh.thickness'))[0]
    f.get(fp)
    lh_thickness = io.read_morph_data(fp)
    os.remove(fp)

    f = list(r.files('*rh.thickness'))[0]
    f.get(fp)
    rh_thickness = io.read_morph_data(fp)
    os.remove(fp)

    files = glob(op.join(rois_path, '*.label'))
    thickness_sum = 0
    n_regions = len(files)
    n_vertex = 0

    for f in files:
        thickness = 0
        filename = op.basename(f)
        roi = io.read_label(f)
        n_vertex += len(roi)
        if filename.startswith('rh'):
            for vertex in roi:
                thickness += rh_thickness[vertex]
        elif filename.startswith('lh'):
            for vertex in roi:
                thickness += lh_thickness[vertex]

        if weighted:
            thickness_sum += thickness
        else:
            thickness_sum += thickness / len(roi)

    if weighted:
        signature = thickness_sum / n_vertex
    else:
        signature = thickness_sum / n_regions

    return signature


def signature(x, experiment_id, subcommand, resource_name='FREESURFER6_HIRES'):
    import pandas as pd

    columns = ['signature', 'weighted', 'measurement', 'value']
    table = []
    # Jack's signature
    if subcommand == 'jack':
        for weighted in [False, True]:
            for m in ['ThickAvg', 'GrayVol']:
                regions = ['entorhinal', 'inferiortemporal', 'middletemporal',
                           'fusiform']
                res = __jack_signature__(x, experiment_id, regions, weighted,
                                         m, resource_name=resource_name)

                row = ['jack', weighted, m, res]
                table.append(row)
    # ad and Aging signatures
    elif subcommand == 'dickerson':
        for sig in ['ad', 'aging']:
            for m in ['ThickAvg']:
                for weighted in [False, True]:
                    rois_path = op.join(op.dirname(bx.__file__), 'data',
                                        'dickerson', sig)
                    res = __signature__(x, experiment_id, rois_path, weighted,
                                        resource_name='FREESURFER6_HIRES')
                    row = [sig, weighted, m, res]
                    table.append(row)

    return pd.DataFrame(table, columns=columns)


def signatures(x, experiments, subcommand, resource_name='FREESURFER6_HIRES'):
    from tqdm import tqdm
    import pandas as pd

    table = []
    for e in tqdm(experiments):
        log.debug(e)
        try:
            s = e['subject_label']
            e_id = e['ID']
            volumes = signature(x, e_id, subcommand,
                                resource_name=resource_name)

            volumes['subject'] = s
            volumes['ID'] = e['ID']
            table.append(volumes)
        except KeyboardInterrupt:
            return pd.concat(table).set_index('ID').sort_index()
        except Exception as exc:
            log.error('Failed for %s. Skipping it. (%s)' % (e, exc))

    data = pd.concat(table).set_index('ID').sort_index()
    return data
