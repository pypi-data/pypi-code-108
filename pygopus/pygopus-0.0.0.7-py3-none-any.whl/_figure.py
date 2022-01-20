from typing import List, MutableSequence


class Row:
    def make(self):
        ...


class Figure(MutableSequence):
    data: List[Row]

    def __init__(self, initlist=None):
        self.data = []
        if initlist is not None:
            # XXX should this accept an arbitrary sequence?
            if type(initlist) == type(self.data):
                self.data[:] = initlist
            elif isinstance(initlist, Figure):
                print("here")
                self.data[:] = initlist.data[:]
            else:
                self.data = list(initlist)

    def __delitem__(self):
        ...

    def __getitem__(self):
        ...

    def __setitem__(self):
        ...

    def __len__(self):
        ...

    def __iter__(self):
        return self.data.__iter__()

    def insert(self):
        ...


class T(Figure):
    ...


f = Figure([1, 2, 3])
t = T([7, 8, 9])

for i in f:
    ...
