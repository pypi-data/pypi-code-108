


import weakref




class WeakValueList:

	################################################################################################################################
	#### Public Methods
	################################################################################################################################

	def __init__(self):
		self.__weakItems = []
	#

	################################################################################################################################
	#### Public Properties
	################################################################################################################################

	#
	# Get a list of all objects that are still alive.
	# Cleanup of references that are no longer needed is performed automatically if this method is called.
	#
	@property
	def itemsAlive(self) -> list:
		toDelete = []
		ret = []

		for weakRef in self.__weakItems:
			obj = weakRef()
			if obj is not None:
				ret.append(obj)
			else:
				toDelete.append(weakRef)

		for weakRef in toDelete:
			self.__weakItems.remove(weakRef)
			del weakRef

		return ret
	#

	################################################################################################################################
	#### Public Methods
	################################################################################################################################

	#
	# Remove an existing (but maybe already garbage collected) object from the list.
	#
	def remove(self, existingObj):
		assert existingObj is not None

		toDelete = []

		for weakRef in self.__weakItems:
			obj = weakRef()
			if obj is not None:
				if existingObj == obj:
					toDelete(weakRef)
			else:
				toDelete.append(weakRef)

		for weakRef in toDelete:
			self.__weakItems.remove(weakRef)
			del weakRef
	#

	def append(self, obj):
		assert obj is not None

		self.__weakItems.append(weakref.ref(obj))
	#

	def clear(self):
		self.__weakItems.clear()
	#

#













