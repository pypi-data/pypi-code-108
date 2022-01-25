from whatap.util.hash_util import HashUtil

DEFAULT_CAPACITY = 101
DEFAULT_LOAD_FACTOR = 0.75
TYPE = {
    'KEYS': 0,
    'VALUES': 1,
    'ENTRIES': 2
}
MODE = {
    'FORCE_FIRST': 0,
    'FORCE_LAST': 1,
    'FIRST': 2,
    'LAST': 3
}


class LinkedEntry(object):
    def __init__(self, key, value, next):
        self.key = key
        self.value = value
        self.next = next
        self.link_next = None
        self.link_prev = None

    def getKey(self):
        return self.key

    def getValue(self):
        return self.value

    def setValue(self, value):
        oldValue = self.value
        self.value = value
        return oldValue

    def hashCode(self):
        return HashUtil.hashFromString(self.key)

    def toString(self):
        return self.key + "=" + self.value


class Enumer():
    def __init__(self, map, type):
        self.map = map
        self.entry = map.header.link_next
        self.lastEnt = None
        self.type = type if type else TYPE['ENTRIES']

    def hasMoreElements(self):
        return self.map.header is not self.entry and self.entry is not None

    def nextElement(self):
        if self.hasMoreElements():
            e = self.lastEnt = self.entry
            self.entry = e.link_next
            if self.type == TYPE['KEYS']:
                return e.key
            elif self.type == TYPE['VALUES']:
                return e.value
            else:
                return e
        else:
            return


