#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class ErpRelationModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(ErpRelationModel, self).__init__(ErpRelation, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class ErpRelation:

    def __init__(self):
        super(ErpRelation, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # 应用标识
        self.app_key = ""  # 应用密钥(商家实例化生成的app_key)
        self.store_name = ""  # 店铺名称
        self.is_release = 0  # 是否发布(1是0否)
        self.start_date = "1900-01-01 00:00:00"  # 开始时间
        self.end_date = "1900-01-01 00:00:00"  # 结束时间
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.sync_date = "1900-01-01 00:00:00"  # 同步时间
        self.return_date = "1900-01-01 00:00:00"  # 回传时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'app_key', 'store_name', 'is_release', 'start_date', 'end_date', 'create_date', 'sync_date', 'return_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "erp_relation_tb"
