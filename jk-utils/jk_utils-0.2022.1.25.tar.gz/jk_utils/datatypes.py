

def _fullname(o):
	module = o.__class__.__module__
	if module is None or module == str.__class__.__module__:
		return o.__class__.__name__		# Avoid reporting __builtin__
	else:
		#items = module.split(".")
		#if items[-1] == o.__class__.__name__:
		#	return module
		#else:
		#	return module + '.' + o.__class__.__name__
		return module + '.' + o.__class__.__name__
#




def getTypeAsStr(value, fqn:bool = False, bAllowNull:bool = True):
	assert isinstance(fqn, bool)

	if value is None:
		if bAllowNull:
			return "(null)"
		else:
			raise Exception("Value is (null)!")

	if isinstance(value, bool):
		return "bool"

	if isinstance(value, int):
		return "int"

	if isinstance(value, float):
		return "float"

	if isinstance(value, str):
		return "str"

	if isinstance(value, (list, tuple)):
		assert len(value) > 0

		elementType = None
		firstValue = None
		for v in value:
			if elementType is None:
				if v is not None:
					elementType = type(v)
					firstValue = v
			else:
				if v is not None:
					assert elementType == type(v)

		if firstValue is None:
			raise Exception("Only (null)s!")

		return getTypeAsStr(v, fqn, False) + "[]"

	if isinstance(value, dict):
		assert len(value) > 0
		keyType = None
		elementType = None
		firstKey = None
		firstValue = None
		for k in value.keys():
			v = value[k]

			if keyType is None:
				assert k is not None
				keyType = type(k)
				firstKey = k
			else:
				assert keyType == type(k)

			if elementType is None:
				if v is not None:
					elementType = type(v)
					firstValue = v
			else:
				if v is not None:
					assert elementType == type(v)

		if firstKey is None:
			raise Exception("Only (null)s!")
		if firstValue is None:
			raise Exception("Only (null)s!")

		return "dict<" + getTypeAsStr(firstKey, fqn, False) + "," + getTypeAsStr(firstValue, fqn, False) + ">"

	if fqn:
		s = _fullname(value)
	else:
		s = value.__class__.__name__
		pos = s.rfind(".")
		if pos:
			s = s[pos + 1:]
	return s
#




