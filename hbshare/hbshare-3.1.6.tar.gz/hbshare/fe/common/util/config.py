#!/usr/bin/python
#coding:utf-8
Q_MAP = {
    "day": 250.0,
    "week": 52.0,
    "month": 12.0,
    "season": 4,
    "semi": 2,
    "year": 1
}

style_name = [
    "size", "beta", "momentum", "earnyield", "resvol", "growth", "btop", "leverage", "liquidity", "sizenl"]

industry_name = {
    'zx': {
        '房地产': 'RealEstate',
        '通信': 'TeleCom',
        '建筑': 'Build',
        '基础化工': 'BasicChem',
        '医药': 'Medicine',
        '电子元器件': 'EleComp',
        '商贸零售': 'CommeTrade',
        '电力设备': 'ElecEqp',
        '纺织服装': 'Textile',
        '传媒': 'Media',
        '轻工制造': 'LightManu',
        '交通运输': 'Transport',
        '汽车': 'Car',
        '食品饮料': 'FoodBever',
        '机械': 'Machine',
        '家电': 'HouseApp',
        '石油石化': 'Petroleum',
        '建材': 'BuildMaterial',
        '电力及公用事业': 'PowerUtil',
        '有色金属': 'NonFerMetal',
        '餐饮旅游': 'CaterTour',
        '钢铁': 'IronSteel',
        '综合': 'Conglomerates',
        '农林牧渔': 'ArgiForest',
        '计算机': 'Computer',
        '煤炭': 'Coal',
        '国防军工': 'AeroDef',
        '非银行金融': 'NonBankFinan',
        '银行': 'Bank'
    },
    'sw':
        {
        '银行': 'Bank',
        '房地产': 'RealEstate',
        '医药生物': 'Health',
        '交通运输': 'Transportation',
        '采掘': 'Mining',
        '有色金属': 'NonFerMetal',
        '家用电器': 'HouseApp',
        '休闲服务': 'LeiService',
        '机械设备': 'MachiEquip',
        '建筑装饰': 'BuildDeco',
        '商业贸易': 'CommeTrade',
        '建筑材料': 'CONMAT',
        '汽车': 'Auto',
        '纺织服装': 'Textile',
        '食品饮料': 'FoodBever',
        '电子': 'Electronics',
        '计算机': 'Computer',
        '轻工制造': 'LightIndus',
        '公用事业': 'Utilities',
        '通信': 'Telecom',
        '农林牧渔': 'AgriForest',
        '化工': 'CHEM',
        '传媒': 'Media',
        '钢铁': 'IronSteel',
        '非银金融': 'NonBankFinan',
        '电气设备': 'ELECEQP',
        '国防军工': 'AERODEF',
        '综合': 'Conglomerates',
        }
}

factor_map_dict = {"size": "规模", "beta": "Beta", "momentum": "动量", "resvol": "波动率", "btop": "估值",
                   "earnyield": "盈利", "growth": "成长", "leverage": "杠杆", "sizenl": "非线性规模", "liquidity": "流动性"}

industry_cluster_dict = {"大金融": ["银行", "非银金融", "房地产"],
                         "消费": ["家用电器", "食品饮料", "医药生物", "休闲服务", "农林牧渔", "商业贸易", "纺织服装"],
                         "TMT": ["电子", "计算机", "传媒", "通信"],
                         "周期": ["钢铁", "采掘", "有色金属", "化工", "建筑装饰", "建筑材料"],
                         "制造": ["公用事业", "交通运输", "机械设备", "汽车", "电气设备", "轻工制造"]}

industry_cluster_dict_new = {"大金融": ["银行", "非银金融", "房地产"],
                             "消费": ["家用电器", "食品饮料", "医药生物", "社会服务", "农林牧渔", "商贸零售", "纺织服饰", "美容护理"],
                             "TMT": ["电子", "计算机", "传媒", "通信"],
                             "周期": ["钢铁", "煤炭", "有色金属", "基础化工", "石油石化", "建筑装饰", "建筑材料"],
                             "制造": ["公用事业", "交通运输", "机械设备", "汽车", "电力设备", "轻工制造", "环保"]}


cta_factors = ['tsmom_d1', 'tsmom_d2', 'tsmom_d3', 'tsmom_d5', 'tsmom_d10', 'tsmom_d20', 'tsmom_d30',
               'carry_d20_q70', 'tsbasismom_d5', 'tsbasismom_d20']

cta_factor_map_dict = {"rev_short": "短期反转", "tendency_medium": "中短期趋势", "tendency_long": "中长期趋势",
                       "roll_return": "展期收益", "basis_mom_short": "短期基差动量", "basis_mom_long": "中长期基差动量"}

sql_params = {
    "ip": "192.168.223.152",
    "user": "readonly",
    "pass": "c24mg2e6",
    "port": "3306",
    "database": "riskmodel"
}

engine_params = "mysql+pymysql://{}:{}@{}:{}/{}".format(sql_params['user'], sql_params['pass'], sql_params['ip'],
                                                        sql_params['port'], sql_params['database'])


industry_names = {
        '银行': 'Bank',
        '房地产': 'RealEstate',
        '医药生物': 'Health',
        '交通运输': 'Transportation',
        '采掘': 'Mining',
        '有色金属': 'NonFerMetal',
        '家用电器': 'HouseApp',
        '休闲服务': 'LeiService',
        '机械设备': 'MachiEquip',
        '建筑装饰': 'BuildDeco',
        '商业贸易': 'CommeTrade',
        '建筑材料': 'CONMAT',
        '汽车': 'Auto',
        '纺织服装': 'Textile',
        '食品饮料': 'FoodBever',
        '电子': 'Electronics',
        '计算机': 'Computer',
        '轻工制造': 'LightIndus',
        '公用事业': 'Utilities',
        '通信': 'Telecom',
        '农林牧渔': 'AgriForest',
        '化工': 'CHEM',
        '传媒': 'Media',
        '钢铁': 'IronSteel',
        '非银金融': 'NonBankFinan',
        '电气设备': 'ELECEQP',
        '国防军工': 'AERODEF',
        '综合': 'Conglomerates'
}