import gspread

from typing import Union
from google.oauth2.service_account import Credentials

class GoogleDriveController:
	scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

	@classmethod
	def get_spreadsheet_by_name_file(cls, google_secret_file:str, spreadsheet:str, sheet_index:int=0):
		creds = Credentials.from_service_account_file(google_secret_file, scopes=cls.scope)
		sheet = cls.__open_spreadsheet_name(creds, spreadsheet, sheet_index)
		result = cls.__get_spreadsheet_as_string(sheet)
		return result

	@classmethod
	def get_spreadsheet_by_name_dict(cls, google_secret_dict:dict, spreadsheet:str, sheet_index:int=0):
		creds = Credentials.from_service_account_info(google_secret_dict, scopes=cls.scope)
		sheet = cls.__open_spreadsheet_name(creds, spreadsheet, sheet_index)
		result = cls.__get_spreadsheet_as_string(sheet)
		return result

	@classmethod
	def get_spreadsheet_by_url_file(cls, google_secret_file:str, spreadsheet_url:str, sheet_index:int=0):
		creds = Credentials.from_service_account_file(google_secret_file, scopes=cls.scope)
		sheet = cls.__open_spreadsheet_url(creds, spreadsheet_url, sheet_index)
		result = cls.__get_spreadsheet_as_string(sheet)
		return result

	@classmethod
	def get_spreadsheet_by_url_dict(cls, google_secret_dict:dict, spreadsheet_url:str, sheet_index:int=0):
		creds = Credentials.from_service_account_info(google_secret_dict, scopes=cls.scope)
		sheet = cls.__open_spreadsheet_url(creds, spreadsheet_url, sheet_index)
		result = cls.__get_spreadsheet_as_string(sheet)
		return result

	@classmethod
	def update_cell_spreadsheet_by_name_file(cls, google_secret_file:str, spreadsheet:str, cell:str, value:Union[str, int, float], sheet_index:int=0):
		creds = Credentials.from_service_account_file(google_secret_file, scopes=cls.scope)
		sheet = cls.__open_spreadsheet_name(creds, spreadsheet, sheet_index)
		sheet.update(cell, value)
		result = cls.__get_spreadsheet_as_string(sheet)
		return result

	@classmethod
	def update_cell_spreadsheet_by_name_dict(cls, google_secret_dict:dict, spreadsheet:str, cell:str, value:Union[str, int, float], sheet_index:int=0):
		creds = Credentials.from_service_account_info(google_secret_dict, scopes=cls.scope)
		sheet = cls.__open_spreadsheet_name(creds, spreadsheet, sheet_index)
		sheet.update(cell, value)
		result = cls.__get_spreadsheet_as_string(sheet)
		return result

	@classmethod
	def update_cell_spreadsheet_by_url_file(cls, google_secret_file:str, spreadsheet_url:str, cell:str, value:Union[str, int, float], sheet_index:int=0):
		creds = Credentials.from_service_account_file(google_secret_file, scopes=cls.scope)
		sheet = cls.__open_spreadsheet_url(creds, spreadsheet_url, sheet_index)
		sheet.update(cell, value)
		result = cls.__get_spreadsheet_as_string(sheet)
		return result

	@classmethod
	def update_cell_spreadsheet_by_url_dict(cls, google_secret_dict:dict, spreadsheet_url:str, cell:str, value:Union[str, int, float], sheet_index:int=0):
		creds = Credentials.from_service_account_info(google_secret_dict, scopes=cls.scope)
		sheet = cls.__open_spreadsheet_url(creds, spreadsheet_url, sheet_index)
		sheet.update(cell, value)
		result = cls.__get_spreadsheet_as_string(sheet)
		return result


	def __open_spreadsheet_name(creds:Credentials, spreadsheet:str, sheet_index:int):
		client = gspread.authorize(creds)
		return client.open(spreadsheet).get_worksheet(sheet_index)

	def __open_spreadsheet_url(creds:Credentials, spreadsheet_url:str, sheet_index:int):
		client = gspread.authorize(creds)
		return client.open_by_url(spreadsheet_url).get_worksheet(sheet_index)

	def __get_spreadsheet_as_string(sheet):
		values = sheet.get_all_values()
		head = values.pop(0)
		return [{head[i]: col for i, col in enumerate(row)} for row in values]