class LinkedMap(object):
    MODE = MODE

    def __init__(self, initCapacity=None, loadFactor=None):
        self.initCapacity = initCapacity if initCapacity else DEFAULT_CAPACITY
        self.loadFactor = loadFactor if loadFactor else DEFAULT_LOAD_FACTOR
        self.threshold = int(self.initCapacity * self.loadFactor)

        self.table = [None for _ in range(self.initCapacity)]
        self.header = LinkedEntry(None, None, None)
        self.header.link_next = self.header.link_prev = self.header
        self.count = 0
        self.max = 0

    def size(self):
        return self.count

    def keys(self):
        return Enumer(self, TYPE['KEYS'])

    def values(self):
        return Enumer(self, TYPE['VALUES'])

    def entries(self):
        return Enumer(self, TYPE['ENTRIES'])

    def containsKey(self, key):
        if key is None:
            return False

        tab = self.table
        index = self.hash(key) % len(tab)
        e = tab[index]

        while True:
            if not e:
                return False

            if e.key == key:
                return True
            e = e.next

    def get(self, key):
        if key is None:
            return None

        tab = self.table
        index = self.hash(key) % len(tab)
        e = tab[index]

        while True:
            if not e:
                return None

            if e.key == key:
                return e.value
            e = e.next

    def getLastValue(self):
        if self.isEmpty():
            return None
        return self.header.link_prev.value

    def hash(self, key):
        if not key:
            return 0
        return HashUtil.hashFromString(str(key)) & 0x7fffffff

    def rehash(self):
        oldCapacity = len(self.table)
        oldMap = self.table
        newCapacity = oldCapacity * 2 + 1
        newMap = [None for _ in range(newCapacity)]
        self.threshold = int(newCapacity * self.loadFactor)
        self.table = newMap

        for i in range(oldCapacity -1, -1, -1):
            old = oldMap[i]
            while True:
                if not old:
                    break

                e = old
                old = old.next
                key = e.key
                index = self.hash(key) % newCapacity
                e.next = newMap[index]
                newMap[index] = e

    def isEmpty(self):
        return self.size() == 0

    def setMax(self, max):
        self.max = max
        return self

    def isFull(self):
        return self.max > 0 and self.max <= self.count

    def put(self, key, value):
        return self._put(key, value, MODE['LAST'])

    def putLast(self, key, value):
        return self._put(key, value, MODE['FORCE_LAST'])

    def putFirst(self, key, value):
        return self._put(key, value, MODE['FORCE_FIRST'])

    def _put(self, key, value, m, noover=False):
        if noover and self.max > 0 and self.size() > self.max:
            return None

        tab = self.table
        index = self.hash(key) % len(tab)
        e = tab[index]

        while True:
            if not e:
                break

            if e.key == key:
                old = e.value
                e.value = value
                if m == MODE['FORCE_FIRST']:
                    if self.header.link_next != e:
                        self.unchain(e)
                        self.chain(self.header, self.header.link_next, e)
                elif m == MODE['FORCE_LAST']:
                    if self.header.link_prev != e:
                        self.unchain(e)
                        self.chain(self.header.link_prev, self.header, e)
                return old

            e = e.next

        if self.max > 0:
            if m == MODE['FORCE_FIRST'] or m == MODE['FIRST']:
                while self.count >= self.max:
                    k = self.header.link_prev.key
                    v = self.remove(k)
                    self.overflowed(k, v)
            elif m == MODE['FORCE_LAST'] or m == MODE['LAST']:
                while self.count >= self.max:
                    k = self.header.link_next.key
                    v = self.remove(k)
                    self.overflowed(k, v)

        if self.count >= self.threshold:
            self.rehash()
            tab = self.table
            index = self.hash(key) % len(tab)

        e = LinkedEntry(key, value, tab[index])
        tab[index] = e

        if m == MODE['FORCE_FIRST'] or m == MODE['FIRST']:
            self.chain(self.header, self.header.link_next, e)
        elif m == MODE['FORCE_LAST'] or m == MODE['LAST']:
            self.chain(self.header.link_prev, self.header, e)

        self.count += 1
        return None

    def overflowed(self, key, value):
        return

    def create(self, key):
        return

    def intern(self, key):
        return self._intern(key, MODE['LAST'])

    def _intern(self, key, m):
        tab = self.table
        index = self.hash(key) % len(tab)
        e = tab[index]

        while True:
            if not e:
                break

            if e.key == key:
                old = e.value

                if m == MODE['FORCE_FIRST']:
                    if self.header.link_next != e:
                        self.unchain(e)
                        self.chain(self.header, self.header.link_next, e)
                elif m == MODE['FORCE_LAST']:
                    if self.header.link_prev != e:
                        self.unchain(e)
                        self.chain(self.header.link_prev, self.header, e)
                return old
            e = e.next

        value = self.create(self, key)
        if not value:
            return None

        if self.max > 0:
            if m == MODE['FORCE_FIRST'] or m == MODE['FIRST']:
                while self.count >= self.max:
                    k = self.header.link_prev.key
                    v = self.remove(k)
                    self.overflowed(k, v)
            elif m == MODE['FORCE_LAST'] or m == MODE['LAST']:
                while self.count >= self.max:
                    k = self.header.link_next.key
                    v = self.remove(k)
                    self.overflowed(k, v)

        if self.count >= self.threshold:
            self.rehash()
            tab = self.table
            index = self.hash(key) % len(tab)

        e = LinkedEntry(key, value, tab[index])
        tab[index] = e

        if m == MODE['FORCE_FIRST'] or m == MODE['FIRST']:
            self.chain(self.header, self.header.link_next, e)
        elif m == MODE['FORCE_LAST'] or m == MODE['LAST']:
            self.chain(self.header.link_prev, self.header, e)

        self.count += 1
        return value

    def remove(self, key):
        if key is None:
            return None

        tab = self.table
        index = self.hash(key) % len(tab)
        e = tab[index]
        prev = None

        while True:
            if not e:
                return None

            if e.key == key:
                if prev:
                    prev.next = e.next
                else:
                    tab[index] = e.next

                self.count -= 1
                oldValue = e.value
                e.value = None
                self.unchain(e)
                return oldValue

            prev = e
            e = e.next
        return None

    def removeFirst(self):
        if self.isEmpty():
            return None
        return self.remove(self.header.link_next.key)

    def removeLast(self):
        if self.isEmpty():
            return None
        return self.remove(self.header.link_prev.key)

    def clear(self):
        tab = self.table
        for i, t in enumerate(tab):
            tab[i] = None
        self.header.link_next = self.header.link_prev = self.header
        self.count = 0

    def chain(self, link_prev, link_next, e):
        e.link_prev = link_prev
        e.link_next = link_next
        link_prev.link_next = e
        link_next.link_prev = e

    def unchain(self, e):
        e.link_prev.link_next = e.link_next
        e.link_next.link_prev = e.link_prev
        e.link_prev = None
        e.link_next = None

    def putAll(self, other):
        if not other or not isinstance(other, LinkedMap):
            return
        it = other.entries()
        while it.hasMoreElements():
            e = it.nextElement()
            self.put(e.getKey(), e.getValue())
