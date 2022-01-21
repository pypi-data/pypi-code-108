"""
主观股多的估值表分析
"""
import os
import datetime
import pandas as pd
import numpy as np
import hbshare as hbs
from hbshare.quant.Kevin.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB
from sqlalchemy import create_engine
from hbshare.quant.Kevin.rm_associated.config import engine_params
from hbshare.fe.common.util.config import industry_name, industry_cluster_dict
import plotly
import plotly.graph_objs as go
import pyecharts.options as opts
from pyecharts.charts import Bar, Timeline
import plotly.figure_factory as ff
from hbshare.db.simu import valuation


# from plotly.offline import plot as plot_ly

# plotly.offline.init_notebook_mode(connected=True)


def plot_render(plot_dic, width=1200, height=600, **kwargs):
    kwargs['output_type'] = 'div'
    plot_str = plotly.offline.plot(plot_dic, **kwargs)
    print('%%angular <div style="height: %ipx; width: %spx"> %s </div>' % (height, width, plot_str))

# def plot_render(plot_dic, width=1200, height=600, **kwargs):
#     data=plot_dic['data']
#     layout=plot_dic['layout']
#     fig = go.Figure(data=data, layout=layout)
#     fig.show()

class HoldingExtractor:
    def __init__(self, table_name,fund_name,is_increment=1,data_path=None,fund_code=None,date_list=None):
        self.data_path = data_path
        self.table_name = table_name
        self.fund_name = fund_name
        self.is_increment = is_increment
        self.fund_code=fund_code
        self.date_list=date_list
        self.total_asset_dmlist=['资产类合计:','资产合计']
        self.net_asset_dmlist=['基金资产净值:','资产净值','资产资产净值:']
        self.debt_dmlist=['负债类合计:']
        if(data_path is not None):
            self._load_portfolio_weight()

    @staticmethod
    def _shift_date(date):
        trade_dt = datetime.datetime.strptime(date, '%Y%m%d')
        pre_date = (trade_dt - datetime.timedelta(days=30)).strftime('%Y%m%d')

        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
            pre_date, date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
        df['isWeekEnd'] = df['isWeekEnd'].fillna(0).astype(int)
        df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)

        trading_day_list = df[df['isOpen'] == 1]['calendarDate'].tolist()

        return trading_day_list[-1]

    def valuation_data2DB(self,jjdm,date_list,fund_name):

        portfolio_weight_list = []
        for date in date_list:
            data=valuation.get_prod_valuation_by_jjdm_gzrq(jjdm,date)
            if(data.empty):
                print("data for {0} missed,continue...".format(date))
                continue
            date = self._shift_date(str(date))
            columns_map=dict(zip(['kmdm','sz','kmmc'],['科目代码','市值','科目名称']))

            data.rename(columns=columns_map,inplace=True)

            for dm in self.total_asset_dmlist:
                if(len(data[data['科目代码'] == dm])>0):
                    total_asset = float(data[data['科目代码'] ==dm]['市值'].values[0])
                    break

            net_asset=0
            for dm in self.net_asset_dmlist:
                if(len(data[data['科目代码'] == dm])>0):
                    net_asset = float(data[data['科目代码'] == dm]['市值'].values[0])
                    break

            if(net_asset==0):
                for dm in self.debt_dmlist:
                    if (len(data[data['科目代码'] == dm]) > 0):
                        debt = float(data[data['科目代码'] == dm]['市值'].values[0])
                        net_asset=total_asset-debt
                        break

            leverage = total_asset / net_asset
            # A股
            sh = data[data['科目代码'].str.startswith('11020101')]
            sz = data[data['科目代码'].str.startswith('11023101')]
            cyb = data[data['科目代码'].str.startswith('11024101')]
            kcb = data[data['科目代码'].str.startswith('1102C101')]
            equity_a = pd.concat([sh, sz, cyb, kcb], axis=0)
            # sh1 = data[data['科目代码'].str.startswith('11021101')]
            # sz1 = data[data['科目代码'].str.startswith('11021201')]
            # cyb1 = data[data['科目代码'].str.startswith('11021501')]
            # kcb1 = data[data['科目代码'].str.startswith('1102D201')]
            # xsg = data[data['科目代码'].str.startswith('11028401')]
            # equity_cr = pd.concat([sh1, sz1, cyb1, kcb1, xsg], axis=0)
            # equity_a = pd.concat([equity_a, equity_cr], axis=0)
            equity_a['len'] = equity_a['科目代码'].apply(lambda x: len(x))
            equity_a = equity_a[equity_a['len'] > 8]
            equity_a['ticker'] = equity_a['科目代码'].apply(lambda x: x[-6:])
            equity_a['weight'] = equity_a['市值'].astype(float) / net_asset
            equity_a = equity_a.rename(columns={"科目名称": "sec_name"})[['ticker', 'sec_name', 'weight']]
            # 港股
            hk1 = data[data['科目代码'].str.startswith('11028101')]
            hk2 = data[(data['科目代码'].str.startswith('11028201')) | (data['科目代码'].str.startswith('11028301'))]
            equity_hk = pd.concat([hk1, hk2], axis=0)
            equity_hk['len'] = equity_hk['科目代码'].apply(lambda x: len(x))
            equity_hk = equity_hk[equity_hk['len'] > 8]
            equity_hk['ticker'] = equity_hk['科目代码'].apply(lambda x: x[-6:])
            equity_hk['科目名称'] = equity_hk['科目名称'].apply(lambda x: x.strip())  # add
            equity_hk['weight'] = equity_hk['市值'].astype(float) / net_asset
            equity_hk = equity_hk.rename(columns={"科目名称": "sec_name"})[['ticker', 'sec_name', 'weight']]
            equity_hk = equity_hk.groupby(['sec_name', 'ticker'])['weight'].sum().reset_index()
            # 债券
            tmp = data[data['科目代码'] == '1103']
            if tmp.empty:
                bond_df = pd.DataFrame()
            else:
                bond_ratio = tmp['市值'].astype(float).values[0] / net_asset
                bond_df = pd.DataFrame(columns=['ticker', 'sec_name', 'weight'])
                bond_df.loc[0] = ['b00001', '债券投资', bond_ratio]
            # 基金
            tmp = data[data['科目代码'] == '1105']
            if tmp.empty:
                fund_df = pd.DataFrame()
            else:
                fund_ratio = tmp['市值'].astype(float).values[0] / net_asset
                fund_df = pd.DataFrame(columns=['ticker', 'sec_name', 'weight'])
                fund_df.loc[0] = ['f00001', '基金投资', fund_ratio]

            df = pd.concat([equity_a, equity_hk, bond_df, fund_df], axis=0)
            # 其他类
            cash_df = pd.DataFrame(columns=['ticker', 'sec_name', 'weight'])
            cash_df.loc[0] = ['c00001', '现金类投资', leverage - df['weight'].sum()]
            df = pd.concat([df, cash_df], axis=0)
            df['trade_date'] = date
            if(len(df[df['ticker'].str[0].isin(['0', '3', '6'])])>0):
                portfolio_weight_list.append(df)

        portfolio_weight_df = pd.concat(portfolio_weight_list)
        portfolio_weight_df['fund_name'] = fund_name

        return  portfolio_weight_df

    def _load_portfolio_weight(self):
        filenames = os.listdir(self.data_path)
        filenames = [x for x in filenames if x.split('.')[-1] in ['xls', 'xlsx']]

        portfolio_weight_list = []
        for file_name in filenames:
            if self.fund_name == '亘曦2号':
                date = file_name.split('.')[0].split('_')[-1][:-3].replace('-', '')
            elif self.fund_name in ['富乐一号', '仁布积极进取1号']:
                date = file_name.split('.')[0].split('_')[-2]
            else:
                date = file_name.split('.')[0].split('_')[-1]
            # shift_date
            date = self._shift_date(date)
            data = pd.read_excel(
                os.path.join(self.data_path, file_name), sheet_name=0, header=3).dropna(subset=['科目代码'])
            net_asset = data[data['科目代码'] == '基金资产净值:']['市值'].values[0]
            total_asset = data[data['科目代码'] == '资产类合计:']['市值'].values[0]
            leverage = total_asset / net_asset
            # A股
            sh = data[data['科目代码'].str.startswith('11020101')]
            sz = data[data['科目代码'].str.startswith('11023101')]
            cyb = data[data['科目代码'].str.startswith('11024101')]
            kcb = data[data['科目代码'].str.startswith('1102C101')]
            equity_a = pd.concat([sh, sz, cyb, kcb], axis=0)
            # sh1 = data[data['科目代码'].str.startswith('11021101')]
            # sz1 = data[data['科目代码'].str.startswith('11021201')]
            # cyb1 = data[data['科目代码'].str.startswith('11021501')]
            # kcb1 = data[data['科目代码'].str.startswith('1102D201')]
            # xsg = data[data['科目代码'].str.startswith('11028401')]
            # equity_cr = pd.concat([sh1, sz1, cyb1, kcb1, xsg], axis=0)
            # equity_a = pd.concat([equity_a, equity_cr], axis=0)
            equity_a['len'] = equity_a['科目代码'].apply(lambda x: len(x))
            equity_a = equity_a[equity_a['len'] > 8]
            equity_a['ticker'] = equity_a['科目代码'].apply(lambda x: x[-6:])
            equity_a['weight'] = equity_a['市值'] / net_asset
            equity_a = equity_a.rename(columns={"科目名称": "sec_name"})[['ticker', 'sec_name', 'weight']]
            # 港股
            hk1 = data[data['科目代码'].str.startswith('11028101')]
            hk2 = data[(data['科目代码'].str.startswith('11028201')) | (data['科目代码'].str.startswith('11028301'))]
            equity_hk = pd.concat([hk1, hk2], axis=0)
            equity_hk['len'] = equity_hk['科目代码'].apply(lambda x: len(x))
            equity_hk = equity_hk[equity_hk['len'] > 8]
            equity_hk['ticker'] = equity_hk['科目代码'].apply(lambda x: x[-6:])
            equity_hk['科目名称'] = equity_hk['科目名称'].apply(lambda x: x.strip())  # add
            equity_hk['weight'] = equity_hk['市值'] / net_asset
            equity_hk = equity_hk.rename(columns={"科目名称": "sec_name"})[['ticker', 'sec_name', 'weight']]
            equity_hk = equity_hk.groupby(['sec_name', 'ticker'])['weight'].sum().reset_index()
            # 债券
            tmp = data[data['科目代码'] == '1103']
            if tmp.empty:
                bond_df = pd.DataFrame()
            else:
                bond_ratio = tmp['市值'].values[0] / net_asset
                bond_df = pd.DataFrame(columns=['ticker', 'sec_name', 'weight'])
                bond_df.loc[0] = ['b00001', '债券投资', bond_ratio]
            # 基金
            tmp = data[data['科目代码'] == '1105']
            if tmp.empty:
                fund_df = pd.DataFrame()
            else:
                fund_ratio = tmp['市值'].values[0] / net_asset
                fund_df = pd.DataFrame(columns=['ticker', 'sec_name', 'weight'])
                fund_df.loc[0] = ['f00001', '基金投资', fund_ratio]

            df = pd.concat([equity_a, equity_hk, bond_df, fund_df], axis=0)
            # 其他类
            cash_df = pd.DataFrame(columns=['ticker', 'sec_name', 'weight'])
            cash_df.loc[0] = ['c00001', '现金类投资', leverage - df['weight'].sum()]
            df = pd.concat([df, cash_df], axis=0)
            df['trade_date'] = date
            portfolio_weight_list.append(df)

        portfolio_weight_df = pd.concat(portfolio_weight_list)
        portfolio_weight_df['fund_name'] = self.fund_name

        return portfolio_weight_df

    def Pre_test(self,fromdb=False):

        if (fromdb):
            data = self.valuation_data2DB(self.fund_code, self.date_list, self.fund_name)
        else:
            data = self._load_portfolio_weight()

        start_date=data['trade_date'].unique().tolist()[0]
        end_date=data['trade_date'].unique().tolist()[-1]

        HoldingAnalysor(self.fund_name, start_date=start_date, end_date=end_date,inputdf=data).get_construct_result()

    def writeToDB(self,fromdb=False):
        if self.is_increment == 1:
            if(fromdb):
                data=self.valuation_data2DB(self.fund_code,self.date_list,self.fund_name)
            else:
                data = self._load_portfolio_weight()
            trading_day_list = data['trade_date'].unique().tolist()
            sql_script = "delete from {} where trade_date in ({}) and fund_name = '{}'".format(
                self.table_name, ','.join(trading_day_list), self.fund_name)
            # delete first
            delete_duplicate_records(sql_script)
            # add new records

            WriteToDB().write_to_db(data, self.table_name)
        else:
            sql_script = """
                create table {}(
                id int auto_increment primary key,
                trade_date date not null,
                ticker varchar(10),
                sec_name varchar(20),
                weight decimal(5, 4),
                fund_name varchar(40))
            """.format(self.table_name)
            create_table(self.table_name, sql_script)
            data = self._load_portfolio_weight()
            WriteToDB().write_to_db(data, self.table_name)


