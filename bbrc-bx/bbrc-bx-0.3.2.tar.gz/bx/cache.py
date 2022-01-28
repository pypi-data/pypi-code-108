
import logging as log
import os.path as op
import pandas as pd
import hashlib
from tqdm import tqdm
from datetime import datetime


def __find_cache__(od, md5, measurements=None):
    from glob import glob

    dates = sorted(set(['_'.join(op.split(e)[-1].split('_')[1:]).split('.')[0]\
        for e in glob(op.join(od, 'bxcache_%s'%md5, 'bxcache*.xlsx'))]))
    print(dates)
    if len(dates) == 0:
        return None
    lastdate = dates[-1]
    if not measurements is None:
        files = [op.join(od, 'bxcache_%s'%md5, 'bxcache_%s_%s.xlsx'%(n, lastdate)) \
            for n in measurements]
    else:
        files = [op.join(od, 'bxcache_%s'%md5, 'bxcache_%s.xlsx'%lastdate)]
    print(files)
    do_exist = True
    for f in files:
        if not op.isfile(f):
            do_exist = False
    if do_exist:
        log.info('Found cache %s'%lastdate)
        return files
    else:
        return None

def __save_files__(od, tables, md5, measurements=None):
    from datetime import datetime
    import os

    if not op.isdir(op.join(od, 'bxcache_%s'%md5)):
        os.mkdir(op.join(od, 'bxcache_%s'%md5))

    dt = datetime.today().strftime('%Y%m%d_%H%M%S')
    if not measurements is None:
        for n, each in zip(measurements, tables):

            fn = 'bxcache_%s_%s.xlsx'%(n, dt)
            fp = op.join(od, 'bxcache_%s'%md5, fn)
            log.info('Saving %s'%fp)
            each.to_excel(fp)

    else:
        fn = 'bxcache_%s.xlsx'%dt
        fp = op.join(od, 'bxcache_%s'%md5, fn)
        log.info('Saving %s'%fp)
        tables.to_excel(fp)

def cache_freesurfer6(c, project_id=None, resource_name='FREESURFER6',
        measurements=['aseg', 'aparc', 'hippoSfVolumes'], od='/tmp',
        force=False, max_rows=None):

    startTime = datetime.now()

    projects = list(set([project_id])) if isinstance(project_id, str) \
        else list(set(project_id))
    config = (projects, resource_name, measurements)
    md5 = hashlib.md5(str(config).encode('utf-8')).hexdigest()
    log.info('MD5: %s'%md5)

    cache = __find_cache__(od, md5, measurements)
    if cache and not force:
        log.info('Loading %s'%str(cache))
        res = [pd.read_excel(e, engine="openpyxl").set_index('subject') for e in cache]

        seconds = datetime.now() - startTime
        m, s = divmod(seconds.total_seconds(), 60)
        h, m = divmod(m, 60)
        elapsedtime = "%d:%02d:%02d" % (h, m, s)
        log.info('Elapsed time: %s'%elapsedtime)
        return res

    experiments = []
    for each in projects:
        a = c.array.experiments(project_id=each, columns=['subject_label'])
        experiments.extend(a.data)

    tables = {'aseg':[], 'aparc':[], 'hippoSfVolumes':[]}
    # Querying FreeSurfer resource -if any- from each experiment

    for e in tqdm(experiments[:max_rows]):
        s = e['subject_label']
        r = c.select.experiment(e['ID']).resource(resource_name)

        if r.exists():
            if 'aseg' in measurements:
                volumes = r.aseg()
                volumes['ID'] = e['ID']
                volumes['subject'] = s
                eTIV = volumes.query('region == "eTIV"')['value'].tolist()[0]
                volumes['eTIV'] = eTIV
                tables['aseg'].append(volumes)

            if 'aparc' in measurements:
                volumes = r.aparc()
                volumes['ID'] = e['ID']
                volumes['subject'] = s
                tables['aparc'].append(volumes)

            if 'hippoSfVolumes' in measurements:
                volumes = r.hippoSfVolumes()
                volumes['ID'] = e['ID']
                volumes['subject'] = s
                eTIV = r.aseg().query('region == "eTIV"')['value'].tolist()[0]
                volumes['eTIV'] = eTIV
                tables['hippoSfVolumes'].append(volumes)

    # Convert to dataframe
    df = [pd.concat(tables[each]).set_index('subject').sort_index() \
        for each in measurements]

    __save_files__(od, df, md5, measurements)

    seconds = datetime.now() - startTime
    m, s = divmod(seconds.total_seconds(), 60)
    h, m = divmod(m, 60)
    elapsedtime = "%d:%02d:%02d" % (h, m, s)
    log.info('Elapsed time: %s'%elapsedtime)
    return df


def cache_ashs(c, project_id=None, resource_name='ASHS',
         od='/tmp', force=False, max_rows=None):

    startTime = datetime.now()

    projects = list(set([project_id])) if isinstance(project_id, str) \
        else list(set(project_id))
    config = (projects, resource_name)
    md5 = hashlib.md5(str(config).encode('utf-8')).hexdigest()
    log.info('MD5: %s'%md5)

    cache = __find_cache__(od, md5)
    if cache and not force:
        log.info('Loading %s'%str(cache))
        res = [pd.read_excel(e, engine="openpyxl").set_index('subject') for e in cache]

        seconds = datetime.now() - startTime
        m, s = divmod(seconds.total_seconds(), 60)
        h, m = divmod(m, 60)
        elapsedtime = "%d:%02d:%02d" % (h, m, s)
        log.info('Elapsed time: %s'%elapsedtime)
        return res

    experiments = []
    for each in projects:
        a = c.array.experiments(project_id=each, columns=['subject_label'])
        experiments.extend(a.data)

    table = []
    # Querying ASHS resource -if any- from each experiment

    for e in tqdm(experiments[:max_rows]):
        s = e['subject_label']
        r = c.select.experiment(e['ID']).resource(resource_name)
        if r.exists():
            try:
                volumes = r.volumes()
                volumes['ID'] = e['ID']
                table.append(volumes)
            except IndexError:
                log.error('Error: check subject %s'%s)
                continue

    # Convert to dataframe
    df = pd.concat(table).set_index('subject').sort_index()
    __save_files__(od, df, md5)

    seconds = datetime.now() - startTime
    m, s = divmod(seconds.total_seconds(), 60)
    h, m = divmod(m, 60)
    elapsedtime = "%d:%02d:%02d" % (h, m, s)
    log.info('Elapsed time: %s'%elapsedtime)
    return df
