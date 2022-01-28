#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class VersionInfoModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(VersionInfoModel, self).__init__(VersionInfo, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class VersionInfo:

    def __init__(self):
        super(VersionInfo, self).__init__()
        self.id = 0  # id
        self.type_id = 0  # 类型（1消费者端2千牛端）
        self.version_number = ""  # 更新版本号
        self.is_force_update = 0  # 是否强制更新（1是0否）
        self.content = ""  # 更新内容
        self.update_scope = 0  # 更新范围(1-全部,会同步更新到baseinfo表2-指定用户) 取最新记录，如果指定用户取最新记录的值，否则取baseinfo表的值
        self.white_lists = ""  # 更新白名单(多个逗号分隔)
        self.is_release = 0  # 是否发布（1是0否）
        self.release_date = "1900-01-01 00:00:00"  # 发布时间
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 更新时间

    @classmethod
    def get_field_list(self):
        return ['id', 'type_id', 'version_number', 'is_force_update', 'content', 'update_scope', 'white_lists', 'is_release', 'release_date', 'create_date', 'modify_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "version_info_tb"
