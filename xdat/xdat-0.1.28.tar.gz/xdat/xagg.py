import numpy


class _Agg:
    def __init__(self, col_name):
        self.col_name = col_name

    def _get_func(self):
        raise NotImplemented

    def as_tuple(self):
        func = self._get_func()
        return self.col_name, func


class Count(_Agg):
    def __init__(self):
        super().__init__(None)

    def _get_func(self):
        return numpy.size


class Min(_Agg):
    def _get_func(self):
        return numpy.min


class Max(_Agg):
    def _get_func(self):
        return numpy.max


class Mean(_Agg):
    def _get_func(self):
        return numpy.mean


class Std(_Agg):
    def _get_func(self):
        return numpy.std


class Any(_Agg):
    def _get_func(self):
        return lambda x: x.values[0] if len(x) else numpy.NaN


class Lambda(_Agg):
    def __init__(self, col_name, func):
        super().__init__(col_name)
        self.func = func

    def _get_func(self):
        return self.func


