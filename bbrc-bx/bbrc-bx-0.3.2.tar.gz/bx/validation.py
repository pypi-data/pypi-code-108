import logging as log
from tqdm import tqdm
import pandas as pd


def collect_reports(x, experiments, validator='ArchivingValidator',
                    version=['toto']):
    reports = {}

    for e in tqdm(experiments):
        try:
            exp = x.select.experiment(e['ID'])
            r = exp.resource('BBRC_VALIDATOR')
            if not r.exists():
                continue
            if len(list(r.files('%s*.json' % validator))) == 0:
                log.error('%s has no %s' % (e['ID'], validator))
                continue
            j = r.tests(validator)

            if 'version' not in j.keys():
                log.warning('Version not found in report %s' % j.keys())
                continue
            if j['version'] not in version and '*' not in version:
                continue
            fields = list(j.keys())
            try:
                for each in ['version', 'generated', 'experiment_id']:
                    fields.remove(each)
            except ValueError:
                msg = 'No valid report found (%s).' % e
                log.error(msg)
                raise Exception(msg)
            reports[e['ID']] = j

        except KeyboardInterrupt:
            return reports

    return reports


def validation_scores(x, experiments, validator, version):
    def build_dataframe(res):
        fields.insert(0, 'ID')
        for each in ['version', 'generated', 'experiment_id']:
            fields.remove(each)
        fields.extend(['version', 'generated'])
        df = pd.DataFrame(res, columns=fields).set_index('ID')
        return df

    res = []
    # Collecting reports of given version(s)
    log.info('Looking for experiments with %s report with versions %s.'
             % (validator, version))
    reports = dict(list(collect_reports(x, validator=validator,
                                        experiments=experiments,
                                        version=version).items()))
    log.info('Now initiating download for %s experiment(s).'
             % len(reports.items()))

    # Creating list of columns (intersection between all reports tests)
    fields = list(list(reports.items())[0][1].keys())
    for e, report in tqdm(reports.items()):
        fields = set(fields).intersection(list(report.keys()))
    fields = list(fields)

    # Compiling data from reports (has_passed from each test)
    for e, report in tqdm(reports.items()):
        try:
            row = [e]
            row.extend([report[f]['has_passed'] for f in fields
                        if f not in ['version', 'generated', 'experiment_id']])
            row.extend([report[f] for f in ['version', 'generated']])
            res.append(row)
        except KeyboardInterrupt:
            return build_dataframe(res)

    # Building DataFrame
    return build_dataframe(res)