class HoldingAnalysor:
    def __init__(self, fund_name, start_date, end_date, threshold=1,inputdf=None):
        self.fund_name = fund_name
        self.start_date = start_date
        self.end_date = end_date
        self.threshold = threshold
        if(inputdf is None):
            self._load_data()
        else:self._load_data(inputdf)

    def _load_portfolio_weight(self):
        sql_script = "SELECT * FROM subjective_fund_holding where fund_name = '{}' and " \
                     "trade_date >= {} and trade_date <= {}".format(self.fund_name, self.start_date, self.end_date)
        engine = create_engine(engine_params)
        holding_df = pd.read_sql(sql_script, engine)
        holding_df['trade_date'] = holding_df['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))

        return holding_df[['trade_date', 'ticker', 'sec_name', 'weight']]

    @staticmethod
    def _load_shift_date(date):
        trade_dt = datetime.datetime.strptime(date, '%Y%m%d')
        pre_date = (trade_dt - datetime.timedelta(days=100)).strftime('%Y%m%d')

        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
            pre_date, date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
        df['isWeekEnd'] = df['isWeekEnd'].fillna(0).astype(int)
        df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)

        trading_day_list = df[df['isMonthEnd'] == 1]['calendarDate'].tolist()

        return trading_day_list[-1]

    @staticmethod
    def _load_benchmark_weight(benchmark_id, shift_date, date):
        sql_script = "SELECT * FROM hsjy_gg.SecuMain where SecuCategory = 4 and SecuCode = '{}'".format(benchmark_id)
        res = hbs.db_data_query('readonly', sql_script)
        index_info = pd.DataFrame(res['data'])
        inner_code = index_info.set_index('SECUCODE').loc[benchmark_id, 'INNERCODE']

        sql_script = "SELECT (select a.SecuCode from hsjy_gg.SecuMain a where a.InnerCode = b.InnerCode and " \
                     "rownum = 1) SecuCode, b.EndDate, b.Weight FROM hsjy_gg.LC_IndexComponentsWeight b WHERE " \
                     "b.IndexCode = '{}' and b.EndDate = to_date('{}', 'yyyymmdd')".format(inner_code, shift_date)
        data = pd.DataFrame(hbs.db_data_query('readonly', sql_script)['data'])
        weight_df = data.rename(
            columns={"SECUCODE": "ticker", "ENDDATE": "effDate", "WEIGHT": "weight"})
        weight_df['benchmark_id'] = benchmark_id
        weight_df['trade_date'] = date

        return weight_df[['trade_date', 'ticker', 'benchmark_id']]

    @staticmethod
    def _load_security_sector(portfolio_weight):
        equity_portfolio_weight = portfolio_weight[portfolio_weight['ticker'].str[0].isin(['0', '3', '6'])]
        trading_day_list = sorted(portfolio_weight['trade_date'].unique())
        cols_list = ['ticker'] + [x.lower() for x in industry_name['sw'].values()]
        security_sector_list = []
        for date in trading_day_list:
            ticker_list = equity_portfolio_weight[equity_portfolio_weight['trade_date'] == date]['ticker'].tolist()
            sql_script = "SELECT {} FROM st_ashare.r_st_barra_style_factor where TRADE_DATE = '{}' and " \
                         "ticker in ({})".format(','.join(cols_list), date,
                                                 ','.join("'{0}'".format(x) for x in ticker_list))
            res = hbs.db_data_query('alluser', sql_script, page_size=5000)
            data = pd.DataFrame(res['data']).set_index('ticker')
            reverse_ind = dict([(value.lower(), key) for (key, value) in industry_name['sw'].items()])
            ind_exposure = data[reverse_ind.keys()].rename(columns=reverse_ind)
            ind_exposure = ind_exposure.reset_index().melt(
                id_vars=['ticker'], value_vars=list(reverse_ind.values()), var_name='industryName1', value_name='sign')
            ind_exposure = ind_exposure[ind_exposure['sign'] == '1']
            ind_exposure['trade_date'] = date
            ind_exposure = ind_exposure.set_index('ticker').reindex(ticker_list).dropna().reset_index()
            security_sector_list.append(ind_exposure)

        security_sector_df = pd.concat(security_sector_list)[['trade_date', 'ticker', 'industryName1']]

        return security_sector_df

    @staticmethod
    def _load_security_value(portfolio_weight):
        equity_portfolio_weight = portfolio_weight[portfolio_weight['ticker'].str[0].isin(['0', '3', '6'])]
        trading_day_list = sorted(portfolio_weight['trade_date'].unique())
        value_data_list = []
        for date in trading_day_list:
            ticker_list = equity_portfolio_weight[equity_portfolio_weight['trade_date'] == date]['ticker'].tolist()
            # 主板
            sql_script = "SELECT PE, PB, DividendRatio, TotalMV, SecuCode FROM " \
                         "(SELECT b.PE, b.PB, b.DividendRatio, b.TotalMV, a.SecuCode, " \
                         "row_number() over(partition by a.InnerCode order by a.InnerCode) rn FROM " \
                         "hsjy_gg.LC_DIndicesForValuation b join hsjy_gg.SecuMain a on a.InnerCode = b.InnerCode and " \
                         "a.SecuMarket in (83, 90) and a.SecuCategory = 1 WHERE " \
                         "b.TradingDay = to_date('{}', 'yyyymmdd') and a.SecuCode in ({})) " \
                         "WHERE rn = 1".format(date, ','.join("'{0}'".format(x) for x in ticker_list))
            res = hbs.db_data_query('readonly', sql_script, page_size=5000)
            data_main = pd.DataFrame(res['data']).rename(columns={"PE": "PETTM"})
            # 科创板
            sql_script = "SELECT PETTM, PB, DividendRatio, TotalMV, SecuCode FROM " \
                         "(SELECT b.PETTM, b.PB, b.DividendRatio, b.TotalMV, a.SecuCode, " \
                         "row_number() over(partition by a.InnerCode order by a.InnerCode) rn FROM " \
                         "hsjy_gg.LC_STIBDIndiForValue b join hsjy_gg.SecuMain a on a.InnerCode = b.InnerCode and " \
                         "a.SecuMarket in (83, 90) and a.SecuCategory = 1 WHERE " \
                         "b.TradingDay = to_date('{}', 'yyyymmdd') and a.SecuCode in ({})) " \
                         "WHERE rn = 1".format(date, ','.join("'{0}'".format(x) for x in ticker_list))
            res = hbs.db_data_query('readonly', sql_script, page_size=5000)
            data_stib = pd.DataFrame(res['data'])

            data = pd.concat([data_main, data_stib]).rename(columns={"SECUCODE": "ticker", "TOTALMV": "MarketValue"})
            data['MarketValue'] /= 1e+8
            del data['ROW_ID']
            data = data.dropna(subset=['ticker'])
            data['trade_date'] = date
            value_data_list.append(data)

        security_value_df = pd.concat(value_data_list)

        return security_value_df

    def _load_data(self,inputdf=None):
        if(inputdf is None):
            portfolio_weight_df = self._load_portfolio_weight()
        else:
            portfolio_weight_df=inputdf
        date_list = sorted(portfolio_weight_df['trade_date'].unique())
        benchmark_weight = []
        for date in date_list:
            shift_date = self._load_shift_date(date)
            weight_300 = self._load_benchmark_weight('000300', shift_date, date)
            weight_500 = self._load_benchmark_weight('000905', shift_date, date)
            weight_1000 = self._load_benchmark_weight('000852', shift_date, date)
            benchmark_weight.append(pd.concat([weight_300, weight_500, weight_1000]))

        benchmark_weight = pd.concat(benchmark_weight)

        security_sector_df = self._load_security_sector(portfolio_weight_df)

        security_value_df = self._load_security_value(portfolio_weight_df)

        self.data_param = {"portfolio_weight": portfolio_weight_df,
                           "benchmark_weight": benchmark_weight,
                           "security_sector_df": security_sector_df,
                           "security_value_df": security_value_df}

    @staticmethod
    def _calculate_asset_allo_series(portfolio_weight):
        date_list = sorted(portfolio_weight['trade_date'].unique())
        equity_a_series = portfolio_weight[portfolio_weight['ticker'].str[0].isin(['0', '3', '6'])].groupby(
            'trade_date')['weight'].sum().reindex(date_list).fillna(0.).to_frame('A股')
        equity_hk_series = portfolio_weight[portfolio_weight['ticker'].str.startswith('H')].groupby(
            'trade_date')['weight'].sum().reindex(date_list).fillna(0.).to_frame('港股')
        bond_series = portfolio_weight[portfolio_weight['ticker'].str.startswith('b')].groupby(
            'trade_date')['weight'].sum().reindex(date_list).fillna(0.).to_frame('债券')
        fund_series = portfolio_weight[portfolio_weight['ticker'].str.startswith('f')].groupby(
            'trade_date')['weight'].sum().reindex(date_list).fillna(0.).to_frame('基金')
        cash_series = portfolio_weight[portfolio_weight['ticker'].str.startswith('c')].groupby(
            'trade_date')['weight'].sum().reindex(date_list).fillna(0.).to_frame('现金类')
        asset_allo_series = pd.concat(
            [equity_a_series, equity_hk_series, bond_series, fund_series, cash_series], axis=1)
        # asset_allo_series['现金类'] = 1 - asset_allo_series.sum(axis=1)

        return asset_allo_series

    @staticmethod
    def _calculate_ind_allo_series(portfolio_weight, security_sector_df):
        weight_df = pd.merge(portfolio_weight, security_sector_df, on=['trade_date', 'ticker'])
        grouped_df = weight_df.groupby(['trade_date', 'industryName1'])['weight'].sum().reset_index()
        pivot_df = pd.pivot_table(
            grouped_df, index='trade_date', columns='industryName1', values='weight').sort_index().fillna(0.)

        sector_df = pd.DataFrame(index=pivot_df.index, columns=industry_cluster_dict.keys())
        for key, value in industry_cluster_dict.items():
            value_include = [x for x in value if x in pivot_df.columns]
            sector_df[key] = pivot_df[value_include].sum(axis=1)

        return pivot_df, sector_df

    @staticmethod
    def _calculate_mkt_dis(portfolio_weight, security_value_df):
        df = pd.merge(
            portfolio_weight, security_value_df[['trade_date', 'ticker', 'MarketValue']],
            on=['trade_date', 'ticker']).dropna()
        df.loc[df['MarketValue'] < 100, 'sign'] = 'S'
        df.loc[(df['MarketValue'] >= 100) & (df['MarketValue'] < 300), 'sign'] = 'M'
        df.loc[(df['MarketValue'] >= 300) & (df['MarketValue'] < 1000), 'sign'] = 'L'
        df.loc[df['MarketValue'] >= 1000, 'sign'] = 'XL'
        grouped_df = df.groupby(['trade_date', 'sign'])['weight'].sum().reset_index()
        pivot_df = pd.pivot_table(
            grouped_df, index='trade_date', columns='sign', values='weight').sort_index().fillna(0.)
        pivot_df = pivot_df[['XL', 'L', 'M', 'S']].rename(
            columns={"XL": "1000亿以上", "L": "300-1000亿", "M": "100-300亿", "S": "100亿以下"})

        return pivot_df

    @staticmethod
    def plotly_area(df, title_text, range_upper=100, figsize=(1200, 600)):
        fig_width, fig_height = figsize
        cols = df.index.tolist()

        data = []
        for col in cols:
            tmp = go.Scatter(
                x=df.columns.tolist(),
                y=df.loc[col].values,
                name=col,
                mode='lines',
                line=dict(width=0.5),
                fill='tonexty',
                stackgroup='one')
            data.append(tmp)

        layout = go.Layout(
            title=title_text,
            autosize=False,
            width=fig_width,
            height=fig_height,
            showlegend=True,
            xaxis=dict(type='category'),
            yaxis=dict(
                type='linear',
                range=[1, range_upper],
                dtick=20,
                ticksuffix='%'))

        return data, layout

    @staticmethod
    def plotly_line(df, title_text, figsize=(1200, 600)):
        fig_width, fig_height = figsize
        data = []
        for col in df.columns:
            trace = go.Scatter(
                x=df.index.tolist(),
                y=df[col],
                name=col,
                mode="lines+markers"
            )
            data.append(trace)

        layout = go.Layout(
            title=dict(text=title_text),
            autosize=False, width=fig_width, height=fig_height,
            yaxis=dict(tickfont=dict(size=12), tickformat=',.0%', showgrid=True),
            xaxis=dict(showgrid=True),
            template='plotly_white'
        )

        return data, layout

    @staticmethod
    def plotly_double_y_line(df, title_text, figsize=(1200, 600)):
        fig_width, fig_height = figsize

        trace0 = go.Scatter(
            x=df.index.tolist(), y=df[df.columns[0]], mode="lines+markers", name=df.columns[0] + '(左轴)')
        trace1 = go.Scatter(
            x=df.index.tolist(), y=df[df.columns[1]], mode="lines+markers", name=df.columns[1] + '(右轴)', yaxis='y2')

        data = [trace0, trace1]

        layout = go.Layout(
            title=dict(text=title_text),
            autosize=False, width=fig_width, height=fig_height,
            yaxis=dict(tickfont=dict(size=12), showgrid=False),
            yaxis2=dict(overlaying='y', side='right'),
            xaxis=dict(showgrid=True),
            template='plotly_white'
        )

        return data, layout

    @staticmethod
    def draw_timeline_bar(df, title_text, min_value=0, min_height=600):
        num = int(df.gt(min_value).sum(axis=1).max())
        tl = Timeline(init_opts=opts.InitOpts(width='1200px', height='{}px'.format(max(25 * num, min_height))))

        for i in df.index.tolist():
            tmp = df.loc[i].dropna()
            tmp = tmp[tmp >= min_value].sort_values()
            bar = (
                Bar()
                .add_xaxis(tmp.index.tolist())
                .add_yaxis(
                    "持仓权重",
                    (tmp * 100).round(2).values.tolist(),
                    itemstyle_opts=opts.ItemStyleOpts(color="#37a2da"),
                    label_opts=opts.LabelOpts(is_show=False))
                .reversal_axis()
                .set_global_opts(
                    title_opts=opts.TitleOpts("{} (时间点: {})".format(title_text, i)),
                    xaxis_opts=opts.AxisOpts(
                        axislabel_opts=opts.LabelOpts(formatter="{value} %"),
                        splitline_opts=opts.SplitLineOpts(is_show=True, linestyle_opts=opts.LineStyleOpts(opacity=0.3)))
                )
            )
            tl.add(bar, "{}年{}月".format(i[:4], i[4:6]))

        return tl

    @staticmethod
    def plotly_table(portfolio_weight_df, threshold=1.0):
        df = portfolio_weight_df[portfolio_weight_df['ticker'].str[0].isin(['0', '3', '6', 'H'])]
        df['weight'] *= 100.
        df['content'] = df['sec_name'] + '（' + df['weight'].round(1).map(str) + '%）'
        df = df[df['weight'] >= threshold]
        max_len = int(df['trade_date'].value_counts().max())
        table_data = pd.DataFrame(index=np.arange(max_len), columns=sorted(df['trade_date'].unique()))
        for col in table_data.columns:
            tmp = df[df['trade_date'] == col].sort_values(by='weight', ascending=False)
            table_data.loc[:len(tmp) - 1, col] = tmp['content'].tolist()

        table_data.dropna(how='any', axis=0, inplace=True)

        fig = ff.create_table(table_data)

        return fig, table_data.shape[1]

    @staticmethod
    def plotly_change_table(portfolio_weight_df, threshold=1.0):
        df = portfolio_weight_df[portfolio_weight_df['ticker'].str[0].isin(['0', '3', '6', 'H'])]
        df['weight'] = (100 * df['weight']).round(1)
        pivot_df = pd.pivot_table(df, index=['ticker', 'sec_name'], columns='trade_date', values='weight').sort_index()
        pivot_df['mean'] = pivot_df.mean(axis=1)
        pivot_df = pivot_df[pivot_df.mean(axis=1) > threshold].sort_values(by='mean', ascending=False)
        del pivot_df['mean']
        pivot_df.fillna('-', inplace=True)
        res_df = pivot_df.reset_index().rename(columns={"ticker": "股票代码", "sec_name": "股票简称"})

        fig = ff.create_table(res_df)

        return fig, res_df.shape[1]

    def get_construct_result(self, is_tl_show=False):
        portfolio_weight = self.data_param['portfolio_weight']
        benchmark_weight = self.data_param['benchmark_weight']
        security_sector_df = self.data_param['security_sector_df']
        security_value_df = self.data_param['security_value_df']
        # 资产配置时序
        asset_allo_series = self._calculate_asset_allo_series(portfolio_weight)
        # 行业配置时序
        industry_allo_df, sector_allo_df = self._calculate_ind_allo_series(portfolio_weight, security_sector_df)
        industry_cr = \
            pd.concat([industry_allo_df.apply(lambda x: x.nlargest(1).sum(), axis=1).to_frame('第一大行业'),
                       industry_allo_df.apply(lambda x: x.nlargest(3).sum(), axis=1).to_frame('前三大行业'),
                       industry_allo_df.apply(lambda x: x.nlargest(5).sum(), axis=1).to_frame('前五大行业')], axis=1)
        # 重仓持股
        equity_weight = portfolio_weight[~portfolio_weight['ticker'].str[0].isin(['b', 'f', 'c'])]
        equity_weight = pd.pivot_table(
            equity_weight, index='trade_date', columns='sec_name', values='weight').sort_index()
        tmp = equity_weight.fillna(0.)
        equity_cr = pd.concat([tmp.apply(lambda x: x.nlargest(3).sum(), axis=1).to_frame('cr3'),
                               tmp.apply(lambda x: x.nlargest(5).sum(), axis=1).to_frame('cr5'),
                               tmp.apply(lambda x: x.nlargest(10).sum(), axis=1).to_frame('cr10')], axis=1)
        # 平均PE/PB
        value_df = pd.merge(security_value_df, portfolio_weight, on=['trade_date', 'ticker']).dropna(
            subset=['PB', 'PETTM'])
        # 做一下剔除
        value_df = value_df[(value_df['PETTM'] <= 1000) & (value_df['PETTM'] >= -1000)]
        average_pe = value_df.groupby('trade_date').apply(
            lambda x: (x['weight'] * x['PETTM']).sum() / x['weight'].sum()).to_frame('平均市盈率')
        average_pb = value_df.groupby('trade_date').apply(
            lambda x: (x['weight'] * x['PB']).sum() / x['weight'].sum()).to_frame('平均市净率')
        average_pe_pb = pd.concat([average_pe, average_pb], axis=1)
        # 持仓宽基分布
        df = portfolio_weight[portfolio_weight['ticker'].str[0].isin(['0', '3', '6'])]
        df = pd.merge(df, benchmark_weight, on=['trade_date', 'ticker'], how='left').fillna('other')
        bm_dis = df.groupby(['trade_date', 'benchmark_id'])['weight'].sum().reset_index()
        bm_dis = pd.pivot_table(
            bm_dis, index='trade_date', columns='benchmark_id', values='weight').sort_index().fillna(0.)
        map_dict = {"000300": "沪深300", "000905": "中证500", "000852": "中证1000", "other": "1800以外"}
        bm_dis.columns = [map_dict[x] for x in bm_dis.columns]
        # bm_dis = bm_dis[['沪深300', '中证500', '中证1000', '1800以外']]
        # 持仓市值分布
        mkt_dis = self._calculate_mkt_dis(portfolio_weight, security_value_df)

        upper_range = np.ceil(asset_allo_series.sum(axis=1).max() / 0.2) * 20
        data, layout = self.plotly_area(100 * asset_allo_series.T, '资产配置走势', upper_range)
        plot_render({"data": data, "layout": layout}, width=1200, height=600)

        upper_range = np.ceil(industry_allo_df.sum(axis=1).max() / 0.2) * 20
        data, layout = self.plotly_area(100 * industry_allo_df.T, '行业配置走势', upper_range)
        plot_render({"data": data, "layout": layout}, width=1200, height=600)
        # fig = go.Figure(data=data, layout=layout)
        # plot_ly(fig, filename="D:\\主观股多估值表基地\\图表所在\\B-行业配置走势.html", auto_open=False)

        upper_range = np.ceil(sector_allo_df.sum(axis=1).max() / 0.2) * 20
        data, layout = self.plotly_area(100 * sector_allo_df.T, '板块配置走势', upper_range)
        plot_render({"data": data, "layout": layout}, width=1200, height=600)

        data, layout = self.plotly_line(industry_cr, '行业集中度走势')
        plot_render({"data": data, "layout": layout}, width=1200, height=600)

        if is_tl_show:
            tl_bar = self.draw_timeline_bar(industry_allo_df, "截面行业权重", min_value=0.02, min_height=400)
            html_content = tl_bar.render_embed()
            print("%html {}".format(html_content))
            # tl_bar.render('D:\\主观股多估值表基地\\图表所在\\D-持仓行业明细.html')

        fig, n = self.plotly_table(portfolio_weight)
        plot_render({"data": fig.data, "layout": fig.layout}, width=120*n, height=600)

        fig, n = self.plotly_change_table(portfolio_weight)
        plot_render({"data": fig.data, "layout": fig.layout}, width=80*n, height=600)

        data, layout = self.plotly_line(equity_cr, "持股集中度走势")
        plot_render({"data": data, "layout": layout}, width=1200, height=600)

        if is_tl_show:
            tl_bar = self.draw_timeline_bar(equity_weight, "截面持股权重", min_value=0.02)
            html_content = tl_bar.render_embed()
            print("%html {}".format(html_content))

        data, layout = self.plotly_double_y_line(average_pe_pb.round(1), "持股估值水平走势")
        plot_render({"data": data, "layout": layout}, width=1200, height=600)

        upper_range = np.ceil(bm_dis.sum(axis=1).max() / 0.2) * 20
        data, layout = self.plotly_area(100 * bm_dis.T, '宽基成分配置走势', upper_range)
        plot_render({"data": data, "layout": layout}, width=1200, height=600)

        upper_range = np.ceil(mkt_dis.sum(axis=1).max() / 0.2) * 20
        data, layout = self.plotly_area(100 * mkt_dis.T, '持股市值分布走势', upper_range)
        plot_render({"data": data, "layout": layout}, width=1200, height=600)


