"""
货币类指标
"""
import pandas as pd
from datetime import datetime
from hbshare.quant.Kevin.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB
from WindPy import w

w.start()


class Currency:
    def __init__(self, start_date, end_date, is_increment=1):
        self.start_date = start_date
        self.end_date = end_date
        self.is_increment = is_increment
        self.table_name = 'mac_curr'

    def get_currency_data(self):
        """
        货币类数据：M1同比、M2同比、金融机构：短期贷款余额、金融机构：中长期贷款余额、社会融资规模存量同比、社会融资规模存量、
                 7日逆回购利率、贷款市场报价利率(LPR):1年、贷款市场报价利率(LPR):5年、
                 中长期贷款利率:3至5年(含)、人民币存款准备金率:中小型存款类金融机构(月)、人民币存款准备金率:大型存款类金融机构(月)、
                 银行间质押式回购加权利率:7天、
                 基础货币余额、货币乘数
        """
        index_list = ['M0001383', 'M0001385', 'M0043417', 'M0043418', 'M5525763', 'M5525755',
                      'M0041371', 'M0096870', 'M0331299',
                      'M0009815', 'M0043821', 'M0061518',
                      'M0041653',
                      'M0001690', 'M0010131']
        name_dict = {"M0001383": "M1_yoy", "M0001385": "M2_yoy",
                     "M0043417": "short_term_loan_balance", "M0043418": "long_term_loan_balance",
                     "M5525763": "social_finance_yoy", "M5525755": "social_finance_scale",
                     "M0041371": "reverse_repo_7", "M0096870": "LPR_1_year", "M0331299": "LPR_5_year",
                     "M0009815": "long_term_loan_rate",
                     "M0043821": "deposit_reserve_ratio_s", "M0061518": "deposit_reserve_ratio_l",
                     "M0041653": "pledged_repo_7",
                     "M0001690": "currency", "M0010131": "curr_multiplier"}

        res = w.edb(','.join(index_list), self.start_date, self.end_date)
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch currency data error: start_date = {}, end_date = {}".format(self.start_date, self.end_date))
        else:
            if len(res.Data) == 1:
                data = pd.DataFrame(res.Data[0], index=res.Codes, columns=res.Times).T
            else:
                data = pd.DataFrame(res.Data, index=res.Codes, columns=res.Times).T
            data.index.name = 'trade_date'
            data.reset_index(inplace=True)
            data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
            data.rename(columns=name_dict, inplace=True)

        data['currency'] = data['currency'].round(2)
        data['curr_multiplier'] = data['curr_multiplier'].round(2)

        return data

    def get_construct_result(self):
        if self.is_increment == 1:
            data = self.get_currency_data()
            sql_script = "delete from {} where trade_date in ({})".format(
                self.table_name, ','.join(data['trade_date'].tolist()))
            # delete first
            delete_duplicate_records(sql_script)
            # add new records
            WriteToDB().write_to_db(data, self.table_name)
        else:
            sql_script = """
                create table mac_curr(
                id int auto_increment primary key,
                trade_date date not null unique,
                M1_yoy decimal(4, 2),
                M2_yoy decimal(4, 2),
                short_term_loan_balance decimal(10, 2),
                long_term_loan_balance decimal(10, 2),
                social_finance_yoy decimal(4, 2),
                social_finance_scale decimal(6, 2),
                reverse_repo_7 decimal(4, 2),
                LPR_1_year decimal(4, 2),
                LPR_5_year decimal(4, 2),
                long_term_loan_rate decimal(4, 2),
                deposit_reserve_ratio_s decimal(4, 2),
                deposit_reserve_ratio_l decimal(4, 2),
                pledged_repo_7 decimal(6, 4),
                currency decimal(9, 2),
                curr_multiplier decimal(4, 2)) 
            """
            create_table(self.table_name, sql_script)
            data = self.get_currency_data()
            WriteToDB().write_to_db(data, self.table_name)


class CurrencyShibor:
    def __init__(self, start_date, end_date, is_increment=1):
        self.start_date = start_date
        self.end_date = end_date
        self.is_increment = is_increment
        self.table_name = 'mac_curr_shibor'

    def get_currency_data(self):
        """
        货币类数据-SHIBOR: 隔夜、一周、两周、一个月、3个月、6个月、9个月、1年
        """
        index_list = ['M0017138', 'M0017139', 'M0017140', 'M0017141', 'M0017142', 'M0017143', 'M0017144', 'M0017145']
        name_dict = {"M0017138": "SHIBOR_ON", "M0017139": "SHIBOR_1W",
                     "M0017140": "SHIBOR_2W", "M0017141": "SHIBOR_1M",
                     "M0017142": "SHIBOR_3M", "M0017143": "SHIBOR_6M",
                     "M0017144": "SHIBOR_9M", "M0017145": "SHIBOR_1Y"}

        res = w.edb(','.join(index_list), self.start_date, self.end_date)
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch currency data error: start_date = {}, end_date = {}".format(self.start_date, self.end_date))
        else:
            if len(res.Data) == 1:
                data = pd.DataFrame(res.Data[0], index=res.Codes, columns=res.Times).T
            else:
                data = pd.DataFrame(res.Data, index=res.Codes, columns=res.Times).T
            data.index.name = 'trade_date'
            data.reset_index(inplace=True)
            data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
            data.rename(columns=name_dict, inplace=True)

        return data

    def get_construct_result(self):
        if self.is_increment == 1:
            data = self.get_currency_data()
            sql_script = "delete from {} where trade_date in ({})".format(
                self.table_name, ','.join(data['trade_date'].tolist()))
            # delete first
            delete_duplicate_records(sql_script)
            # add new records
            WriteToDB().write_to_db(data, self.table_name)
        else:
            sql_script = """
                create table mac_curr_shibor(
                id int auto_increment primary key,
                trade_date date not null unique,
                SHIBOR_ON decimal(6, 4),
                SHIBOR_1W decimal(6, 4),
                SHIBOR_2W decimal(6, 4),
                SHIBOR_1M decimal(6, 4),
                SHIBOR_3M decimal(6, 4),
                SHIBOR_6M decimal(6, 4),
                SHIBOR_9M decimal(6, 4),
                SHIBOR_1Y decimal(6, 4)) 
            """
            create_table(self.table_name, sql_script)
            data = self.get_currency_data()
            WriteToDB().write_to_db(data, self.table_name)


if __name__ == '__main__':
    Currency('2005-01-01', '2021-06-10', is_increment=0).get_construct_result()
    # CurrencyShibor('2006-10-08', '2021-05-17', is_increment=1).get_construct_result()