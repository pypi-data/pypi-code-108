import datetime


# noinspection SqlNoDataSourceInspection

def define_start_date(facebook, report, time_increment, account):
    table_name = '%s.%s' % (facebook.schema_name if facebook.schema_name else facebook.config.get('schema_name'), 'report_async')
    query = """
            SELECT max(end_report) as start_date
            FROM %s 
            WHERE account_id='%s' and time_increment='%s' and report_name='%s' and status='Job Completed'
            and created_at>=end_report
            """ % (table_name, account["id"], time_increment, report.get('name'))

    try:
        start_date = facebook.transactional_dbstream.execute_query(query)[0]["start_date"]
    except Exception:
        return None
    if start_date:
        if time_increment == '1':
            return str(datetime.datetime.strptime(str(start_date)[:10], '%Y-%m-%d') - datetime.timedelta(days=1))[:10]
        return str(datetime.datetime.strptime(str(start_date)[:10], '%Y-%m-%d') - datetime.timedelta(days=28))[:10]
    else:
        return None


# noinspection SqlNoDataSourceInspection

def define_updated_time_filter(facebook, report, time_increment, account):
    table_name = '%s.%s_%s' % (facebook.schema_name if facebook.schema_name else facebook.config.get('schema_name'), report.get('name'), time_increment)
    query = """
                SELECT max(updated_time) as updated_time
                FROM %s 
                WHERE account_id='%s'
            """ % (table_name, account["account_id"])
    try:
        updated_time = facebook.dbstream.execute_query(query)[0]["updated_time"]
    except Exception:
        return None
    if updated_time:
        return datetime.datetime.strptime(str(updated_time)[:10], '%Y-%m-%d') - datetime.timedelta(days=28)
    else:
        return None
