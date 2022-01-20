from iguanas.space import UniformFloat, UniformInteger, Choice
from hyperopt import hp


def test_uniform_float():
    uf = UniformFloat(0, 1)
    assert type(uf.transform('label')) == type(hp.uniform('label', 0, 1))


def test_uniform_integer():
    uf = UniformInteger(0, 1)
    assert type(uf.transform('label')) == type(hp.quniform('label', 0, 1, 1))


def test_choice():
    uf = Choice(['a', 'b'])
    assert type(uf.transform('label')) == type(hp.choice('label', ['a', 'b']))
