import datetime

import pymysql
import pandas as pd
import requests as rq
from typing import List, Union, Optional, Dict, Tuple, Any
from collections import defaultdict
from .database_connection import *
from .database_dictionary import *


def sql_request(
		sql: str, db: str = "readonly"
) -> List[Dict]:
	init_hbs()
	post_data = []
	for i in range(1, int(1e10)):
		data = hbs.db_data_query(db, sql, is_pagination=True, page_num=i, page_size=5000)
		if data.get("success", False):
			now_data = data.get("data", [])
			if len(now_data) == 0:
				break
			post_data.extend(now_data)
		else:
			raise Exception(f'请求错误： {data.get("returnMsg", "无详细错误信息")}')
	return post_data


def base_request(
		fields: Union[None, str, List[str]],
		conditions: Union[List[str], None],
		table: str,
) -> List[dict]:
	init_hbs()
	if not fields:
		fields = "*"
	if isinstance(fields, list):
		fields = ",".join(fields)
	if isinstance(conditions, list):
		sql = f"select {fields} from {table} where {','.join(conditions)}"
	else:
		sql = f"select {fields} from {table}"
	post_data = sql_request(sql)
	return post_data


def get_manager_basic_info(
		fields: Union[None, str, List[str]],
		conditions: Union[List[str], None]
) -> pd.DataFrame:
	data = base_request(fields, conditions, "funddb.jjgg")
	data_df = pd.DataFrame(data).drop(["ROW_ID"], axis=1)
	data_df.columns = [ManagerDict.get(x.upper(), x) for x in data_df.columns]
	return data_df


def get_public_fund_net_value(
		fields: Union[None, str, List[str]],
		conditions: Union[None, List[str]]
) -> pd.DataFrame:
	if conditions is None:
		conditions = []
	conditions.append("jjdm in (select jjdm from funddb.jjxx1)")
	data = base_request(fields, conditions, "funddb.jjjz")
	data_df = pd.DataFrame(data).drop(["ROW_ID"], axis=1)
	data_df.columns = [FundNetValueDict.get(x.upper(), x) for x in data_df.columns]
	return data_df


def get_all_fund_category(is_first: bool = True) -> Dict[str, str]:
	if is_first:
		type_code = "301634"
	else:
		type_code = "301635"
	data = sql_request(f"SELECT typecode, typename FROM st_main.t_st_gg_mj where  type='{type_code}' order by typecode", "funduser")
	result = dict()
	for da in data:
		result[da['typecode']] = da['typename']
	return result


def get_csi_share_index(start_date: Optional[datetime.datetime] = None) -> List[dict]:
	start_date = '20060101' if start_date is None else start_date
	all_share_sql = f"select jyrq, spjg from funddb.zsjy where ZQDM='000985' and spjg is not null and jyrq >= {start_date} order by jyrq"
	return sql_request(all_share_sql)


def get_csi_bond_index(start_date: Optional[datetime.datetime] = None) -> List[dict]:
	start_date = '20060101' if start_date is None else start_date
	all_bond_sql = f"select jyrq, spjg from funddb.zsjy where ZQDM='H11001' and spjg is not null and jyrq >= {start_date} order by jyrq"
	return sql_request(all_bond_sql)


def get_fund_category(funds: List[str]) -> List[dict]:
	fund_category_sql = f"""
			SELECT a.jjdm, b.typename as first, c.typename as second
			From st_fund.t_st_gm_jjxx a
			join st_main.t_st_gg_mj b on a.jjfl = b.typecode
			join st_main.t_st_gg_mj c on a.ejfl = c.typecode
			where b.type='301634' and c.type = '301635' and a.jjdm in ('{"','".join(funds)}') and a.jjzt<>'c'
	"""
	return sql_request(fund_category_sql, "funduser")


def get_net_worth_by_manager(manager_code: str, start_date: Optional[str] = None) -> List[dict]:
	date = '20060101' if start_date is None else start_date
	sql = f"""
		select a.rydm,a.ryxm,a.rzrq,case when a.lrrq='19000101' then null else lrrq end as lrrq,a.jjdm,b.jjjc, b.clrq, c.jzrq,c.jjjz,c.ljjz 
		from funddb.jjgg a
		join funddb.jjxx1 b on a.jjdm=b.jjdm 
		join funddb.jjjz c on a.jjdm=c.jjdm and c.jzrq>=a.rzrq and c.jzrq>='{date}' and c.jzrq<=case when a.lrrq='19000101' or a.lrrq is null then to_char(sysdate,'yyyymmdd') else lrrq  end
		where a.rydm='{manager_code}'  
		order by c.jzrq, a.jjdm DESC
		"""
	return sql_request(sql, "readonly")


def get_fund_position_ratio(fund_code: str) -> List[dict]:
	sql = f"""
	select gpbl, zqbl, jjdm, jsrq 
	from funddb.zcpz
	where  ggrq is not null  and jjdm = '{fund_code}'
	order by ggrq
	"""
	return sql_request(sql, "readonly")


