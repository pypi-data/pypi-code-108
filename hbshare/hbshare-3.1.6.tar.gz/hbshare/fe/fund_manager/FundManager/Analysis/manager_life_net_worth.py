import datetime

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
import os

from ..database import *
from .functions import *


class ManagerNetWorth:
	def __init__(self):
		# 基金经理编号（不重复）
		self.manager_code: str = ''
		# 中证全指日涨跌幅
		self.csi_all_share_ratio: Union[pd.DataFrame, None] = None
		# 中证全债日涨跌幅
		self.csi_all_bond_ratio: Union[pd.DataFrame, None] = None
		# 基金经理历史业绩
		self.manager_history_rtn: Union[pd.DataFrame, None] = None
		# 全部基金代码
		self.funds: List[str] = []
		# 基金历史规模
		self.fund_size: pd.DataFrame = pd.DataFrame()
		self.category_all_data = None
		self.share_funds = None
		self.bond_funds = None
		self.mix_funds = None
		# 基金经理偏股指数
		self.fund_manager_share_index: pd.DataFrame = pd.DataFrame()
		# 基金经理偏债指数
		self.fund_manager_bond_index: pd.DataFrame = pd.DataFrame()
		# 基金净值首日
		self.first_fund_day: Optional[datetime] = None
		# 基金净值最后一日
		self.last_fund_day: Optional[datetime] = None
		# 净值记录数据库
		self.record_db = record_db.initialize(SqliteDatabase('FundManagerRecord.db'))
		# 是否是每日更新任务
		self.is_everyday_work: bool = False
		# 上次更新时间
		self.latest_share_record_date: Optional[datetime] = None
		self.latest_bond_record_date: Optional[datetime] = None
		# 上次更新的指标值
		self.latest_share_record_index: Optional[float] = 0
		self.latest_bond_record_index: Optional[float] = 0
		# 混合型基金最新持仓比例公告日期
		self.mix_fund_latest_announcement = dict()
		create_tables()

	def run(self, manager_code: str, is_everyday_work: bool = False):
		return self.get_manager_all_net_worth(manager_code, is_everyday_work)

	def get_manager_all_net_worth(self, manager_code: str, is_everyday_work: bool = False):
		self.is_everyday_work = is_everyday_work
		self.manager_code = manager_code

		print('开始取数据')
		data = pd.DataFrame()

		if is_everyday_work:

			latest_share_record, latest_bond_record = get_latest_net_worth_record(self.manager_code)
			if latest_share_record == {} or latest_bond_record == {}:
				trading_date = get_all_trading_day(start_date='20210101')
				start_date = trading_date[-90]['JYRQ']
				self.latest_bond_record_date = datetime.strptime(start_date, "%Y%m%d")
				self.latest_share_record_date = datetime.strptime(start_date, "%Y%m%d")
				if latest_share_record != {}:
					self.latest_share_record_date = latest_share_record['index_date']
					self.latest_share_record_index = latest_share_record['index_value']
					self.mix_fund_latest_announcement = latest_share_record['mix_fund_latest_announcement']
				if latest_bond_record != {}:
					self.latest_bond_record_date = latest_bond_record['index_date']
					self.latest_bond_record_index = latest_bond_record['index_value']
					self.mix_fund_latest_announcement = latest_bond_record['mix_fund_latest_announcement']

			else:
				self.latest_share_record_index = latest_share_record['index_value']
				self.latest_bond_record_index = latest_bond_record['index_value']
				self.latest_share_record_date = latest_share_record['index_date']
				self.latest_bond_record_date = latest_bond_record['index_date']
				self.mix_fund_latest_announcement = latest_share_record['mix_fund_latest_announcement']
				start_date = min(self.latest_bond_record_date, self.latest_share_record_date).date().strftime("%Y%m%d")
				trading_date = get_all_trading_day(start_date=start_date)

			if len(trading_date) != 0:
				refreshed_date = self.refresh_latest_announcement()
				if refreshed_date is not None:
					start_date_time = min([refreshed_date, datetime.strptime(start_date, "%Y%m%d")])
					start_date = start_date_time.strftime("%Y%m%d")
					self.latest_share_record_date = min(self.latest_share_record_date, refreshed_date)
					self.latest_bond_record_date = min(self.latest_bond_record_date, refreshed_date)
					history_share_index = get_share_index_by_manager(self.manager_code)
					history_bond_index = get_bond_index_by_manager(self.manager_code)
					if len(history_share_index) != 0:
						self.latest_share_record_index = history_share_index[history_share_index['date'] == start_date_time]
					if len(history_bond_index) != 0:
						self.latest_bond_record_index = history_bond_index[history_bond_index['date'] == start_date_time]

				data = get_net_worth_by_manager(self.manager_code, start_date)
				data = pd.DataFrame(data)
			self.get_index_value(start_date=start_date)

		else:
			self.latest_share_record_date = datetime(1900, 1, 1)
			self.latest_bond_record_date = datetime(1900, 1, 1)
			self.refresh_latest_announcement()
			self.get_index_value()
			data = get_net_worth_by_manager(manager_code)
			data = pd.DataFrame(data)

		if len(data) == 0:
			print('该基金经理没有历史业绩。')

		else:
			data['RTN'] = data.groupby('JJDM')['JJJZ'].pct_change(fill_method='ffill').fillna(0)
			data['JZRQ'] = [transfer_datetime_str_to_datetime(str(x)) for x in data['JZRQ']]
			self.manager_history_rtn = data
			self.funds = data['JJDM'].drop_duplicates().to_list()
			self.fund_size = self.get_fund_size(self.funds)
			self.category_all_data, self.share_funds, self.bond_funds, self.mix_funds = self.generate_fund_category(self.funds)
			self.last_fund_day = self.manager_history_rtn.loc[:, 'JZRQ'].iloc[-1]
			self.first_fund_day = self.manager_history_rtn.loc[:, 'JZRQ'].iloc[0]
			print('开始处理')
			self.generate_manager_net_worth_by_category()

	def generate_manager_net_worth_by_category(self):
		be_calculated_fund_time = dict()
		share_day_rtn = list()
		bond_day_rtn = list()
		have_first_share_fund = False
		have_first_bond_fund = False
		temp_csi_share_index = []
		temp_csi_bond_index = []
		mixed_fund_status = dict()
		for rtn_date in self.csi_all_share_ratio['JYRQ'].drop_duplicates():
			if rtn_date < self.first_fund_day:
				continue
			if rtn_date > self.last_fund_day:
				break
			csi_share_rtn, csi_bond_rtn = self.get_csi_rtn(rtn_date)
			today_share = defaultdict(list)
			today_bond = defaultdict(list)
			now_time = rtn_date
			bond_day_dict = {"date": now_time}
			share_day_dict = {"date": now_time}
			rtn_df = self.manager_history_rtn[self.manager_history_rtn['JZRQ'] == rtn_date]
			for index, row in rtn_df.iterrows():
				fund_code = row.JJDM
				be_calculated_time = be_calculated_fund_time.get(fund_code, None)
				if be_calculated_time is None:
					inception_date = transfer_datetime_str_to_datetime(str(row.CLRQ))
					tenure_date = transfer_datetime_str_to_datetime(str(row.RZRQ))
					if abs((inception_date - tenure_date).days) > 5:
						be_calculated_fund_time[fund_code] = tenure_date + relativedelta(months=+3)
					else:
						be_calculated_fund_time[fund_code] = inception_date + relativedelta(months=+6)
					be_calculated_time = be_calculated_fund_time.get(fund_code, None)
				if now_time >= be_calculated_time:

					if fund_code in self.share_funds and now_time > self.latest_share_record_date:
						today_share['rtn'].append(row.RTN)
						today_share['weight'].append(self.get_fund_size_by_day(now_time, fund_code))

					elif fund_code in self.bond_funds and now_time > self.latest_bond_record_date:
						today_bond['rtn'].append(row.RTN)
						today_bond['weight'].append(self.get_fund_size_by_day(now_time, fund_code))

					else:
						now_status = mixed_fund_status.get(fund_code, None)

						if now_status is None or (now_status is not None and now_status['next_update_time'] < now_time):
							now_status_df = self.mix_funds.get(fund_code, None)
							if now_status_df is not None and len(now_status_df) > 0:
								try:
									now_status_num = now_status_df[now_status_df['public_date'] <= now_time].loc[:, 'category'].iloc[-1]
								except:
									now_status_num = 0
								try:
									next_update_time = now_status_df[now_status_df['public_date'] > now_time].loc[:, 'public_date'].iloc[0]
								except:
									next_update_time = datetime(2100, 1, 1)
								mixed_fund_status[fund_code] = dict(
									now_status=now_status_num,
									next_update_time=next_update_time
								)
								now_status = mixed_fund_status[fund_code]

						if now_status is not None:
							now_status_num = now_status['now_status']
							if now_status_num == 1 and now_time > self.latest_share_record_date:
								today_share['rtn'].append(row.RTN)
								today_share['weight'].append(self.get_fund_size_by_day(now_time, fund_code))
							elif now_status_num == -1 and now_time > self.latest_bond_record_date:
								today_bond['rtn'].append(row.RTN)
								today_bond['weight'].append(self.get_fund_size_by_day(now_time, fund_code))

			if len(today_share.get('rtn', [])) > 0:
				try:
					share_day_dict.update({"rtn": np.average(today_share['rtn'], weights=today_share['weight'])})
					have_first_share_fund = True
				except:
					share_day_dict.update({"rtn": csi_share_rtn})
				share_day_rtn.extend(temp_csi_share_index)
				share_day_rtn.append(share_day_dict)
				temp_csi_share_index = []
			elif have_first_share_fund:
				share_day_dict.update({"rtn": csi_share_rtn})
				temp_csi_share_index.append(share_day_dict)

			if len(today_bond.get('rtn', [])) > 0:
				try:
					bond_day_dict.update({"rtn": np.average(today_bond['rtn'], weights=today_bond['weight'])})
					have_first_bond_fund = True
				except:
					bond_day_dict.update({"rtn": csi_bond_rtn})
				bond_day_rtn.extend(temp_csi_bond_index)
				bond_day_rtn.append(bond_day_dict)
				temp_csi_bond_index = []
			elif have_first_bond_fund:
				bond_day_dict.update({"rtn": csi_bond_rtn})
				temp_csi_bond_index.append(bond_day_dict)
		share_df = pd.DataFrame(share_day_rtn)
		bond_df = pd.DataFrame(bond_day_rtn)
		if len(share_df) > 0:
			share_df['rtn'] += 1
			if self.latest_share_record_index == 0:
				share_df['index'] = 1000 * np.cumprod(share_df['rtn'])
			else:
				share_df['index'] = self.latest_share_record_index * np.cumprod(share_df['rtn'])
			share_df.drop(['rtn'], axis=1, inplace=True)
		if len(bond_df) > 0:
			bond_df['rtn'] += 1
			if self.latest_bond_record_index == 0:
				bond_df['index'] = 1000 * np.cumprod(bond_df['rtn'])
			else:
				bond_df['index'] = self.latest_bond_record_index * np.cumprod(bond_df['rtn'])
			bond_df.drop(['rtn'], axis=1, inplace=True)
		self.fund_manager_bond_index = bond_df
		self.fund_manager_share_index = share_df
		print('计算完毕，开始插入数据库')
		self.insert_record()

	def get_fund_size_by_day(self, date: datetime, fund: str) -> float:
		try:
			size = float(self.fund_size[(self.fund_size['JJDM'] == fund) & (self.fund_size['GGRQ'] <= date)].loc[:, 'JZZC'].iloc[-1])
		except:
			size = 0
		return size

	def get_csi_rtn(self, date: datetime):
		csi_share_rtn = self.csi_all_share_ratio[self.csi_all_share_ratio['JYRQ'] == date]['RTN'].iloc[-1]
		try:
			csi_bond_rtn = self.csi_all_bond_ratio[self.csi_all_bond_ratio['JYRQ'] == date]['RTN'].iloc[-1]
		except:
			csi_bond_rtn = 0
		return csi_share_rtn, csi_bond_rtn

	@staticmethod
	def get_fund_size(funds: List[str]) -> pd.DataFrame:
		fund_history_size = pd.DataFrame(get_fund_size(funds)).dropna()
		if len(fund_history_size) > 0:
			fund_history_size['GGRQ'] = [transfer_datetime_str_to_datetime(str(x)) for x in fund_history_size['GGRQ']]
		return fund_history_size

	def generate_fund_category(self, funds: Union[str, List[str]]):
		if isinstance(funds, str):
			funds = [funds]
		data = get_fund_category(funds)
		share_fund = []
		bond_fund = []
		mix_fund = dict()
		for cate in data:
			category = (cate["first"], cate['second'])
			if category in [('股票型', '普通股票型'), ('股票型', '股票型'), ('混合型', '偏股混合型')]:
				share_fund.append(cate['jjdm'])
			elif category in [
				('债券型', '普通债券型'),
				('债券型', '债券型'),
				('债券型', '短期纯债型'),
				('债券型', '混合债券型一级'),
				('债券型', '混合债券型二级'),
				('债券型', '债券型'),
				('债券型', '中长期纯债型'),
				('混合型', '偏债混合型')
			]:
				bond_fund.append(cate['jjdm'])
			elif category[0] == '混合型':
				# 两列，public_date和category。category为1是偏股，-1偏债，0都不是
				fund_position_ratio_df: pd.DataFrame = pd.DataFrame(self.get_fund_position_ratio_history(cate['jjdm']))
				mix_fund[cate['jjdm']]: pd.DataFrame = fund_position_ratio_df
		return data, share_fund, bond_fund, mix_fund

	def get_index_value(self, start_date: Optional[str] = None):
		all_share_index_df: pd.DataFrame = pd.DataFrame(get_csi_share_index(start_date))
		all_bond_df: pd.DataFrame = pd.DataFrame(get_csi_bond_index(start_date))
		all_share_index_df = all_share_index_df.drop(["ROW_ID"], axis=1)
		all_bond_df = all_bond_df.drop(["ROW_ID"], axis=1)
		all_share_index_df['PCT'] = all_share_index_df['SPJG'].pct_change(fill_method='ffill')
		all_bond_df['PCT'] = all_bond_df['SPJG'].pct_change(fill_method='ffill')
		all_share_index_df.fillna(0, inplace=True)
		all_bond_df.fillna(0, inplace=True)
		all_share_index_df['RTN'] = all_share_index_df['PCT']
		all_bond_df['RTN'] = all_bond_df['PCT']
		all_share_index_df['JYRQ'] = [transfer_datetime_str_to_datetime(str(x)) for x in all_share_index_df['JYRQ']]
		all_bond_df['JYRQ'] = [transfer_datetime_str_to_datetime(str(x)) for x in all_bond_df['JYRQ']]
		self.csi_all_share_ratio = all_share_index_df.drop(['SPJG'], axis=1)
		self.csi_all_bond_ratio = all_bond_df.drop(['SPJG'], axis=1)

	@staticmethod
	def get_fund_position_ratio_history(fund_id: str) -> List[dict]:
		fund_history_result = []
		fund_position_ratio_df: pd.DataFrame = pd.DataFrame(get_fund_position_ratio(fund_id))
		fund_position_ratio_df = fund_position_ratio_df.fillna(0)
		for index, row in fund_position_ratio_df.iterrows():
			date = str(row.JSRQ)
			date = transfer_datetime_str_to_datetime(date)
			if row.GPBL > 60:
				fund_history_result.append({'public_date': date, 'category': 1})
			elif row.ZQBL > 60:
				fund_history_result.append({'public_date': date, 'category': -1})
			else:
				fund_history_result.append({'public_date': date, 'category': 0})
		return fund_history_result

	def refresh_latest_announcement(self) -> Optional[datetime]:
		need_update_date: bool = False
		need_update_code = []
		latest_announcement_now = pd.DataFrame(get_latest_mix_fund_announcements_by_manager(self.manager_code))
		if len(latest_announcement_now) != 0:
			latest_announcement_now['LATEST_DATE'] = [transfer_datetime_str_to_datetime(x) for x in latest_announcement_now['LATEST_DATE']]
			temp_mix_fund_latest_announcement = self.mix_fund_latest_announcement
			for fund_code, latest_date in self.mix_fund_latest_announcement.items():
				temp_df = latest_announcement_now[latest_announcement_now['JJDM'] == fund_code]
				if len(temp_df) != 0:
					latest_date_now = temp_df.loc[:, 'LATEST_DATE'].iloc[-1]
					if latest_date_now > latest_date:
						need_update_date = True
						need_update_code.append(fund_code)
			if need_update_date:
				update_date = min([temp_mix_fund_latest_announcement[x] for x in need_update_code])
			for index, row in latest_announcement_now.iterrows():
				self.mix_fund_latest_announcement[row.JJDM] = row.LATEST_DATE.to_pydatetime()
			if need_update_date:
				return update_date


	def insert_record(self):
		if self.fund_manager_share_index is not None and len(self.fund_manager_share_index) > 0:
			last_share_date = self.fund_manager_share_index.loc[:, 'date'].iloc[-1].to_pydatetime()
			last_share_index = self.fund_manager_share_index.loc[:, 'index'].iloc[-1]
			insert_net_worth_record(
				last_share_date, self.manager_code,
				last_share_index, True, self.mix_fund_latest_announcement
			)
			values = self.fund_manager_share_index.to_dict('record')
			values = [{'date': x['date'].to_pydatetime(), 'index': x['index']} for x in values]
			save_share_index_values(self.manager_code, values)

		if self.fund_manager_bond_index is not None and len(self.fund_manager_bond_index) > 0:
			last_bond_date = self.fund_manager_bond_index.loc[:, 'date'].iloc[-1].to_pydatetime()
			last_bond_index = self.fund_manager_bond_index.loc[:, 'index'].iloc[-1]
			insert_net_worth_record(
				last_bond_date, self.manager_code,
				last_bond_index, False, self.mix_fund_latest_announcement
			)
			values = self.fund_manager_bond_index.to_dict('records')
			values = [{'date': x['date'].to_pydatetime(), 'index': x['index']} for x in values]
			save_bond_index_values(self.manager_code, values)
