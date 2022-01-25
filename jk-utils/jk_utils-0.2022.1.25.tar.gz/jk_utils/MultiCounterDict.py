



class MultiCounterDict(dict):

	def __init__(self):
		pass
	#

	def increment(self, *keys):
		length = len(keys)
		dParent = self
		for i in range(0, length):
			bIsLast = i == (length - 1)
			key = keys[i]

			if bIsLast:
				dParent[key] = dParent.get(key, 0) + 1
			else:
				d = dParent.get(key, None)
				if d is None:
					d = {}
					dParent[key] = d
				dParent = d
	#

#

