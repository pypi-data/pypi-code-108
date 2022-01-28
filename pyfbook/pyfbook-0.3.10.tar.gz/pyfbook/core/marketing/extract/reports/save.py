import datetime


def _clean_data(facebook, data, table_name):
    report_run_ids = list(set([d['report_run_id'] for d in data]))
    query = '''DELETE FROM %s WHERE report_run_id in ('%s')''' % (table_name, "','".join(report_run_ids))
    try:
        facebook.transactional_dbstream.execute_query(query=query)
    except Exception:
        pass


def save_reports(facebook, data, time_increment, report_name):
    if not data:
        return 0
    table_name = '%s.%s' % (facebook.schema_name if facebook.schema_name else facebook.config.get('schema_name'), 'report_async')
    reports = []
    created_at = str(datetime.datetime.now())[:19]
    for r in data:
        r['time_increment'] = time_increment
        r['report_name'] = report_name
        r['status'] = None
        r['result_fetch'] = None
        r['created_at'] = created_at
        r['updated_at'] = created_at
        reports.append(r)
    columns_name = [c for c in reports[0].keys()]
    _clean_data(
        facebook=facebook,
        data=reports,
        table_name=table_name
    )
    facebook.transactional_dbstream.send_data({
        "table_name": table_name,
        "columns_name": columns_name,
        "rows": [[r[c] for c in columns_name] for r in reports]
    }, replace=False)
