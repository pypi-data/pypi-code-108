#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class StatQueueModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(StatQueueModel, self).__init__(StatQueue, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class StatQueue:

    def __init__(self):
        super(StatQueue, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # 应用标识
        self.act_id = 0  # 活动标识
        self.module_id = 0  # 活动模块标识
        self.user_id = 0  # 用户标识
        self.open_id = ""  # open_id
        self.key_name = ""  # key名称
        self.key_value = 0  # key值
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.process_count = 0  # 处理次数
        self.process_result = ""  # 处理结果
        self.process_date = "1900-01-01 00:00:00"  # 处理时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'module_id', 'user_id', 'open_id', 'key_name', 'key_value', 'create_date', 'process_count', 'process_result', 'process_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "stat_queue_tb"
