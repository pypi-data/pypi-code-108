from typing import Callable, Union


class Rate(object):

    def __init__(self, lambda_t: Union[str, Callable[[float], float]]):

        if isinstance(lambda_t, str):
            if hasattr(self, lambda_t):
                self._lambda_t: Union[str, Callable[[float], float]] = \
                    getattr(self, lambda_t)()
            else:
                raise ValueError(f'Rate class has no method {lambda_t}')
        else:
            self._lambda_t: Callable[[float], float] = lambda_t

    def __call__(self, t: float) -> float:

        return self._lambda_t(t)

    @classmethod
    def linear(cls) -> 'Rate':
        return Rate(lambda t: t)

    @classmethod
    def quadratic(cls) -> 'Rate':
        return Rate(lambda t: t ** 2)

    @classmethod
    def cubic(cls) -> 'Rate':
        return Rate(lambda t: t ** 3)
