from collections.abc import Mapping


class CodelistCode(Mapping):
    def __init__(self, data, extension_name=None):
        self.data = data
        self.extension_name = extension_name

    def __eq__(self, other):
        if isinstance(other, CodelistCode):
            return self.data == other.data and self.extension_name == other.extension_name
        return dict.__eq__(self.data, other)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __lt__(self, other):
        return self.data['Code'] < other.data['Code']

    def __repr__(self):
        if self.extension_name:
            return f'CodelistCode(data={self.data!r}, extension_name={self.extension_name!r})'
        return f'CodelistCode(data={self.data!r})'

    def pop(self, *args):
        return self.data.pop(*args)
