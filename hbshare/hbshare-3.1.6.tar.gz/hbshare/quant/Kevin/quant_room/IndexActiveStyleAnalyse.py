"""
指数指增主动风格分析
"""
import hbshare as hbs
import pandas as pd
import os
from hbshare.quant.Kevin.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB
from sqlalchemy import create_engine
from hbshare.quant.Kevin.rm_associated.config import engine_params
from datetime import datetime
import pyecharts.options as opts
from pyecharts.globals import ThemeType
from pyecharts.charts import Line
# from pyecharts.charts import Grid, Tab
# from hbshare.rm_associated.util.plot_util import draw_active_exposure_series

style_name_list = [
    "size", "beta", "momentum", "earnyield", "resvol", "growth", "btop", "leverage", "liquidity", "sizenl"]
path = r'D:\kevin\risk_model_jy\RiskModel\data'


class IndexActiveStyleCalculator:
    def __init__(self, fund_id, benchmark_id, start_date, end_date):
        self.fund_id = fund_id
        self.benchmark_id = benchmark_id
        self.start_date = start_date
        self.end_date = end_date
        self._load_data()

    def _load_calendar(self):
        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
            self.start_date, self.end_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
        df['isWeekEnd'] = df['isWeekEnd'].fillna(0).astype(int)
        df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)

        self.calendar_df = df[['calendarDate', 'isOpen', 'isWeekEnd', 'isMonthEnd']]

        df = df[df['isMonthEnd'] == 1].copy()
        trading_day_list = [x for x in sorted(df['calendarDate'].unique()) if x[4:6] in ['06', '12']]

        return trading_day_list

    def _load_portfolio_weight(self):
        sql_script = "SELECT JJDM, JSRQ, ZQDM, ZJBL FROM funddb.GPZH WHERE JJDM = '{}' and GGRQ >= {} " \
                     "and GGRQ <= {}".format(self.fund_id, self.start_date, self.end_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        data = pd.DataFrame(res['data']).rename(
            columns={"JSRQ": "endDate", "ZQDM": "ticker", "ZJBL": "weight"})
        date_list = [x for x in sorted(data['endDate'].unique()) if x[4:6] not in ['03', '09']]
        trading_day_list = [
            self.calendar_df[(self.calendar_df['calendarDate'] <= x) & (self.calendar_df['isOpen'] == 1)]
            ['calendarDate'].unique()[-1] for x in date_list]
        map_dict = dict(zip(date_list, trading_day_list))
        data['endDate'] = data['endDate'].replace(map_dict)

        portfolio_weight_series_dict = {}
        for date in trading_day_list:
            portfolio_weight_series_dict[date] = data[data['endDate'] == date].set_index('ticker')['weight'] / 100.

        return portfolio_weight_series_dict

    def _load_benchmark_weight(self, portfolio_weight_series_dict):
        sql_script = "SELECT * FROM hsjy_gg.SecuMain where SecuCategory = 4 and SecuCode = '{}'".format(
            self.benchmark_id)
        res = hbs.db_data_query('readonly', sql_script)
        index_info = pd.DataFrame(res['data'])
        inner_code = index_info.set_index('SECUCODE').loc[self.benchmark_id, 'INNERCODE']
        trading_day_list = sorted(portfolio_weight_series_dict.keys())
        benchmark_weight_series_dict = dict()
        for date in trading_day_list:
            sql_script = "SELECT (select a.SecuCode from hsjy_gg.SecuMain a where a.InnerCode = b.InnerCode and " \
                         "rownum = 1) SecuCode, b.EndDate, b.Weight FROM hsjy_gg.LC_IndexComponentsWeight b WHERE " \
                         "b.IndexCode = '{}' and b.EndDate = to_date('{}', 'yyyymmdd')".format(inner_code, date)
            data = pd.DataFrame(hbs.db_data_query('readonly', sql_script)['data'])
            weight_df = data.rename(
                columns={"SECUCODE": "consTickerSymbol", "ENDDATE": "effDate", "WEIGHT": "weight"})
            benchmark_weight_series_dict[date] = weight_df.set_index(
                'consTickerSymbol')['weight'] / 100.

        return benchmark_weight_series_dict

    @staticmethod
    def _load_style_factor_exposure(portfolio_weight_series_dict):
        style_factor_exposure_dict = dict()
        for date in portfolio_weight_series_dict.keys():
            data_path = os.path.join(path, r'zzqz_sw\style_factor')
            exposure_df = pd.read_csv(
                os.path.join(data_path, '{0}.csv'.format(date)), dtype={"ticker": str}).set_index(
                'ticker')[style_name_list]
            style_factor_exposure_dict[date] = exposure_df

        return style_factor_exposure_dict

    def _load_data(self):
        trading_day_list = self._load_calendar()
        if len(trading_day_list) < 2:
            return
        portfolio_weight_series_dict = self._load_portfolio_weight()
        benchmark_weight_series_dict = self._load_benchmark_weight(portfolio_weight_series_dict)
        style_factor_exposure_series_dict = self._load_style_factor_exposure(portfolio_weight_series_dict)

        data_param = {
            "portfolio_weight_series_dict": portfolio_weight_series_dict,
            "benchmark_weight_series_dict": benchmark_weight_series_dict,
            "style_factor_exposure_series_dict": style_factor_exposure_series_dict
        }

        self.data_param = data_param

    def get_construct_result(self):
        portfolio_weight_series_dict = self.data_param.get('portfolio_weight_series_dict')
        benchmark_weight_series_dict = self.data_param.get('benchmark_weight_series_dict')
        style_factor_exposure_series_dict = self.data_param.get('style_factor_exposure_series_dict')

        exposure_list = []
        for date in portfolio_weight_series_dict.keys():
            portfolio_weight_series = portfolio_weight_series_dict[date]
            benchmark_weight_series = benchmark_weight_series_dict[date]
            style_factor_exposure_series = style_factor_exposure_series_dict[date]

            idx = portfolio_weight_series.index.union(benchmark_weight_series.index).intersection(
                style_factor_exposure_series.index)

            portfolio_weight_series = portfolio_weight_series.reindex(idx).fillna(0.)
            benchmark_weight_series = benchmark_weight_series.reindex(idx).fillna(0.)
            style_factor_exposure_series = style_factor_exposure_series.reindex(idx)

            portfolio_expo = style_factor_exposure_series.T.dot(portfolio_weight_series)
            benchmark_expo = style_factor_exposure_series.T.dot(benchmark_weight_series)
            style_expo = pd.concat([portfolio_expo.to_frame('port'), benchmark_expo.to_frame('bm')], axis=1)
            style_expo['active'] = style_expo['port'] - style_expo['bm']
            style_expo['style'] = style_expo.index
            style_expo['date'] = date
            style_expo.reset_index(drop=True, inplace=True)

            exposure_list.append(style_expo)

        exposure_df = pd.concat(exposure_list, axis=0)

        return exposure_df


class EquityIndexStyleCalculator:
    def __init__(self, start_date, end_date, benchmark_id, is_increment=1):
        self.start_date = start_date
        self.end_date = end_date
        self.benchmark_id = benchmark_id
        self.is_increment = is_increment
        self.table_name = 'stock_index_style_exposure'
        self._load_data()

    def _load_calendar(self):
        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
            self.start_date, self.end_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
        df['isWeekEnd'] = df['isWeekEnd'].fillna(0).astype(int)
        df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)

        self.calendar_df = df[['calendarDate', 'isOpen', 'isWeekEnd', 'isMonthEnd']]
        trading_day_list = self.calendar_df[self.calendar_df['isMonthEnd'] == 1]['calendarDate'].tolist()

        return trading_day_list

    def _load_benchmark_weight(self, trading_day_list):
        sql_script = "SELECT * FROM hsjy_gg.SecuMain where SecuCategory = 4 and SecuCode = '{}'".format(
            self.benchmark_id)
        res = hbs.db_data_query('readonly', sql_script)
        index_info = pd.DataFrame(res['data'])
        inner_code = index_info.set_index('SECUCODE').loc[self.benchmark_id, 'INNERCODE']
        benchmark_weight_series_dict = dict()
        for date in trading_day_list:
            sql_script = "SELECT (select a.SecuCode from hsjy_gg.SecuMain a where a.InnerCode = b.InnerCode and " \
                         "rownum = 1) SecuCode, b.EndDate, b.Weight FROM hsjy_gg.LC_IndexComponentsWeight b WHERE " \
                         "b.IndexCode = '{}' and b.EndDate = to_date('{}', 'yyyymmdd')".format(inner_code, date)
            data = pd.DataFrame(hbs.db_data_query('readonly', sql_script)['data'])
            weight_df = data.rename(
                columns={"SECUCODE": "consTickerSymbol", "ENDDATE": "effDate", "WEIGHT": "weight"})
            benchmark_weight_series_dict[date] = weight_df.set_index(
                'consTickerSymbol')['weight'] / 100.

        return benchmark_weight_series_dict

    @staticmethod
    def _load_style_exposure(trading_day_list):
        style_factor_exposure_series_dict = dict()
        for date in trading_day_list:
            data_path = os.path.join(path, r'zzqz_sw\style_factor')
            exposure_df = pd.read_csv(
                os.path.join(data_path, '{0}.csv'.format(date)), dtype={"ticker": str}).set_index(
                'ticker')[style_name_list]
            # sql_script = "SELECT * FROM st_ashare.r_st_barra_style_factor where TRADE_DATE = '{}'".format(date)
            # res = hbs.db_data_query('alluser', sql_script, page_size=5000)
            # exposure_df = pd.DataFrame(res['data']).set_index('ticker')[style_name_list]
            style_factor_exposure_series_dict[date] = exposure_df

        return style_factor_exposure_series_dict

    def _load_data(self):
        trading_day_list = self._load_calendar()
        benchmark_weight_series_dict = self._load_benchmark_weight(trading_day_list)
        style_factor_exposure_series_dict = self._load_style_exposure(trading_day_list)

        self.data_param = {"benchmark_weight_series_dict": benchmark_weight_series_dict,
                           "style_factor_exposure_series_dict": style_factor_exposure_series_dict}

    def get_benchmark_style_exposure(self):
        benchmark_weight_series_dict = self.data_param.get('benchmark_weight_series_dict')
        style_factor_exposure_series_dict = self.data_param.get('style_factor_exposure_series_dict')

        exposure_list = []
        for date in benchmark_weight_series_dict.keys():
            benchmark_weight_series = benchmark_weight_series_dict[date]
            style_factor_exposure_series = style_factor_exposure_series_dict[date]

            idx = benchmark_weight_series.index.intersection(style_factor_exposure_series.index)

            benchmark_weight_series = benchmark_weight_series.reindex(idx)
            style_factor_exposure_series = style_factor_exposure_series.reindex(idx)
            exposure_series = style_factor_exposure_series.T.dot(benchmark_weight_series)
            exposure_list.append(exposure_series.to_frame(date))

        exposure_df = pd.concat(exposure_list, axis=1).T
        exposure_df['trade_date'] = exposure_df.index
        exposure_df = pd.melt(exposure_df, id_vars=['trade_date'], var_name='factor_name', value_name='exposure')
        exposure_df['benchmark_id'] = self.benchmark_id

        return exposure_df

    def get_construct_result(self):
        if self.is_increment == 1:
            data = self.get_benchmark_style_exposure()
            sql_script = "delete from {} where trade_date in ({}) and benchmark_id = {}".format(
                self.table_name, ','.join(data['trade_date'].tolist()), self.benchmark_id)
            # delete first
            delete_duplicate_records(sql_script)
            # add new records
            WriteToDB().write_to_db(data, self.table_name)
        else:
            sql_script = """
                create table stock_index_style_exposure(
                id int auto_increment primary key,
                trade_date date not null,
                factor_name varchar(20),
                exposure decimal(4, 3),
                benchmark_id varchar(10))
            """
            create_table(self.table_name, sql_script)
            data = self.get_benchmark_style_exposure()
            WriteToDB().write_to_db(data, self.table_name)


