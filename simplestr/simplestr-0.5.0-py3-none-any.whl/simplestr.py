def gen_str(cls):
    def __str__(self):
        class_name = type(self).__name__
        fields_texts = []
        for field in vars(self).items():
            field_name = str(field[0])
            field_value = str(field[1])
            field_text = field_name + '=' + field_value
            fields_texts.append(field_text)
        fields_texts_merged = ', '.join(fields_texts)
        return class_name + '{' + fields_texts_merged + '}'

    cls.__str__ = __str__
    return cls


def gen_repr(cls):
    def __repr__(self):
        return str(self)

    cls.__repr__ = __repr__
    return cls


def gen_eq(cls):
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        for field in vars(self).items():
            field_name = str(field[0])
            self_field_value = getattr(self, field_name)
            other_field_value = getattr(other, field_name)
            if self_field_value != other_field_value:
                return False
        return True

    def __hash__(self):
        return hash(str(self))

    cls.__eq__ = __eq__
    cls.__hash__ = __hash__
    return cls


def gen_str_repr(cls):
    cls = gen_str(cls)
    cls = gen_repr(cls)
    return cls


def gen_str_repr_eq(cls):
    cls = gen_str(cls)
    cls = gen_repr(cls)
    cls = gen_eq(cls)
    return cls
