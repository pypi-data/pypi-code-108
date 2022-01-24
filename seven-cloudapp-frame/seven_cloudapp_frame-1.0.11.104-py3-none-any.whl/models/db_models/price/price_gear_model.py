#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *


class PriceGearModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(PriceGearModel, self).__init__(PriceGear, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class PriceGear:

    def __init__(self):
        super(PriceGear, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # 应用标识
        self.act_id = 0  # 活动标识
        self.relation_type = 0  # 关联类型：1商品skuid关联2商品id关联
        self.goods_id = ""  # 商品ID
        self.sku_id = ""  # sku_id
        self.price_gear_name = ""  # 档位名称
        self.price_gear_pic = ""  # 档位图片
        self.price = 0  # 价格
        self.is_del = 0  # 是否删除（1是0否）
        self.effective_date = "1900-01-01 00:00:00"  # 有效时间
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 更新时间
        self.remark = ""  # 备注

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'relation_type', 'goods_id', 'sku_id', 'price_gear_name', 'price_gear_pic', 'price', 'is_del', 'effective_date', 'create_date', 'modify_date', 'remark']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "price_gear_tb"
