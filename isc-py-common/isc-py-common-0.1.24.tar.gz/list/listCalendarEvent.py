class Node:
    def __init__(self, item=None, next=None):
        self.item = item
        self.next = next

    def __str__(self):
        # return f'{self.item}, next=[{self.next.item if self.next else None}]'
        return f'{self.item}'


class LinkedList:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v() if callable(v) else v)

        self.first = None
        self.last = None
        self._length = 0

    def print(self, comment=''):
        print('\n')
        print(f'======================================================= {comment} ({self.__hash__()}): =======================================================')
        print(str(self))
        print(f'===================================================== end {comment} ({self.__hash__()}) ({self.length}): =====================================================')

    def _fill_blanks(self, lenght):
        res = ''
        for i in range(lenght):
            res += ' '
        return res

    def __str__(self):
        if self.first is not None:
            current = self.first

            out = f'{self.__class__.__name__} [\n{self._fill_blanks(4)}{str(current)}\n'

            while current.next is not None:
                current = current.next
                out += f'{self._fill_blanks(4)}{str(current)}\n'
            return f'{out}]'

        return f'{self.__class__.__name__} []'

    def clear(self):
        self.__init__()

    @property
    def length(self):
        self._length = 0

        if self.first is not None:
            self._length += 1
            current = self.first

            while current.next is not None:
                current = current.next
                self._length += 1

        return self._length

    # Добавление элементов в конец списка.
    def add(self, item):
        self._length += 1
        if self.first is None:
            # self.first и self.last будут указывать на одну область памяти
            self.last = self.first = Node(item=item)
        else:
            # здесь, уже на разные, т.к. произошло присваивание
            self.last.next = self.last = Node(item=item)

    # А не научиться ли нам вставлять эл-ты в начало списка?)
    def push(self, item):
        self._length += 1
        if self.first is None:
            self.last = self.first = Node(item=item)
        else:
            self.first = Node(item=item, next=self.first)

    # Вставка в позицию
    def insert(self, pos, item):
        if self.first is None:
            self.last = self.first = Node(item=item, next=None)
            return

        if pos == 0:
            self.first = Node(item=item, next=self.first)
            return

        curr = self.first
        count = 0

        while curr is not None:
            count += 1
            if count == pos:
                curr.next = Node(item=item, next=curr.next)
                if curr.next.next is None:
                    self.last = curr.next
                break
            curr = curr.next

    # Удаление головного элемента
    def pop(self):
        oldhead = self.first
        if oldhead is None:
            return None

        self.first = oldhead.next
        if self.first is None:
            self.last = None

        return oldhead.value

    # Удаление элемента из списка
    def Del(self, pos):
        if (self.first is None):
            return
        curr = self.first
        count = 0
        if pos == 0:
            self.first = self.first.next
            return
        while curr is not None:
            if count == pos:
                if curr.next is None:
                    self.last = curr
                old.next = curr.next
                break
            old = curr
            curr = curr.next
            count += 1

    # Вставка в позицию
    def replace(self, pos, item):
        self.insert(pos, item)
        self.Del(pos + 1)

    # Вставка элемента в отсортированный список
    def sorted_insert(self, item):
        if self.first is None:
            self.first = Node(item, self.last)
            return
        if self.first.item > item:
            self.first = Node(item, self.first)
            return
        curr = self.first
        while curr is not None:
            if curr.value > item:
                old.next = Node(item, curr)
                return
            old = curr
            curr = curr.next
        self.last = old.next = Node(item, None)

    # удаление повторяющихся значений
    def remove_duplicates(self):
        if (self.first is None):
            return
        old = curr = self.first
        while curr is not None:
            _del = 0
            if curr.next is not None:
                if curr.value == curr.next.value:
                    curr.next = curr.next.next
                    _del = 1
            if _del == 0:
                curr = curr.next

    def __getitem__(self, key):  # поддержка обращения по ключу
        length = 0
        current = None
        if self.first is not None:
            current = self.first
            # while key != length or current.next is not None:
            while key != length:
                if current.next is not None:
                    current = current.next
                    length += 1
                else:
                    current = None
                    break

            if key == length:
                current = current.item

        return current

    def find(self, item, func_equal=None):
        curr = self.first
        while curr is not None:
            if func_equal:
                res = func_equal(item, curr.item)
            else:
                res = curr == item

            if res:
                return curr.item
            curr = curr.next
        return None
