
# import json
# import os

# class Config:
#
#     def __init__(self):
#
#         config_dir='//'.join(os.path.abspath(__file__).split('\\')[0:-1])+'//config'
#
#         with open(config_dir+"//Database_Connnection.json", "r") as load_f:
#             self.DBconfig= json.load(load_f)
#         with open(config_dir+"//Columns_Translation.json", "r") as load_f:
#             self.Columns_name_trans =  json.load(load_f)
#             # json.dump(new_dict, f)
#         with open(config_dir+"//JY_Sql.json", "r") as load_f:
#             self.Jy_sql =  json.load(load_f)
#         with open(config_dir+"//Mkr_code.json", "r") as load_f:
#             self.Mkr_code =  json.load(load_f)
#         with open(config_dir+"//IndexType.json", "r") as load_f:
#             self.Index_type= json.load(load_f)

class Config:

    def __init__(self):

        self.DBconfig={'Sql_ip': '192.168.223.152',
                     'Sql_user': 'admin',
                     'Sql_pass': 'mysql',
                     'Database': 'fe_temp_data',
                     'port': '3306'}

        self.Columns_name_trans={'科目代码': 'Code',
                                '科目名称': 'Name',
                                '数量': 'Quant',
                                '单位成本': 'Unit_cost',
                                '成本': 'Cost',
                                '成本占净值%': 'Cost_weight',
                                '市价': 'Price',
                                '市值': 'Mkt_value',
                                '市值占净值%': 'Weight',
                                '估值增值': 'Increased_val',
                                '停牌信息': 'Trading_flg',
                                '币种': 'Currency',
                                '汇率': 'Ex_rate',
                                '权益信息': 'Hd_info'}

        self.Jy_sql = {'sql_indus_a':
                           {'comment': 'join the industry of normal A share with its sec code and name table ',
                             'sql': 'SELECT A.CompanyCode,A.SecuCode,A.SecuAbbr,B.FirstIndustryName,B.XGRQ from HSJY_GG.SecuMain A left join HSJY_GG.LC_ExgIndustry B on A.CompanyCode=B.CompanyCode where B.Standard=24 @@'
                            },
                     'sql_indus_b':
                         {'comment': 'join the industry of  A share in chuangyeban  with its sec code and name table ',
                          'sql': 'SELECT A.CompanyCode,A.SecuCode,A.SecuAbbr,B.FirstIndustryName,B.UpdateTime from HSJY_GG.SecuMain A,HSJY_GP.LC_STIBExgIndustry B where A.CompanyCode=B.CompanyCode and B.Standard=24 @@'
                          },
                     'sql_fin':
                           {'comment': 'join the table LC_DIndicesForValuation and SecuMain to get the financial data',
                            'sql': 'select a.PE,a.PB,a.DividendRatio,a.TradingDay,b.SecuCode,b.SecuAbbr from HSJY_GG.LC_DIndicesForValuation a left join HSJY_GG.SecuMain b on a.InnerCode=b.InnerCode @@  '
                            },
                       'sql_fin_date':
                           {'comment': 'find the available date for in the LC_DIndicesForValuation table ',
                            'sql': "select distinct(TradingDay) from HSJY_GG.LC_DIndicesForValuation where TradingDay>= to_date('{0}','yyyymmdd') and TradingDay <=to_date('{1}','yyyymmdd')  "
                            },
                     'sql_benchmark':
                           {'comment': '',
                             'sql': 'select b.SecuCode,a.INNERCODE,a.WEIGHT,a.ENDDATE from hsjy_gg.LC_IndexComponentsWeight a,HSJY_GG.SecuMain b where a.INNERCODE=b.INNERCODE and IndexCode =@IndexCode @@  '
                            }
                       }

        self.Mkr_code ={'Ash': '11020101',
                         'Asz': '11023101',
                         'cyb': '11024101',
                         'ggt': '11028101',
                         'sgt': '11028301'}

        self.Index_type= {'沪深300': '000300', '中证500': '000905', '中证1000': '000852'}

        self.Asset_type= {'活期存款': '100201',
                         '上交所A股': '11020101',
                         '深交所A股': '11023101',
                         '深交所创业板': '11024101',
                         '上交所科创板': '1102C101',
                         '上交所新股成本': '11020301',
                         '上交所增发成本': '11020401',
                         '上交所非公开发行新股成本': '11020601',
                         '上交所配股成本': '11020701',
                         '深交所新股成本': '11023301',
                         '深交所增发成本': '11023401',
                         '深交所非公开发行新股成本': '11023601',
                         '深交所配股成本': '11023701',
                         '港股通': '11028101',
                         '深港通': '11028301',
                         '债券': '其中债券投资:',
                         '基金': '其中基金投资:',
                         '权证': '其中权证投资:',
                         '其他': '其中其他投资:'}
