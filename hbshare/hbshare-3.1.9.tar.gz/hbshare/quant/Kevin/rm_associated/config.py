#!/usr/bin/python
#coding:utf-8
sql_params = {
    "ip": "192.168.223.152",
    "user": "readonly",
    "pass": "c24mg2e6",
    "port": "3306",
    "database": "riskmodel"
}

engine_params = "mysql+pymysql://{}:{}@{}:{}/{}".format(sql_params['user'], sql_params['pass'], sql_params['ip'],
                                                        sql_params['port'], sql_params['database'])

style_names = ["size", "beta", "momentum", "earnyield", "resvol", "growth", "btop", "leverage", "liquidity", "sizenl"]

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

index_name = {"000016": "上证50",
              "000300": "沪深300",
              "000905": "中证500",
              "000852": "中证1000",
              "000985": "上证综指"}
