import re
from datetime import datetime, timedelta


class SQLFormat:
    def __init__(self):
        self.tga_template = '''select %s from ta.user_result_cluster_%s as t1 LEFT JOIN ta.v_user_%s as t2 ON t1."#user_id" = t2."#user_id" where cluster_name='%s' and "#account_id" is not null'''
        self.sql_place = {
            # 当天
            'cur_date': datetime.now().strftime('%Y-%m-%d'),
            # 昨天
            'last_date': (datetime.now() + timedelta(hours=-24)).strftime('%Y-%m-%d'),
            # 当前时间
            'cur_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            # 上一小时的时间
            'last_hour': (datetime.now() + timedelta(hours=-1)).strftime('%Y-%m-%d %H:%M:%S'),
            # 七天前的日期
            'seven_day_before': (datetime.now() + timedelta(days=-7)).strftime('%Y-%m-%d'),
            # 七天前的时间
            'seven_day_before_time': (datetime.now() + timedelta(days=-7)).strftime('%Y-%m-%d %H:%M:%S'),
            # 一天前
            'one_day_before': (datetime.now() + timedelta(days=-1)).strftime('%Y-%m-%d'),
            # 一天前的时间
            'one_day_before_time': (datetime.now() + timedelta(days=-1)).strftime('%Y-%m-%d %H:%M:%S'),
            # 28小时前的日期
            'twenty_eight_hours_before_date': (datetime.now() + timedelta(hours=-28)).strftime('%Y-%m-%d'),
            # 28小时前的时间
            'twenty_eight_hours_before_time': (datetime.now() + timedelta(hours=-28)).strftime('%Y-%m-%d %H:%M:%S'),
        }

    # sql params[sql], tga params[fields, game_id, cluster_name]
    def run(self, params):
        if 'sql' in params:
            download_sql = self.sql_format(params['sql'])
        else:
            download_sql = self.tga_format(fields=params['fields'], game_id=params['game_id'],
                                           cluster_name=params['cluster_name'])
        return download_sql

    def sql_format(self, sql):
        placeholder_pattern = re.compile(r'\$\{\w+\}')
        format_arr = placeholder_pattern.findall(sql)

        for placeholder in format_arr:
            format_type = placeholder.split('$', 1)[1].strip('{}')
            if format_type in self.sql_place:
                sql = sql.replace(placeholder, self.sql_place.get(format_type))
        return sql

    def tga_format(self, fields, game_id, cluster_name):
        sql = self.tga_template % (fields, game_id, game_id, cluster_name)
        return sql
