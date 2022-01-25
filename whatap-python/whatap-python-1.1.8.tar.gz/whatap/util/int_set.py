import threading
import whatap.io.data_outputx as data_outputx
from io import StringIO

class IntSetry(object):
	def __init__(self, key=0, next= None):
		self.key = key
		self.next = next

	def clone(self):
		return  IntSetry(self.key, None if self.next is None else next.clone())

	def getKey(self):
		return self.key

	def equals(self, o):
		if not instance(o,IntSetry):
			return False

		return self.key == o.getKey()

	def hashCode(self):
		return self.key

	def toString(self):
		return str(key)

class Enumer(object):
	def __init__(self, table):
		self.table = table
		self.index = len(table)
		self.entry = None
		self.lastReturned = None

	def hasMoreElements(self):
		while self.entry is None and self.index > 0:
			self.index -= 1
			self.entry = self.table[self.index]

		return self.entry is not None

	def nextInt(self):
		while self.entry is None and self.index > 0:
			self.index -= 1
			self.entry = self.table[self.index]
		if self.entry is not None:
			e = self.lastReturned = self.entry
			self.entry = e.next
			return e.key
		raise Exception("no more next")


class EmptyEnumer(object):
	def hasMoreElements(self):
		return 0

	def nextInt(self):
		return False

class IntSet(object):
	emptyEnumer = EmptyEnumer()

	def __init__(self, initCapacity = int(101), loadFactor = float(0.75)):
		self.count = 0
		if initCapacity < 0:
			raise Exception("Capacity Error: " + initCapacity)
		if loadFactor <= 0:
			raise Exception("Load Count Error: " + loadFactor)
		if initCapacity == 0:
			initCapacity = 1
		self.loadFactor = loadFactor;
		self.table = [None]*initCapacity
		self.threshold = int(initCapacity * loadFactor)

		self.lock = threading.Lock()

	def size(self):
		return self.count

	def values(self):
		try:
			self.lock.acquire()
			return Enumer(self.table)
		finally:
			self.lock.release()

	def contains(self, key):
		buk = self.table
		index = (key & data_outputx.INT_MAX_VALUE) % len(buk)
		e = buk[index]
		while e is not None:
			if e.key == key:
				return True
			e = e.next

		return False

	def get(self, key):
		buk = self.table
		index = (key & data_outputx.INT_MAX_VALUE) % len(buk)

		e = buk[index]
		while e is not None:
			if e.key == key:
				return e.key

		return 0

	def rehash(self):
		oldCapacity = len(self.table)
		oldMap = self.table
		newCapacity = oldCapacity * 2 + 1
		newMap = [None]*newCapacity
		self.threshold = int(newCapacity * loadFactor)
		self.table = newMap

		for i in range(oldCapacity, 1, -1):
			old = oldMap[i]
			while old is not None:
				e = old
				old = old.next
				index = (e.key & data_outputx.INT_MAX_VALUE) % newCapacity
				e.next = newMap[index]
				newMap[index] = e

	def putAll(self, values):
		if not values :
			return
		for v in values:
			self.put(v)

	def put(self, value):
		buk = self.table
		index = (value & data_outputx.INT_MAX_VALUE) % len(buk)
		e = buk[index]
		while  e is not None:
			if e.key == value:
				return False
			e = e.next
		if self.count >= self.threshold:
			self.rehash()
			buk = self.table
			index = (value & Integer.MAX_VALUE) % len(buk)

		e = IntSetry(value, buk[index])
		buk[index] = e
		self.count +=1
		return True

	def remove(self, key):
		buk = self.table
		index = (key & data_outputx.INT_MAX_VALUE) % len(buk)
		e = buk[index]
		prev = None
		while e is not None:
			if e.key == key:
				if prev is not None:
					prev.next = e.next
				else:
					buk[index] = e.next
				self.count-=1
				return key
			prev = e, e = e.next

		return 0

	def clear(self):
		buk = table
		for index in range(len(buk), 0, -1):
			buk[index] = None
		self.count = 0

	def toString(self):
		max = self.size() - 1
		buf = StringIO()
		it = this.values()
		buf.write("{")
		for i in range(max):
			key = it.nextInt()
			buf.write(str(key))
			if i < max:
				buf.write(", ")
		buf.write("}")

		return buf.getvalue()

	def toArray(self):
		_keys = int[self.size()]
		en = self.values()
		for i in range(len(_keys)):
			_keys[i] = en.nextInt()
		return _keys

	def isExistElseAdd(self, value):
		return self.put(value) == False

	def putStrHash(self, s):
		if s is not None:
			self.put(hash(s))
