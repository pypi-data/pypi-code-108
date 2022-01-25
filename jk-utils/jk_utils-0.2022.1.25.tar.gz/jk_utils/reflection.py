


import inspect




def isStaticMethod(theClass, methodName):
	try:
		value = getattr(theClass, methodName)
	except:
		# Such a method does not exist
		return False

	assert getattr(theClass, methodName) == value

	for cls in inspect.getmro(theClass):
		if inspect.isroutine(value):
			if methodName in cls.__dict__:
				binded_value = cls.__dict__[methodName]
				if isinstance(binded_value, staticmethod):
					return True
	return False
#



