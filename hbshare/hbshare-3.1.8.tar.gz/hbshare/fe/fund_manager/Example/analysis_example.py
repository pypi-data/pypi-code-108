import sys
import os
now_path = os.path.abspath("..")
sys.path.append(now_path)
import time


from FundManager import ManagerNetWorth
from FundManager.database.database_operate import *
import pandas as pd
from pyecharts.charts import Line
from pyecharts.render import make_snapshot
import pyecharts.options as opts
from snapshot_selenium import snapshot as driver


if __name__ == "__main__":
	# all_fund_manager = get_manager_basic_info(['distinct ryxm, rydm'], None)

	# for fund_manager in all_fund_manager['人员代码']:
	a = time.time()
	fund_code = '30131310'

	manager = ManagerNetWorth()

	manager.run(fund_code, True)
	# 基金经理偏股型指数
	share_index = manager.fund_manager_share_index
	# 基金经理偏债型指数
	bond_index = manager.fund_manager_bond_index

	share_index.to_csv(f'{fund_code}_share_2014.csv', index=False)

	print('开始画图')

	# 作图
	if len(share_index) > 0:
		share_line = (
			Line()
			.add_xaxis(share_index['date'].to_list())
			.add_yaxis("偏股型基金指数", share_index['index'].to_list())
			.set_series_opts(
				areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
				label_opts=opts.LabelOpts(is_show=False),
			)
		)
		make_snapshot(driver, share_line.render(), f"image/{fund_code}_share_line.png")
	if len(bond_index) > 0:
		bond_line = (
			Line()
			.add_xaxis(bond_index['date'].to_list())
			.add_yaxis("偏债型基金指数", bond_index['index'].to_list())
			.set_series_opts(
				areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
				label_opts=opts.LabelOpts(is_show=False),
			)
		)
		make_snapshot(driver, bond_line.render(), f"image/{fund_code}_bond_line.png")
	b = time.time()
	print(f'{fund_code}用时{b - a}秒')

