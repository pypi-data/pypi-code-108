from datetime import datetime

from .exceptions import ParseError


class DataField:
    def __init__(self, start, end, justification='r', fill_char=' ', pad_char=' '):
        self.start = start
        self.end = end
        self.justification = justification
        self.fill_char = fill_char
        self.pad_char = pad_char

    def _strip_padding(self, field_content):
        if self.justification == 'r':
            for i in range(len(field_content)):
                if field_content[i] == self.pad_char:
                    continue
                else:
                    return field_content[i:]
        else:
            for i in reversed(range(len(field_content))):
                if field_content[i] == self.pad_char:
                    continue
                else:
                    return field_content[:i+1]

    def parse(self, row_content):
        field_content = row_content[self.start:self.end]
        if field_content == self.fill_char*(self.end-self.start):
            return None
        return self._strip_padding(field_content)


class TextField(DataField):
    pass


class DateField(DataField):
    def parse(self, row_content):
        field_content = row_content[self.start:self.end]
        try:
            return datetime.strptime(field_content, ' %y%j')
        except ValueError as e:
            raise ParseError(e)


class NumericField(DataField):
    def parse(self, row_content):
        field_content = super().parse(row_content)
        if field_content:
            try:
                return int(field_content)
            except (TypeError, ValueError) as e:
                raise ParseError(e)
        else:
            return None


class ZeroFilledField(DataField):
    def __init__(self, start, end, fill_char='0', **kwargs):
        super().__init__(start, end, fill_char=fill_char, **kwargs)


class EnumField(DataField):
    def __init__(self, start, end, enum, **kwargs):
        self.enum = enum
        super().__init__(start, end, **kwargs)

    def parse(self, row_content):
        field_content = row_content[self.start:self.end]
        try:
            return self.enum(field_content)
        except ValueError as e:
            raise ParseError(e)


class StaticField(DataField):
    def __init__(self, start, end, value, **kwargs):
        self.value = value
        super().__init__(start, end, **kwargs)

    def parse(self, row_content):
        field_content = super().parse(row_content)
        if field_content == self.value:
            return field_content
        else:
            raise ParseError(
                "Field content '%s' does not match expected static value '%s'"
                % (field_content, self.value)
            )
