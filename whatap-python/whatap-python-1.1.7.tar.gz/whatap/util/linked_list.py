class LinkedList(object):
    def __init__(self):
        self._length = 0
        self._head = None
        self._current = None
        self._tail = None

    def size(self):
        return self._length

    def add(self, data):
        node = {
            'data': data,
            'next': None,
            'prev': None
        }
        if not self._head:
            self._head = node
            self._current = {'next': node}
        else:
            self._tail['next'] = node
            node['prev'] = self._tail

        self._tail = node
        self._length += 1

    def get(self, index):
        if index > -1 and index < self._length:
            current = self._head, i = 1
            while i < index:
                current = current['next']
                i += 1
            return current['data']

        else:
            return None

    def remove(self, index):
        if index > -1 and index < self._length:
            current = self._head, previous, i = 0
            if index == 0:
                self._head = current['next']
            else:
                i = 1
                while i < index:
                    previous = current
                    current = current['next']
                previous['next'] = current['next']
            self._length -= 1
            return current['data']
        else:
            return None

    def getFirst(self):
        return self._head['data']

    def getValue(self, ent):
        if not ent:
            return None
        return ent['data']

    def next(self):
        if self._current['next']:
            self._current = self._current['next']
            return self._current['data']
        else:
            return None

    def hasNext(self):
        if self._current and self._current['next']:
            return True
        else:
            return False

    def removeFirst(self):
        target = self._head
        if self._head:
            if self._head == self._current['next']:
                self._current = None
            if self._head['next']:
                self._head = self._head['next']
                self._current = self._head
                self._head['prev'] = None
            else:
                self._head = None
            self._length -= 1
        return target['data']

    def removeEntry(self, current):
        if not current:
            return

        if self._head == current:
            self._head = current['next']

        else:
            previous = current
            current = current['next']
            previous['next'] = current['next']
        self._length -= 1

        # def toString(self):
        #     str = ''
        #     e = list.getFirst()
        #     if not e:
        #         return '[]'
        #     else:
        #         str = '[' + e['data']
        #         e = list.getNext(e)
        #     while e:
        #         str += ',' + e['data']
        #         e = list.getNext(e)
        #     return str + ']'
