#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class AssetWarnNoticeModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(AssetWarnNoticeModel, self).__init__(AssetWarnNotice, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class AssetWarnNotice:

    def __init__(self):
        super(AssetWarnNotice, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # 应用标识
        self.act_id = 0  # 活动标识
        self.user_id = 0  # 用户标识
        self.open_id = ""  # open_id
        self.user_nick = ""  # 用户昵称
        self.asset_type = 0  # 资产类型(1-次数2-积分3-价格档位)
        self.asset_object_id = ""  # 对象标识
        self.handler_name = ""  # 接口名称
        self.request_code = ""  # 请求代码
        self.log_title = ""  # 标题
        self.info_desc = ""  # 详情
        self.info_json = ""  # 详情json
        self.is_notice = 0  # 是否通知
        self.notice_date = "1900-01-01 00:00:00"  # 通知时间
        self.create_day = 0  # 创建时间天
        self.create_date = "1900-01-01 00:00:00"  # 创建时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'user_id', 'open_id', 'user_nick', 'asset_type', 'asset_object_id', 'handler_name', 'request_code', 'log_title', 'info_desc', 'info_json', 'is_notice', 'notice_date', 'create_day', 'create_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "asset_warn_notice_tb"