class EquityIndexStyle:
    def __init__(self, start_date, end_date, benchmark_id):
        self.start_date = start_date
        self.end_date = end_date
        self.benchmark_id = benchmark_id
        self._load_data()

    def _load_data(self):
        sql_script = "SELECT * FROM stock_index_style_exposure where TRADE_DATE >= {} and TRADE_DATE <= {} " \
                     "and BENCHMARK_ID = '{}'".format(self.start_date, self.end_date, self.benchmark_id)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        data = pd.pivot_table(
            data, index='trade_date', columns='factor_name', values='exposure').sort_index()[style_name_list]

        self.data = data

    def generate_trendency_line(self, title):
        df = self.data.copy()
        line = Line(
            init_opts=opts.InitOpts(
                page_title=title,
                width='1200px',
                height='600px',
                theme=ThemeType.MACARONS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            legend_opts=opts.LegendOpts(legend_icon='pin', pos_top='5%'),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                min_interval=0.1,
                name='Index Exposure Series(%)',
                name_location='middle',
                name_gap=45,
                name_textstyle_opts=opts.TextStyleOpts(font_size=16),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")],
        ).add_xaxis(
            xaxis_data=df.index.tolist()
        )

        for style_factor in style_name_list:
            line.add_yaxis(
                series_name=style_factor,
                y_axis=df[style_factor].round(3).tolist(),
                label_opts=opts.LabelOpts(is_show=False),
                is_smooth=True
            )

        return line


if __name__ == '__main__':
    # # 300指增：富国(100038)
    # exposure = IndexActiveStyleCalculator('100038', '000300', '20181220', '20210420').get_construct_result()
    # exposure_300 = exposure.groupby('style').mean().reindex(style_name_list)
    # exposure_300.columns = ['富国300指增风格暴露', '沪深300风格暴露', '主动风格暴露']
    # # 500指增：富国(161017)
    # exposure = IndexActiveStyleCalculator('161017', '000905', '20181220', '20210420').get_construct_result()
    # exposure_500 = exposure.groupby('style').mean().reindex(style_name_list)
    # exposure_500.columns = ['富国500指增风格暴露', '中证500风格暴露', '主动风格暴露']
    # # 300 VS 500
    # index_compare = IndexActiveStyleCalculator('510300', '000905', '20181220', '20210420').get_construct_result()
    # exposure_compare = index_compare.groupby('style').mean().reindex(style_name_list)
    # exposure_compare.columns = ['沪深300风格暴露', '中证500风格暴露', '300相对500主动风格暴露']
    #
    # tab = Tab()
    # grid1 = Grid(init_opts=opts.InitOpts(width="1200px", height="800px", theme=ThemeType.WESTEROS))
    # bar1 = draw_active_exposure_series(exposure_300, '300指增主动风格暴露')
    # grid1.add(bar1, grid_opts=opts.GridOpts(pos_bottom='30%'), is_control_axis_index=True)
    # tab.add(grid1, '300指增主动风格暴露')
    # grid2 = Grid(init_opts=opts.InitOpts(width="1200px", height="800px", theme=ThemeType.WESTEROS))
    # bar2 = draw_active_exposure_series(exposure_500, '500指增主动风格暴露')
    # grid2.add(bar2, grid_opts=opts.GridOpts(pos_bottom='30%'), is_control_axis_index=True)
    # tab.add(grid2, '500指增主动风格暴露')
    # grid3 = Grid(init_opts=opts.InitOpts(width="1200px", height="800px", theme=ThemeType.WESTEROS))
    # bar3 = draw_active_exposure_series(exposure_compare, '沪深300相对中证500主动风格暴露')
    # grid3.add(bar3, grid_opts=opts.GridOpts(pos_bottom='30%'), is_control_axis_index=True)
    # tab.add(grid3, '沪深300相对中证500主动风格暴露')
    #
    # tab.render('D:\\kevin\\宽基指数风格暴露.html')

    # EquityIndexStyleCalculator('20201220', '20210804', '000300', is_increment=1).get_construct_result()
    exposure = IndexActiveStyleCalculator('100038', '000300', '20191220', '20210420').get_construct_result()
    print(123)
    # pic = EquityIndexStyle('20111220', '20210804', '000852').generate_trendency_line(title='宽基指数风格暴露走势图')
    # pic.render('D:\\kevin\\123.html')