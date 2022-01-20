# Author: @v1s1t0r999
# Created ON [14-10-21 @ 12:28 PM]

import requests as r
from requests import *
import json


class CountryNotFound(Exception):
	pass


class InternetConnectionError(Exception):
	pass



class CovidClient:
	"""
	BASE CLIENT FOR GETTING THE INFO FROM <https://disease.sh>
	:cls: Usage
	```py
	# Import the lib
	from covid import CovidClient

	# Initialize the client
	cov = CovidClient()

	# Load the Country
	cov.load_country("Poland")

	# Get the covid info!!
	### Country Info
	cov.country
	cov.population
	cov.flag_url
	cov.country_id

	### Total info
	cov.total_cases
	cov.total_death
	cov.total_recover
	cov.total_tests

	### Specially for cases
	cov.active_cases
	cov.critical_cases

	### Today's Info
	cov.today_cases
	cov.today_death
	cov.today_recover
	#cov.today_tests -> Not Supported form the API side

	### Percentage info
	cov.percent_cases
	cov.percent_death
	cov.percent_test
	#cov.percent_recover -> Not Supported form the API side


	### OR
	self.data # A dict containing all these info...not really required tbh.....and tbh means "To Be Honest"
	```
	"""

	def __init__(self):
		self.country=""
		self.total_cases=""
		self.total_death=""
		self.total_recover=""
		self.total_tests=""
		self.active=""
		self.critical=""
		self.today_cases=""
		self.today_deaths=""
		self.today_recover=""
		self.percent_cases=""
		self.percent_death=""
		self.percent_test=""
		self.population=""
		self.flag_url=""
		self.country_id=""
		self.data={}


	def _data(self):
		"""Internal Function to load data"""
		try:
			s = r.get(f"https://corona.lmao.ninja/v3/covid-19/countries/{self.country}")
		except ConnectionError:
			raise 
		try:
			s.json()['message']
			return False
		except KeyError:
			self.data=json.dumps(s.json(),indent=4)
			return s.json()
		
	def load_country(self,country:str):
		"""
		CovidClient.load_country("MY COUNTRY!!")
		"""
		self.country=country.replace(" ","%20")
		d = self._data()
		if self._data() is False:
			raise CountryNotFound("No such Country Found!!")
			return False
		else:
			self.total_cases=d['cases']
			self.total_death=d['deaths']
			self.total_recover=d['recovered']
			self.total_tests=d['tests']
			self.active = d['active']
			self.critical = d['critical']
			self.today_deaths = d['todayDeaths']
			self.today_cases = d['todayCases']
			self.today_recover=d['todayRecovered']
			self.percent_cases=int(d['oneCasePerPeople'])/int(d['population'])*100
			self.percent_death=int(d['oneDeathPerPeople'])/int(d['population'])*100
			self.percent_test=int(d['oneTestPerPeople'])/int(d['population'])*100
			self.population=d['population']
			self.flag_url=d['countryInfo']['flag']
			self.country_id=d['countryInfo']['_id']
			return True
