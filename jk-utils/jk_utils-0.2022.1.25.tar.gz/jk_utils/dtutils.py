

import os
import sys
import datetime





class dtutils(object):

	__EPOCH = datetime.datetime.utcfromtimestamp(0)



	@staticmethod
	def epochTimeStamp():
		return dtutils.__EPOCH

	#



	@staticmethod
	def dateTimeToSecondsSinceEpoch(dt):
		return (dt - dtutils.__EPOCH).total_seconds()

	#



	@staticmethod
	def dateTimeToMillisecondsSinceEpoch(dt):
		return (dt - dtutils.__EPOCH).total_seconds() * 1000

	#



	@staticmethod
	def secondsSinceEpochToDateTime(seconds):
		datetime.datetime.utcfromtimestamp(seconds)

	#



	@staticmethod
	def nowInSecondsSinceEpoch():
		return (datetime.datetime.utcnow() - dtutils.__EPOCH).total_seconds()

	#



	@staticmethod
	def nowInMillisecondsSinceEpoch():
		return int((datetime.datetime.utcnow() - dtutils.__EPOCH).total_seconds() * 1000)

	#