if __name__ == '__main__':
    name = '新方程泰暘臻选1期'
    # name = '新方程望正精英鹏辉'
    # name = '新方程域秀智享5号'
    # name = '亘曦2号'
    # name = '富乐一号'
    #name = '仁布积极进取1号'
    # name='仁桥金选泽源5期'
    # name='新方程泓澄精选'
    # name='新方程清和泉'
    # name='果实长期成长1号'
    # name='新方程石锋厚积3号'
    # name='新方程石锋厚积5号'
    # name='巨杉净值线3号'
    name='新方程巨杉'
    name='同犇1期'
    name= '同犇消费5号'
    name='圣鑫'
    # name='龙航'
    # name='山楂树'
    name='睿洪二号'
    name='丰岭稳健成长1期'
    name='望正精英-鹏辉1号'

    # name_list=['圣鑫']
    # code_list=['SGE022']
    # date_list=pd.read_excel(r"E:\私募主观\私募主观可用持仓列表.xls")
    # for i in range(len(code_list)):
    #     code=code_list[i]
    #     name=name_list[i]
    #     date_list_temp=date_list[date_list['code']==code].astype(str)
    #     date_list_temp = date_list_temp[date_list_temp['date'] >= '20141031']
    #     date_list_temp['yeatmonth']=[x[0:6] for x in date_list_temp['date']]
    #     date_list_temp=date_list_temp.drop_duplicates('yeatmonth', keep='last')['date'].to_list()
    #     HoldingExtractor(table_name="subjective_fund_holding", fund_name=name,
    #                      is_increment=1, fund_code=code,date_list=date_list_temp)\
    #         .Pre_test(fromdb=True)
    #     print("{} test passed ".format(name))

    name_list=['新方程泓澄精选','新方程清和泉','果实长期成长1号','新方程石锋厚积3号','新方程石锋厚积5号','巨杉净值线3号','龙航','山楂树']
    code_list=['S63505','S61607','S64497','SLE846','SLK336','S20717','SLT681','S20950']
    date_list=pd.read_excel(r"E:\私募主观\私募主观可用持仓列表.xls")
    for i in range(len(code_list)):
        code=code_list[i]
        name=name_list[i]
        date_list_temp=date_list[date_list['code']==code].astype(str)
        date_list_temp = date_list_temp[date_list_temp['date'] >= '20141031']
        date_list_temp['yeatmonth']=[x[0:6] for x in date_list_temp['date']]
        date_list_temp=date_list_temp.drop_duplicates('yeatmonth', keep='last')['date'].to_list()
        HoldingExtractor(table_name="subjective_fund_holding", fund_name=name, is_increment=1,fund_code=code,
                         date_list=date_list_temp)\
            .writeToDB(fromdb=True)
    # HoldingAnalysor(name, start_date='20141231', end_date='20200731').get_construct_result()