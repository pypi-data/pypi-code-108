#! /usr/bin/env python

# TestInterface.py
# implements a generic test web interface for guavacado
# made by Joshua Huseman, jhuseman@alumni.nd.edu
# Created: 06/08/2016
# Updated: 06/08/2016
# Updated: 03/11/2019 - use guavacado imports, instead of old names

import guavacado
import json

import random

import threading
import time

class TestInterface(guavacado.WebInterface):
	def __init__(self,host):
		self.host = host
		self.connect('/test/:id/:it','GET_ID','GET')
	
	def GET_ID(self,id,it):
		output = {'result':'success'}
		try:
			output['id'] = id
			output['it'] = it
			output['rand'] = random.random()
		except Exception as ex:
			output['result'] = 'error'
			output['message'] = str(ex)
		return json.dumps(output, encoding='latin-1')

if __name__ == '__main__':
	host = guavacado.WebHost(12345)
	TestInterface(host)
	threading.Thread(target=host.start_service).start()
	try:
		while True:
			time.sleep(100)
	except KeyboardInterrupt:
		host.stop_service()
	
