import logging as log
import os


def scandate(x, experiment_id, series_desc='T1_ALFA1'):
    """ Given an experiment_id and a SeriesDescription, returns the acquisition
    date extracted from the first DICOM of the matching scanself.
    If multiple scans found, takes the one with the highest SeriesNumber."""

    columns = ['xsiType', 'xnat:imagescandata/type', 'xnat:imagescandata/ID']
    scans = x.array.scans(experiment_id=experiment_id, columns=columns).data
    t1_scans = {e['xnat:imagescandata/id']: e for e in scans
                if e['xnat:imagescandata/type'] == series_desc}

    if len(t1_scans.items()) == 0:
        msg = 'No T1 found for %s: %s. Trying with all of them.'\
              % (experiment_id, [e['xnat:imagescandata/id'] for e in scans])
        log.warning(msg)
        t1_scans = {e['xnat:imagescandata/id']: e for e in scans
                    if not e['xnat:imagescandata/id'].startswith('OT-')
                    and not e['xnat:imagescandata/id'].startswith('O-')}

    max_nb = sorted(t1_scans.keys())[-1]
    log.debug('Found scan: %s' % max_nb)

    scan = x.select.experiment(experiment_id).scan(max_nb)
    r = scan.resource('DICOM')

    return r.scandate()


def collect_scandates(x, experiments):

    def __create_table__(data):
        import pandas as pd
        columns = ('ID', 'label', 'subject_label', 'scandate')
        df = pd.DataFrame(data, columns=columns)
        df['scandate'] = pd.to_datetime(df['scandate'])
        df = df.set_index('ID').sort_index()
        return df

    from tqdm import tqdm

    collected_data = []
    max_rows = 25 if os.environ.get('CI_TEST', None) else None

    for e in tqdm(experiments[:max_rows]):
        try:
            log.debug('Experiment ID: %s Subject label: %s'
                      % (e['ID'], e['subject_label']))

            row = [e['ID'], e['label'], e['subject_label']]
            d = scandate(x, e['ID'])
            row.append(d)
            collected_data.append(row)

        except KeyboardInterrupt:
            return __create_table__(collected_data)
        except Exception as exc:
            log.error('Failed with %s. Skipping it. (%s)' % (e['ID'], exc))
            continue

    return __create_table__(collected_data)
