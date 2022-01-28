"""
线上和本地的Brinson归因结果校验
"""
import pandas as pd
import hbshare as hbs
from hbshare.fe.brinson_attr.equity_brinson_attribution import EquityBrinsonAttribution


class BrinsonAttrCheck:
    def __init__(self, fund_id, mode='single'):
        self.fund_id = fund_id
        self.mode = mode
        if self.mode == 'all':
            self._load_summary_info()
        self._load_data()

    def _load_summary_info(self):
        # fund_info
        sql_script = "select jjdm,clrq,zzrq, (select count(1) from st_fund.t_st_gm_rhb r where r.jjdm = a.jjdm ) " \
                     "hb_count from st_fund.t_st_gm_jjxx a where a.Jjfl = '{}' and m_opt_type<>'03' and " \
                     "clrq is not null order by clrq asc".format('1')
        res = hbs.db_data_query('funduser', sql_script, page_size=10000)
        equity_info = pd.DataFrame(res['data'])
        equity_info['category'] = 'equity'
        sql_script = "select jjdm,clrq,zzrq, (select count(1) from st_fund.t_st_gm_rhb r where r.jjdm = a.jjdm ) " \
                     "hb_count from st_fund.t_st_gm_jjxx a where a.Jjfl = '{}' and m_opt_type<>'03' and " \
                     "clrq is not null order by clrq asc".format('3')
        res = hbs.db_data_query('funduser', sql_script, page_size=10000)
        hybrid_info = pd.DataFrame(res['data'])
        hybrid_info['category'] = 'hybrid'

        fund_info = pd.concat([equity_info, hybrid_info]).rename(
            columns={"clrq": "start_date", "zzrq": "end_date", "jjdm": "fund_id"})

        fund_info['start_date'] = fund_info['start_date'].astype(str)
        fund_info['end_date'] = fund_info['end_date'].fillna('20210824').astype(str)
        print("--- All Equity and Hybrid Fund Num = {} ---".format(fund_info.shape[0]))

        # 剔除成立时间不足一年的
        fund_info = fund_info[fund_info['start_date'] < '20200701']
        print("--- After Operating Period Filter Num = {} ---".format(fund_info.shape[0]))

        self.fund_info = fund_info[['fund_id', 'category', 'start_date', 'end_date']]

    def _load_data(self):
        sql_script = "select jjdm,clrq,zzrq, (select count(1) from st_fund.t_st_gm_rhb r where r.jjdm = a.jjdm ) " \
                     "hb_count from st_fund.t_st_gm_jjxx a where a.Jjfl in ('1', '3') and m_opt_type<>'03' and " \
                     "clrq is not null and jjdm = '{}' order by clrq asc".format(self.fund_id)
        res = hbs.db_data_query('funduser', sql_script)
        df = pd.DataFrame(res['data']).set_index('jjdm')

        self.start_date = \
            str(df.loc[self.fund_id, 'clrq']) if str(df.loc[self.fund_id, 'clrq']) > '20100101' else '20091220'
        self.end_date = str(df.loc[self.fund_id, 'zzrq']) if df.loc[self.fund_id, 'zzrq'] is not None else '20210701'

        sql_script = "SELECT * FROM st_fund.r_st_hold_excess_attr_df where jjdm = '{}'".format(self.fund_id)
        res = hbs.db_data_query('funduser', sql_script)
        attr_df = pd.DataFrame(res['data']).rename(columns={"jjdm": "fund_id", "tjrq": "trade_date"})
        if not attr_df.empty:
            cols = ['trade_date', 'portfolio_return', 'benchmark_return', 'asset_allo', 'sector_allo',
                    'equity_selection', 'trading', 'portfolio_weight', 'benchmark_weight', 'fund_id']
            attr_df_ol = attr_df[cols].sort_values(by='trade_date')
        else:
            attr_df_ol = pd.DataFrame()

        sql_script = "SELECT * FROM st_fund.r_st_hold_sector_attr_df where jjdm = '{}'".format(self.fund_id)
        res = hbs.db_data_query('funduser', sql_script)
        sector_attr_df = pd.DataFrame(res['data']).rename(columns={"jjdm": "fund_id", "tjrq": "trade_date"})
        if not sector_attr_df.empty:
            cols = ['trade_date', 'industry', 'portfolio_weight', 'benchmark_weight', 'active_weight',
                    'portfolio_return', 'benchmark_return', 'active_return',
                    'sector_allo', 'equity_selection', 'management', 'fund_id']
            sector_attr_df_ol = sector_attr_df[cols].sort_values(by='trade_date')
        else:
            sector_attr_df_ol = pd.DataFrame()

        self.attr_result = {"realized_period_attr_df": attr_df_ol, "sector_attr_df": sector_attr_df_ol}

    def get_construct_result(self):
        # 本地结果
        attr_result = \
            EquityBrinsonAttribution(self.fund_id, '000906', self.start_date, self.end_date).get_attribution_result()

        return self.attr_result, attr_result


if __name__ == '__main__':
    res_ol, res_lc = BrinsonAttrCheck(fund_id='000031').get_construct_result()
    print(res_ol['realized_period_attr_df'])
    print("\n")
    print(res_lc['realized_period_attr_df'].round(6))
    # f_info = BrinsonAttrCheck(fund_id='110011', mode='all').fund_info
    # f_info = f_info[f_info['end_date'] > '20100101'].set_index('fund_id')
    #
    # from tqdm import tqdm
    #
    # for fund_id in tqdm(f_info.index.tolist()):
    #     start_date = f_info.loc[fund_id, 'start_date']
    #     start_date = start_date if start_date > '2010101' else '20091220'
    #     end_date = f_info.loc[fund_id, 'end_date']
    #     sql = "SELECT JJDM, JSRQ, ZQDM, ZJBL FROM funddb.GPZH WHERE JJDM = '{}' and GGRQ >= {} " \
    #           "and GGRQ <= {}".format(fund_id, start_date, end_date)
    #     res_outer = hbs.db_data_query('readonly', sql, page_size=10000)
    #     holding_df = pd.DataFrame(res_outer['data'])
    #     date_list = [x for x in holding_df['JSRQ'].unique() if x[4:6] in ["06", "12"]]
    #     f_info.loc[fund_id, 'holding_num'] = len(date_list)
    #
    # sql_script = "SELECT jjdm, count(*) as num FROM st_fund.r_st_hold_excess_attr_df group by jjdm"
    # res = hbs.db_data_query('funduser', sql_script, page_size=10000)
    # df = pd.DataFrame(res['data'])