def get_fund_size(funds: List[str]) -> List[dict]:
	sql = "select jzzc, jjdm, ggrq from funddb.zcpz where jjdm in ('" + "','".join(map(str, funds)) + "') order by ggrq, jjdm"
	return sql_request(sql, "readonly")


def get_all_trading_day(start_date: Union[str, None] = None) -> List[dict]:
	start_date = '20060101' if start_date is None else start_date
	now_date = datetime.datetime.now().date().strftime("%Y%m%d")
	sql = f"select jyrq from funddb.jyrl where sfjj = 0 and jyrq > '{start_date}' and jyrq < '{now_date}' order by jyrq"
	return sql_request(sql, "readonly")


def get_fund_net_worth_days(start_date: Union[str, None] = None) -> List[dict]:
	start_date = '20060101' if start_date is None else start_date
	sql = f"""
		select a.jjdm, count(a.jzrq) as count, max(a.jzrq) as max 
		from funddb.jjjz a 
		left join funddb.jjxx1 b on a.jjdm = b.jjdm 
		where a.jjjz is not null and a.jzrq > '{start_date}' and b.cpfl = '2' and b.jjfl in ('1', '2', '3') 
		group by a.jjdm
	"""
	return sql_request(sql, "readonly")


def get_latest_mix_fund_announcements_by_manager(manager_code: str) -> List[dict]:
	sql = f"""
		select a.jjdm, max(b.jsrq) as latest_date
		from funddb.jjgg a
		join funddb.zcpz b on a.jjdm = b.jjdm
		join funddb.jjxx1 c on a.jjdm = c.jjdm
		where a.rydm = '{manager_code}' and  c.jjfl = '3' and b.jsrq < case when a.lrrq='19000101' or a.lrrq is null then to_char(sysdate,'yyyymmdd') else a.lrrq  end
		group by a.jjdm
	"""
	return sql_request(sql, "readonly")


def insert_net_worth_record(
		last_record_time: datetime,
		manager_code: str,
		index_value: float,
		is_share: bool = True,
		mix_fund_latest_announcement: Optional[dict] = None
):
	now_time = datetime.datetime.now()
	record_type = 'share' if is_share else 'bond'
	NetWorthRecord.create(
		index_date=last_record_time,
		fund_manager_code=manager_code,
		record_date=now_time,
		record_type=record_type,
		index_value=index_value,
		mix_fund_latest_announcement=str(mix_fund_latest_announcement),
	)


def get_latest_net_worth_record(fund_manager_code: str) -> List[dict]:
	import datetime
	result = []
	for record_type in ['share', 'bond']:
		try:
			record = (
				NetWorthRecord
				.select(
					fn.MAX(NetWorthRecord.record_date),
					NetWorthRecord.index_date,
					NetWorthRecord.record_type,
					NetWorthRecord.index_value,
					NetWorthRecord.mix_fund_latest_announcement
				)
				.where(NetWorthRecord.fund_manager_code == fund_manager_code, NetWorthRecord.record_type == record_type)
				.group_by(NetWorthRecord.fund_manager_code)
				.order_by(-NetWorthRecord.record_date)
				.get()
			)
			record = dict(
				record_date=record.record_date,
				index_date=record.index_date,
				record_type=record_type,
				index_value=record.index_value,
				mix_fund_latest_announcement=eval(record.mix_fund_latest_announcement)
			)
		except:
			record = dict()
		result.append(record)
	return result


def get_share_index_by_manager(manager_code: str):
	history_records = (
		ShareIndex
		.select()
		.where(ShareIndex.manager_code == manager_code)
		.order_by(ShareIndex.index_date)
	)
	try:
		return pd.DataFrame(list(history_records.to_dicts()))
	except:
		return pd.DataFrame()


def get_bond_index_by_manager(manager_code: str):
	history_records = (
		BondIndex
		.select()
		.where(BondIndex.manager_code == manager_code)
		.order_by(BondIndex.index_date)
	)
	try:
		return pd.DataFrame(list(history_records.to_dicts()))
	except:
		return pd.DataFrame()


def save_share_index_values(manager_code: str, index_values: List[dict]):
	to_be_deleted = (
		ShareIndex
		.delete()
		.where(ShareIndex.manager_code == manager_code, ShareIndex.index_date.in_([x['date'] for x in index_values]))
	)
	try:
		to_be_deleted.execute()
	except:
		pass
	index = [{'manager_code': manager_code, 'index_date': x['date'], 'index_value': x['index']} for x in index_values]
	ShareIndex.insert_many(index).execute()


def save_bond_index_values(manager_code: str, index_values: List[dict]):
	to_be_deleted = (
		BondIndex
		.delete()
		.where(BondIndex.manager_code == manager_code, BondIndex.index_date.in_([x['date'] for x in index_values]))
	)
	try:
		to_be_deleted.execute()
	except:
		pass
	index = [{'manager_code': manager_code, 'index_date': x['date'], 'index_value': x['index']} for x in index_values]
	BondIndex.insert_many(index).execute()


def create_tables():
	record_db.create_tables([NetWorthRecord, ShareIndex, BondIndex])
