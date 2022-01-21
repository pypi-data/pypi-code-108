from . import form_data


class CoEnum():
    @classmethod
    def to_dict(cls):
        # vars(cls) 包括内置属性
        return form_data.brief_object(cls)

    @classmethod
    def _values(cls):
        m = cls.to_dict()
        return list(m.values())

    @classmethod
    def values(cls):
        return sorted(cls._values())

    @classmethod
    def check_in(cls, value):
        name = cls.__name__.replace('Enum', '')
        vs = cls._values()
        if value not in vs:
            raise ValueError('invalid {}({}), require in {}'.format(name, value, vs))
        return value

    @classmethod
    def pick(cls, form: dict, key: str):
        m = form.get(key, None)
        return cls.check_in(m)

    @classmethod
    def __str__(cls):
        return '[{}]'.format(','.join(cls.values()))
