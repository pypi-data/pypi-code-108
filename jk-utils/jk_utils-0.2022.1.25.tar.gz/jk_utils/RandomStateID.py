

import os
import string
import random














class RandomStateID(object):

	def __init__(self):
		self.__randomStateID = self.__randomString()
	#

	def __randomString(self, stringLength:int = 32) -> str:
		letters = string.ascii_letters + string.digits
		return "".join(random.choice(letters) for i in range(stringLength))
	#

	def touch(self) -> str:
		self.__randomStateID = self.__randomString()
		return self.__randomStateID
	#

	@property
	def randomStateID(self) -> str:
		return self.__randomStateID
	#

	def __str__(self):
		return self.__randomStateID
	#

#






















