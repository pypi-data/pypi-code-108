import pandas as pd
import simdjson

from FundManager.database import *


if __name__ == "__main__":
	# get_manager_basic_info(
	# 	['RYXB', 'RYXM', 'RYXL', 'CYNX', 'RZRQ', 'LRRQ', 'RYZT', 'JJDM', 'GGRQ', "RYDM"], None
	# ).sort_values(["人员代码", "入职日期"]).to_csv("基金经理信息.csv", index=False)
	all_days = len(get_all_trading_day('20210101'))
	fund_net_worth_days = pd.DataFrame(get_fund_net_worth_days('20210101'))
	weekly_funds = []
	for index, row in fund_net_worth_days.iterrows():
		if row.COUNT < all_days:
			weekly_funds.append({'code': row.JJDM, 'count': row.COUNT, 'max_date': row.MAX})
	print(len(weekly_funds) / all_days)
	# get_public_fund_net_value(
	# 	["JJDM", "JZRQ", "LJJZ", "JJJZ"], None
	# ).sort_values(["基金代码", "净值日期"]).to_csv("基金净值信息.csv", index=False)
	# simdjson.dump(get_all_fund_category(), open('database/公募基金一级分类.json', 'w'), indent=2, ensure_ascii=False)
	# simdjson.dump(get_all_fund_category(is_first=False), open('database/公募基金二级分类.json', 'w'), indent=2, ensure_ascii=False)


