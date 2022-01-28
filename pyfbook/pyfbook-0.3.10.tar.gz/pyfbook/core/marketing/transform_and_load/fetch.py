import datetime
import hashlib
import numpy as np

import pandas as pd

from pyfbook.SystemUser import SystemUser
from pyfbook.core.marketing.extract.api import get_report_status, get

time_increment_mapping = {
    "month": "month",
    "day": "1",
    "week": "week",
    "quarter": "quarter",
    "year": "year",
    "lifetime": "maximum",
    "maximum": "maximum"
}
SPECIAL_ACTIONS = ["video_10_sec_watched_actions"]


def treat_actions(row):
    actions = row.get('actions')
    if actions:
        for action in actions:
            row["action_" + action["action_type"].replace('.', '_')] = action["value"]
        del row['actions']
    return row


def treat_action_values(row):
    actions = row.get('action_values')
    if actions:
        for action in actions:
            row["action_" + action["action_type"].replace('.', '_') + '_value'] = action["value"]
        del row['action_values']
    return row


def treat_special_action(row, action_name):
    action = row.get(action_name)
    if action:
        row[action_name] = action[0]["value"]
    return row


def make_date(date_start, time_increment):
    if time_increment:
        return date_start
    print('Error time increment not specified in make_date function')
    exit()


def make_batch_id(date, account_id, campaign_id=None, adset_id=None, ad_id=None):
    chi = "_".join(k for k in [str(campaign_id), str(adset_id), str(ad_id)])
    return hashlib.sha224((date + str(account_id) + str(chi)).encode()).hexdigest()


def check_and_fetch_reports(facebook):
    print("Start fetching reports...")
    table_name = '%s.%s' % (facebook.schema_name if facebook.schema_name else facebook.config.get('schema_name'), 'report_async')
    created_at_min = str(datetime.datetime.now() + datetime.timedelta(hours=-3))[:19]
    all_status = ['Job Completed', 'Job Failed', 'Job Skipped', 'Job Deleted']
    query = '''SELECT * FROM %s WHERE (status not in ('%s') or status is NULL or result_fetch is NULL) and created_at >= '%s' ''' % (
        table_name, "','".join(all_status), created_at_min)
    all_reports = facebook.transactional_dbstream.execute_query(query=query)
    job_not_completed_yet = False
    if not all_reports:
        return job_not_completed_yet
    for r in all_reports:
        if r["status"] != 'Job Completed':
            result = get_report_status(
                system_user=SystemUser.get(facebook=facebook, _id=r["app_system_user_id"]),
                endpoint=r['report_run_id'],
                params={}
            )
            status = result['async_status']
        else:
            status = r["status"]
        if status == 'Job Completed':
            data = _fetch_report(facebook=facebook, r=r)
            _send_data_fetch(
                data=data,
                time_increment=r["time_increment"],
                report_name=r["report_name"],
                facebook=facebook
            )
            r["result_fetch"] = str(datetime.datetime.now())[:19]
        else:
            job_not_completed_yet = True
            r["result_fetch"] = None
        r["status"] = status
        _update_report_status(r, facebook=facebook)
    return job_not_completed_yet


def _fetch_report(facebook, r):
    data = get(
        system_user=SystemUser.get(facebook=facebook, _id=r["app_system_user_id"]),
        endpoint=str(r['report_run_id']) + '/insights',
        params={}
    )
    result_data = []
    for row in data:
        row['date'] = make_date(row['date_start'], r["time_increment"])
        row['batch_id'] = make_batch_id(row['date'], account_id=row['account_id'], campaign_id=row.get("campaign_id"),
                                        adset_id=row.get("adset_id"), ad_id=row.get("ad_id"))
        row = treat_actions(row)
        row = treat_action_values(row)
        for e in SPECIAL_ACTIONS:
            row = treat_special_action(row, action_name=e)
        result_data.append(row)
    return result_data


def _send_data_fetch(data, time_increment, report_name, facebook):
    if not data:
        return 0
    dict_data = pd.json_normalize(data, sep='__').replace({np.nan: None}).to_dict(
        orient='records'
    )
    columns_name = [c for c in dict_data[0].keys()]
    table_name = '%s.%s_%s' % (facebook.schema_name if facebook.schema_name else facebook.config.get('schema_name'), report_name, time_increment)
    _clean_data_fetch(facebook, dict_data, table_name)
    facebook.dbstream.send_data(data={
        "table_name": table_name,
        "columns_name": columns_name,
        "rows": [[r[c] for c in columns_name] for r in dict_data]
    }, replace=False)


def _clean_data_fetch(facebook, dict_data, table_name):
    batch_ids = list(set([d['batch_id'] for d in dict_data]))
    query = '''DELETE FROM %s WHERE batch_id in ('%s')''' % (table_name, "','".join(batch_ids))
    try:
        facebook.dbstream.execute_query(query=query)
    except Exception:
        pass


def _update_report_status(report, facebook):
    table_name = '%s.%s' % (facebook.schema_name if facebook.schema_name else facebook.config.get('schema_name'), 'report_async')
    updated_at = str(datetime.datetime.now())[:19]

    # noinspection SqlNoDataSourceInspection
    query = '''
              UPDATE %s
              SET updated_at = '%s' ,
              status = '%s',
              result_fetch = '%s'
              WHERE report_run_id = %s
    ''' % (
        table_name, updated_at, report["status"], report["result_fetch"], report["report_run_id"])
    facebook.transactional_dbstream.execute_query(query)
