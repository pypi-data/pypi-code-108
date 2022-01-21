#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
常数配置
"""
# 全站基本状态码：只可引用，禁止新建
INITIAL = 0     # 初态 默认值
ENABLE = 1      # 中间态 可用的 正常的 开启的 激活的
DISABLE = -1    # 中间态 禁止 关闭 失效

STATE1 = ENABLE # 中间态
STATE2 = 2      # 中间态
STATE3 = 3      # 中间态
STATE4 = 4      # 中间态
STATE5 = 5      # 中间态
STATE6 = 6      # 中间态
STATE7 = 7      # 中间态
STATE8 = 8      # 中间态
STATE9 = 9      # 中间态
STATE10 = 10    # 中间态

# 以下常用语具备事务特性的场景
SUCCESS = OK = 100      # 终态（不可逆） 完成 成功
FAIL = DELETE = -100    # 终态（不可逆）删除

######################### 以下根据业务模块，指定不同的变量，引用基本状态码 ##########################

# 模块1
order_init = INITIAL            # 下单
order_confirm = ENABLE          # 确认
order_payment = STATE2          # 已支付
order_payment_fail = STATE3     # 支付失败
order_payment_success = STATE4  # 支付成功，
order_send_init = STATE5        # 代发货
order_send_enable = STATE6      # 已发货
order_send_success = STATE7     # 已签收
order_success = SUCCESS         # 已确认，交易完结
order_fail = DELETE             # 订单关闭，库存恢复

# 用户
user_register = INITIAL     # 待审批
user_confirm = SUCCESS      # 审批通过
user_fail = DISABLE         # 审批未通过
user_dispost = STATE2       # 已禁言
user_delete = DELETE        # 已删除

# 项目包状态
PROJECT_INIT = INITIAL      # 初始化
PROJECT_SELECT = STATE1     # 查询中
PROJECT_SUCCESS = SUCCESS   # 成功
PROJECT_FAIL = DISABLE      # 失败
PROJECT_DELETE = DELETE     # 已删除

############################## 映射关系 #####################################
# 上传文件保存目录
FILE_TYPE2PATH = {1: "case", 2: "files"}

# 文书类型
WENSHU_S6 = {0: "全部", 1: "判决书", 2: "裁定书", 3: "调解书", 4: "决定书", 5: "通知书", 9: "令", 10: "其他"}
# 案件公开类型
WENSHU_S43 = {1: "文书公开", 2: "信息公开"}

# 债务人类型
CASE_INT2STR = {
    1: "个人", 2: "有限责任公司", 3: "股份有限公司", 4: "有限合伙企业",
    5: "外商独资企业", 6: "个人独资企业", 7: "国有独资公司", 8: "其他"
}
CASE_STR2INT = {v: k for k, v in CASE_INT2STR.items()}

# 法律状态
LAW_INT2STR = {
    1: "未诉讼", 2: "诉讼中", 3: "已获生效判决", 4: "执行中", 5: "执行终结",
    6: "执行终本", 7: "执行中止", 8: "执行中止", 9: "破产清算"
}
LAW_STR2INT = {v: k for k, v in LAW_INT2STR.items()}

# 资产类型
ASSETS_MAPING = {
    100: {"name": "土地", "items": {101: "工业用地", 102: "商业用地", 103: "住宅用地", 104: "商住用地", 105: "农业用地", 106: "其它用地"}},
    200: {"name": "房产", "items": {201: "住宅", 202: "商业", 203: "别墅", 204: "厂房", 205: "办公", 206: "在建工程", 207: "酒店", 208: "车位"}},
    300: {"name": "其他不动产", "items": {301: "林权", 302: "其它不动产"}},
    400: {"name": "动产", "items": {401: "机器设备", 402: "存货", 403: "应收账款", 404: "票据", 405: "存款", 406: "股权", 407: "基金", 408: "车辆", 409: "船舶", 410: "飞机", 411: "碳排放权", 412: "其它动产"}},
}
# 后端使用
ASSETS_INT2STR = {}
for item in ASSETS_MAPING.values():
    ASSETS_INT2STR.update(item["items"])
ASSETS_STR2INT = {v: k for k, v in ASSETS_INT2STR.items()}
# 前端使用
ASSETS_MAPING2 = []
for code, item in ASSETS_MAPING.items():
    ASSETS_MAPING2.append({
        "lable": item["name"],
        "value": code,
        "children": [{"lable": v, "value": k} for k, v in item["items"].items()]
    })

# 担保方式
GUARANTEE_INT2STR = {1: "担保", 2: "抵押", 3: "质押", 4: "保证+抵押", 5: "保证+质押", 6: "抵押+质押", 7: "保证+抵押+质押"}
GUARANTEE_STR2INT = {v: k for k, v in GUARANTEE_INT2STR.items()}
# 保证方式
GUARANTEE2_INT2STR = {1: "一般保证", 2: "连带责任保证"}
GUARANTEE2_STR2INT = {v: k for k, v in GUARANTEE2_INT2STR.items()}

# 建筑结构
HOUSESTRUCT_INT2STR = {1: "混合", 2: "钢混", 3: "砖混", 4: "砖木", 5: "钢", 6: "其他"}
HOUSESTRUCT_STR2INT = {v: k for k, v in HOUSESTRUCT_INT2STR.items()}

# 城市对照表
from .city import city_mapping
CITY_INT2STR = {}           # {110000: '北京市', 110100: '东城区', 110200: '西城区', 110300: '崇文区'....}
CITY_STR2INT = {}           # {"北京市": 110000, "东城区": 110100, "西城区": 110200....}
for item in city_mapping:
    CITY_INT2STR[item["code"]] = item["name"]
    CITY_STR2INT[item["name"]] = item["code"]
    for d in item["city"]:
        CITY_INT2STR[d["code"]] = d["name"]
        CITY_STR2INT[d["name"]] = d["code"]
# 返回前端下拉框
CITY_MAPPING2 = city_mapping

# 0否 1是 -1未知
YESORNO_INT2STR = {0: "否", 1: "是", -1: "未知"}
YESORNO_STR2INT = {v: k for k, v in YESORNO_INT2STR.items()}

# 抵（质）押人与贷款人的关系/与债务人关系
RELATION_INT2STR = {1: "法定代表人", 2: "股东", 3: "关联公司", 4: "其他"}
RELATION_STR2INT = {v: k for k, v in RELATION_INT2STR.items()}

# 诉讼时效
lawsuit_state_mp = {0: "已过", 1: "未过"}
lawsuit_state_mp2 = {"已过": 0, "未过": 1}
# 抵押类型
collateral_type_mp = {1: "抵押", 2: "质押"}
collateral_type_mp2 = {"抵押": 1, "质押": 2}
# 土地性质
land_type_mp = {1: "国有", 2: "集体"}
land_type_mp2 = {"国有": 1, "集体": 2}
# 土地获得方式
land_own_type_mp = {1: "出让", 2: "划拨", -1: "未知"}
land_own_type_mp2 = {"出让": 1, "划拨": 2, "未知": -1}
# 房产出租情况 1空置 2自用 3出租 4其他
house_lease_mp = {1: "出租", 2: "自用", 3: "空置", 4: "其他"}
house_lease_mp2 = {v: k for k, v in house_lease_mp.items()}
# 抵前/抵后出租 0抵前 1抵后 -1未知
house_order_mp = {1: "抵前", 2: "抵后", -1: "未知"}
house_order_mp2 = {v: k for k, v in house_order_mp.items()}
# 保证人类型 1 企业 2 自然人
guarantor_ptype_mp = {1: "企业", 2: "自然人"}
guarantor_ptype_mp2 = {v: k for k, v in guarantor_ptype_mp.items()}