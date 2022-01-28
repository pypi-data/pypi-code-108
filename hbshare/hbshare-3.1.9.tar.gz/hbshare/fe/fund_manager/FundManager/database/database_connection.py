import hbshare as hbs
from peewee import *


def init_hbs():
	hbs.set_token('Howbuy!')


record_db = DatabaseProxy()


class NetWorthRecord(Model):
	index_date = DateTimeField()
	index_value = FloatField()
	fund_manager_code = CharField()
	record_date = DateTimeField()
	record_type = CharField()
	mix_fund_latest_announcement = TextField()

	class Meta:
		database = record_db


class ShareIndex(Model):
	manager_code = CharField()
	index_date = DateTimeField()
	index_value = FloatField()

	class Meta:
		database = record_db


class BondIndex(Model):
	manager_code = CharField()
	index_date = DateTimeField()
	index_value = FloatField()

	class Meta:
		database = record_db

