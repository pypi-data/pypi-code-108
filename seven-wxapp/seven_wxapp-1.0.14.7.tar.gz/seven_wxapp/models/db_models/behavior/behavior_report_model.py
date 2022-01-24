#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class BehaviorReportModel(BaseModel):
    def __init__(self, db_connect_key='db_wxapp', sub_table=None, db_transaction=None):
        super(BehaviorReportModel, self).__init__(BehaviorReport, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction

    #方法扩展请继承此类

class BehaviorReport:

    def __init__(self):
        super(BehaviorReport, self).__init__()
        self.id = 0  # id
        self.act_id = 0  # act_id
        self.key_name = ""  # 行为字段
        self.key_value = 0  # 行为记录值
        self.create_day = 0  # 日
        self.create_month = 0  # 月
        self.create_year = 0  # 年
        self.create_date = "1900-01-01 00:00:00"  # 创建时间

    @classmethod
    def get_field_list(self):
        return ['id', 'act_id', 'key_name', 'key_value', 'create_day', 'create_month', 'create_year', 'create_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "behavior_report_tb"
