"""
基金风格箱的校验程序
"""
import pandas as pd
import hbshare as hbs


class MorningStarCheck:
    def __init__(self, trade_date, mode):
        self.trade_date = trade_date
        self.mode = mode
        self._get_report_date()

    def _get_report_date(self):
        pre_date = str(int(self.trade_date[:4]) - 2) + '0101'
        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
           pre_date, self.trade_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)
        df = df[df['isMonthEnd'] == 1]

        if self.mode == "main":  # quarter
            df['pre_end'] = df['calendarDate'].shift(1)
            quotation_date = df.set_index('calendarDate').loc[self.trade_date, 'pre_end']
        else:
            df['shift_2'] = df['calendarDate'].shift(2)
            df['shift_4'] = df['calendarDate'].shift(4)
            if self.trade_date[4:6] == "08":
                quotation_date = df.set_index('calendarDate').loc[self.trade_date, 'shift_2']
            else:
                quotation_date = df.set_index('calendarDate').loc[self.trade_date, 'shift_4']

        self.quotation_date = quotation_date

    def get_online_res_from_mysql(self):
        db_name = 'st_fund'
        user_name = 'funduser'

        # equity_score
        sql_script = "SELECT trade_date, ticker, type, cap_score, vcg_score, category FROM " \
                     "{}.r_st_gp_equity_score where trade_date = {} and " \
                     "type = '{}'".format(db_name, self.quotation_date, self.mode)
        res = hbs.db_data_query(user_name, sql_script, page_size=6000)
        equity_score = pd.DataFrame(res['data'])
        # equity_score = equity_score.drop_duplicates(subset=['ticker'])
        # fund_score
        sql_script = "SELECT trade_date, fund_id, type, cap_score, vcg_score, category FROM " \
                     "{}.r_st_gm_equity_score where trade_date = {} and " \
                     "type = '{}'".format(db_name, self.trade_date, self.mode)
        res = hbs.db_data_query(user_name, sql_script, page_size=6000)
        fund_score = pd.DataFrame(res['data'])
        # fund_score = fund_score.drop_duplicates(subset=['fund_id'])

        return equity_score, fund_score


if __name__ == '__main__':
    equity_score_online, fund_score_online = MorningStarCheck('20100430', 'all').get_online_res_from_mysql()
    print(equity_score_online)
    print(fund_score_online)