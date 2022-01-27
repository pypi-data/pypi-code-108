# -*- coding: utf-8 -*-
"""
trace
~~~~~
Module contains a trace to analyze, process, visualize time-discrete measured
signals.

:copyright: (c) 2021-2022 by Jochen Gerhaeusser.
:license: BSD, see LICENSE for details
"""
from __future__ import annotations

import math
import operator
import statistics as stats
from collections import defaultdict
from dataclasses import (
    dataclass, field, replace, fields, asdict, astuple)
from itertools import (
    accumulate, chain, islice, repeat, tee)

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats.mstats import winsorize

from ..types import *

# module exports
__all__ = [
    'Trace', 'vectorize',
    'Traces', 'as_traces',
    'Point2D',
    'Point3D',
    'Vector',
    'VectorTraces', 'polar',
    'Statistics',
    'StatisticsTraces',
    'MovingAverageTraces',
    'SetTraces', 'combine',
    'SlewRateLimiter',
    'SlewRateLimiterTraces',
    'ExponentialSmoothing',
    'ExponentialSmoothingTraces',
    'LinearRegression',
    'LinearRegressionTraces',
    'IIRFilter',
]

# Signum function
sign = np.sign


def _pairwise(trace: Union[Iterator, List, Trace]) -> Iterator[Tuple[Number, Number]]:
    """ Returns a pairwise iterator for the signal :attr:`~Trace.samples` in a
    :class:`Trace`.

    :param trace: trace to iterate
    """
    a, b = tee(trace)
    next(b, None)
    return zip(a, b)


def _clip(value: Number,
          lower: Optional[Number],
          upper: Optional[Number]) -> Number:
    """ Returns the *value* limited between the *lower* and *upper* bound.

    .. note:: The *upper* bound is dominant over the *lower* bound.

    :param value: value to clip
    :param lower: value of the lower bound or None
    :param upper: value of the upper bound or None
    """
    if lower is None and upper is None:
        # no bound
        return value
    elif upper is None:
        # lower bound
        return max(value, lower)
    elif lower is None:
        # upper bound
        return min(value, upper)
    else:
        # both bounds
        return min(upper, max(lower, value))


def _clamp(value: Number, bound: Optional[Number]) -> Number:
    """ Returns the *value* symmetrically clamped at the *bound*.

    :param value: value to clamp
    :param bound: bound to clamp at
    """
    bound = abs(bound)
    return _clip(value, -bound, bound)


def vectorize(operand: Operand) -> Samples:
    """ Returns for an :class:`int`, :class:`float`, :class:`bool` or number
    literal :class:`str` *operand* an endless iterator, otherwise the *operand*
    is returned unchanged.

    :param operand: operand to vectorize
    """
    if operand is None:
        return repeat(None)
    if isinstance(operand, (int, float, bool)):
        # create number iterator
        return repeat(operand)
    if isinstance(operand, str):
        try:
            # create number iterator from literal
            return repeat(int(operand, 0))
        except ValueError:
            raise ValueError(f"Sample literal '{operand}' is not a number.")
    return operand


@dataclass
class IIRFilter:
    """ The :class:`IIRFilter` class is a factory for a second-order recursive
    linear infinite impulse response filter, also known as *SOS-IIR filter*.

    The transfer function :math:`H(z)` with normalized filter coefficients of a
    second-order IIR filter is defined as follows:

        :math:`H(z) = \\frac{b_0 + b_1 \\cdot z^{-1} + b_2 \\cdot z^{-2}}
        {1 + a_1 \\cdot z^{-1} + a_2 \\cdot z^{-2}}`
    """
    #: Normalized feedforward filter coefficient
    b0: float
    #: Normalized feedforward filter coefficient (1st-order)
    b1: float
    #: Normalized feedforward filter coefficient (2nd-order)
    b2: float
    #: Normalized feedback filter coefficient (1st-order)
    a1: float
    #: Normalized feedback filter coefficient (2nd-order)
    a2: float
    #: Sum of the 1st-feedback stage of the SOS-IIR filter
    s1: float = 0.0
    #: Sum of the 2nd-feedback stage of the SOS-IIR filter
    s2: float = 0.0

    @classmethod
    def band_pass(cls, dt: float, f0: float,
                  q: float = 1 / math.sqrt(2)) -> IIRFilter:
        """ Creates a digital second-order IIR band-pass filter with normalized
        filter coefficients for the given sampling-time *dt*, center frequency
        *f0* and quality factor *q* of the filter.

        :param dt: sampling-time of the filter in seconds
        :param f0: center frequency of the filter in Hertz
        :param q: inverse of bandwidth factor of the filter
        """
        omega = 2 * math.pi * f0 * dt
        alpha = math.sin(omega) / (2 * q)

        # filter coefficients numerator
        b0 = alpha
        b1 = 0
        b2 = -alpha

        # filter coefficients denominator
        a0 = 1 + alpha
        a1 = -2 * math.cos(omega)
        a2 = 1 - alpha

        # second-order IIR filter with normalized filter coefficients
        return cls(b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0)

    @classmethod
    def low_pass(cls, dt: float, f0: float,
                 q: float = 1 / math.sqrt(2)) -> IIRFilter:
        """ Creates a digital second-order IIR low-pass filter with normalized
        filter coefficients for the given sampling-time *dt*, cutoff frequency
        *f0* and quality factor *q* of the filter.

        :param dt: sampling-time of the filter in seconds
        :param f0: cutoff frequency of the filter in Hertz
        :param q: inverse of bandwidth factor of the filter
        """
        omega = 2 * math.pi * f0 * dt
        alpha = math.sin(omega) / (2 * q)

        # filter coefficients numerator
        b0 = (1 - math.cos(omega)) / 2
        b1 = 1 - math.cos(omega)
        b2 = b0

        # filter coefficients denominator
        a0 = 1 + alpha
        a1 = -2 * math.cos(omega)
        a2 = 1 - alpha

        # second-order IIR filter with normalized filter coefficients
        return cls(b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0)

    @classmethod
    def high_pass(cls, dt: float, f0: float,
                  q: float = 1 / math.sqrt(2)) -> IIRFilter:
        """ Creates a digital second-order IIR high-pass filter with normalized
        filter coefficients for the given sampling-time *dt*, cutoff frequency
        *f0* and quality factor *q* of the filter.

        :param dt: sampling-time of the filter in seconds
        :param f0: cutoff frequency of the filter in Hertz
        :param q: inverse of bandwidth factor of the filter
        """
        omega = 2 * math.pi * f0 * dt
        alpha = math.sin(omega) / (2 * q)

        # filter coefficients numerator
        b0 = (1 + math.cos(omega)) / 2
        b1 = -(1 + math.cos(omega))
        b2 = b0

        # filter coefficients denominator
        a0 = 1 + alpha
        a1 = -2 * math.cos(omega)
        a2 = 1 - alpha

        # second-order IIR filter with normalized filter coefficients
        return cls(b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0)

    @classmethod
    def notch(cls, dt: float, f0: float, q: float = 1 / math.sqrt(2)) -> IIRFilter:
        """ Creates a digital second-order IIR notch filter with normalized
        filter coefficients for the given sampling-time *dt*, center frequency
        *f0* and quality factor *q* of the filter.

        :param dt: sampling-time of the filter in seconds
        :param f0: center frequency of the filter in Hertz
        :param q: inverse of bandwidth factor of the filter
        """
        omega = 2 * math.pi * f0 * dt
        alpha = math.sin(omega) / (2 * q)

        # filter coefficients numerator
        b0 = 1
        b1 = -2 * math.cos(omega)
        b2 = b0

        # filter coefficients denominator
        a0 = 1 + alpha
        a1 = -2 * math.cos(omega)
        a2 = 1 - alpha

        # second-order IIR filter with normalized filter coefficients
        return cls(b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0)

    @classmethod
    def all_pass(cls, dt: float, f0: float,
                 q: float = 1 / math.sqrt(2)) -> IIRFilter:
        """ Creates a digital second-order IIR all-pass filter with normalized
        filter coefficients for the given sampling-time *dt*, center frequency
        *f0* and quality factor *q* of the filter.

        :param dt: sampling-time of the filter in seconds
        :param f0: center frequency of the filter in Hertz
        :param q: inverse of bandwidth factor of the filter
        """
        omega = 2 * math.pi * f0 * dt
        alpha = math.sin(omega) / (2 * q)

        # filter coefficients numerator
        b0 = 1 - alpha
        b1 = -2 * math.cos(omega)
        b2 = 1 + alpha

        # filter coefficients denominator
        a0 = 1 + alpha
        a1 = -2 * math.cos(omega)
        a2 = 1 - alpha

        # second-order IIR filter with normalized filter coefficients
        return cls(b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0)

    def clear(self):
        """ Clears the sum value of the feedback stages of the SOS-IIR filter.
        """
        self.s1 = 0.0
        self.s2 = 0.0

    def compute(self, x: float) -> float:
        """ Computes for the sample :math:`x` the SOS-IIR filter equation in
        canonical form with the configured normalized filter coefficients.

        :param x: sample value to compute
        """
        # normalized canonical form
        y = self.b0 * x + self.s1
        self.s1 = (self.b1 * x - self.a1 * y) + self.s2
        self.s2 = (self.b2 * x - self.a2 * y)
        return y


@dataclass(eq=False)
class Trace:
    """ Trace data class for time-discrete, equidistant signal samples.
    """
    #: Label of the trace displayed in its plot.
    label: str = 'Trace'
    #: List of the time-discrete, equidistant signal samples of the trace.
    samples: Samples = field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.samples, list):
            # samples type conversion -> list
            self.samples = list(self.samples)
        if not isinstance(self.label, str):
            # label type conversion -> str
            self.label = str(self.label)

    @classmethod
    def from_dict(cls, key: str, data: DataFrame, **kwargs) -> Trace:
        """ Returns a new trace labeled with the *key*, and the signal
        :attr:`samples` from the value of the *data* dictionary item selected
        by the *key*.

        :param str key: key name of the signal :attr:`samples` to select from the
            data dictionary
        :param DataFrame data: dictionary with signal :attr:`samples`
        :keyword str label: optional :attr:`label` to set instead of the key name
        """
        kwargs['label'] = kwargs.get('label', key)
        kwargs['samples'] = data[key]
        return cls(**kwargs)

    def relabel(self, label: str) -> Trace:
        """ Returns the same trace relabeled with the new *label*.

        :param str label: new label to set
        """
        self.label = str(label)
        return self

    @property
    def label_stem(self) -> str:
        """ Returns the stem of the trace :attr:`label`."""
        return self.label.partition(':')[0]

    def __len__(self) -> int:
        """ Returns the number of signal :attr:`samples` in the trace."""
        return len(self.samples)

    def __getitem__(self, index: int) -> Union[List[Sample], Sample]:
        """ Returns the sample at the *index* from the trace.

        :param int index: index of the sample to get
        """
        if isinstance(index, slice):
            return self.samples[index]
        else:
            return self.samples[index]

    def __setitem__(self, index: int, value: Sample) -> None:
        """ Sets the sample at the *index* to the *value* in the trace.

        :param int index: index of the sample to set
        :param value: numerical value to set
        :type value: int, float
        """
        self.samples[index] = value

    def __contains__(self, item) -> bool:
        """ Checks if the *item* is in the signal :attr:`samples` of the trace.
        """
        return item in self.samples

    def __iter__(self):
        """ Returns an iterator over the signal :attr:`samples` in the trace."""
        return iter(self.samples)

    def __reversed__(self) -> Iterator[Union[int, bool, float, str]]:
        """ Returns a reverse iterator over the signal :attr:`samples` in the
        trace."""
        return reversed(self.samples)

    def repeat(self, times: Optional[int] = 1) -> Iterator[Sample]:
        """ Returns an iterator repeating each signal sample of the trace
        n-*times*.

        :param times: number of times to repeat a sample.
            Default is ``1``.
        """
        return chain.from_iterable((map(lambda x: repeat(x, times), self)))

    def fields(self) -> Tuple[Any, ...]:
        """ Returns a tuple describing the fields of the data class."""
        return fields(self)

    def as_dict(self) -> Dict[str, Any]:
        """ Returns the trace data class as a dictionary."""
        return asdict(self)

    def as_tuple(self) -> tuple[Any, ...]:
        """ Returns the trace data class as a tuple.
        """
        return astuple(self)

    def bool(self, **kwargs) -> Trace:
        """ Returns a new trace with the signal :attr:`samples` converted to
        booleans.

        :keyword str label: optional trace label to set
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:bool'),
                       samples=map(bool, self))

    def int(self, base: Optional[int] = None, **kwargs) -> Trace:
        """ Returns a new trace with the signal :attr:`samples` converted to
        integers.

        :keyword str label: optional trace label to set
        """
        if base is None:
            return replace(self,
                           label=kwargs.get('label', f'{self.label}:int'),
                           samples=map(int, self))
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:int'),
                       samples=map(lambda item: int(item, base), self))

    def float(self, **kwargs) -> Trace:
        """ Returns a new trace with the signal :attr:`samples` converted to
        floating-points.

        :keyword str label: optional trace label to set
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:float'),
                       samples=map(float, self))

    def bin(self, **kwargs) -> Trace:
        """ Returns a new trace with the signal :attr:`samples` converted to
        binary literals.

        :keyword str label: optional trace label to set
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:bin'),
                       samples=map(bin, self))

    def oct(self, **kwargs) -> Trace:
        """ Returns a new trace with the signal :attr:`samples` converted to
        octal literals.

        :keyword str label: optional trace label to set
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:oct'),
                       samples=map(oct, self))

    def hex(self, **kwargs) -> Trace:
        """ Returns a new trace with the signal :attr:`samples` converted to
        hexadecimal literals.

        :keyword str label: optional trace label to set
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:hex'),
                       samples=map(hex, self))

    def less(self, operand: Operand) -> Trace:
        """ Returns a new trace with the results as integers of the lesser
        comparison between the signal :attr:`samples` and the operand.

        :parameter operand: iterable or number to compare with

        .. note:: An iterable *operand* should have at least the same length as
            the trace :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        return replace(self,
                       label=f'{self.label}:lt',
                       samples=map(lambda lhs, rhs: int(lhs < rhs),
                                   self, vectorize(operand)))

    def __lt__(self, operand: Operand) -> Trace:
        return self.less(operand)

    def less_equal(self, operand: Operand) -> Trace:
        """ Returns a new trace with the results as integers of the lesser or
        equal comparison between the signal :attr:`samples` and the operand.

        :parameter operand: iterable or number to compare with

        .. note:: An iterable *operand* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        return replace(self,
                       label=f'{self.label}:le',
                       samples=map(lambda lhs, rhs: int(lhs <= rhs),
                                   self, vectorize(operand)))

    def __le__(self, operand: Operand) -> Trace:
        return self.less_equal(operand)

    def equal(self, operand: Operand) -> Trace:
        """ Returns a new trace with the results as integers of the equal
        comparison between the signal :attr:`samples` and the operand.

        :parameter operand: iterable or number to compare with

        .. note:: An iterable *operand* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        return replace(self,
                       label=f'{self.label}:eq',
                       samples=map(lambda lhs, rhs: int(lhs == rhs),
                                   self, vectorize(operand)))

    def __eq__(self, operand: Operand) -> Trace:
        return self.equal(operand)

    def not_equal(self, operand: Operand) -> Trace:
        """ Returns a new trace with the results as integers of the not equal
        comparison between the signal :attr:`samples` and the operand.

        :parameter operand: iterable or number to compare with

        .. note:: An iterable *operand* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        return replace(self, label=f'{self.label}:ne',
                       samples=map(lambda lhs, rhs: int(lhs != rhs),
                                   self, vectorize(operand)))

    def __ne__(self, operand: Operand) -> Trace:
        return self.not_equal(operand)

    def greater_equal(self, operand: Operand) -> Trace:
        """ Returns a new trace with the results as integers of the greater or
        equal comparison between the signal :attr:`samples` and the operand.

        :parameter operand: iterable or number to compare with

        .. note:: An iterable *operand* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        return replace(self,
                       label=f'{self.label}:ge',
                       samples=map(lambda lhs, rhs: int(lhs >= rhs),
                                   self, vectorize(operand)))

    def __ge__(self, operand: Operand) -> Trace:
        return self.greater_equal(operand)

    def greater(self, operand: Operand) -> Trace:
        """ Returns a new trace with the results as integers of the greater
        comparison between the signal :attr:`samples` and the operand.

        :parameter operand: iterable or number to compare with

        .. note:: An iterable *operand* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        return replace(self,
                       label=f'{self.label}:gt',
                       samples=map(lambda lhs, rhs: int(lhs > rhs),
                                   self, vectorize(operand)))

    def __gt__(self, operand: Operand) -> Trace:
        return self.greater(operand)

    def add(self, summand: Operand) -> Trace:
        """ Returns a new trace with the sums of the signal :attr:`samples`
        and the *summand*.

        :parameter summand: iterable or number

        .. note:: An iterable *summand* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        return replace(self,
                       label=f'{self.label}:add',
                       samples=map(lambda a, b: a + b,
                                   self, vectorize(summand)))

    def __add__(self, summand: Operand) -> Trace:
        return self.add(summand)

    def __radd__(self, summand: Operand) -> Trace:
        """ Returns a new trace with the sums of the *summand* and the signal
        :attr:`samples`.

        :parameter summand: iterable or number

        .. note:: An iterable *summand* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        return replace(self,
                       label=f'{self.label}:radd',
                       samples=map(lambda a, b: a + b,
                                   vectorize(summand), self))

    def sub(self, subtrahend: Operand) -> Trace:
        """ Returns a new trace with the differences between the signal
        :attr:`samples` and the *subtrahend*.

        :parameter subtrahend: iterable or number

        .. note:: An iterable *subtrahend* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        return replace(self,
                       label=f'{self.label}:sub',
                       samples=map(lambda a, b: a - b,
                                   self, vectorize(subtrahend)))

    def __sub__(self, subtrahend: Operand) -> Trace:
        return self.sub(subtrahend)

    def __rsub__(self, minuend: Operand) -> Trace:
        """ Returns a new trace with the differences between the *minuend* and
        the signal :attr:`samples`.

        :parameter minuend: iterable or number

        .. note:: An iterable *minuend* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        return replace(self,
                       label=f'{self.label}:rsub',
                       samples=map(lambda a, b: a - b,
                                   vectorize(minuend), self))

    def mul(self, factor: Operand) -> Trace:
        """ Returns a new trace with the products between the signal
        :attr:`samples` and the *factor*.

        :parameter factor: iterable or number

        .. note:: An iterable *factor* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        return replace(self,
                       label=f'{self.label}:mul',
                       samples=map(lambda a, b: a * b,
                                   self, vectorize(factor)))

    def __mul__(self, factor: Operand) -> Trace:
        return self.mul(factor)

    def __rmul__(self, factor: Operand) -> Trace:
        """ Returns a new trace with the products between the *factor* and the
        signal :attr:`samples`.

        :parameter factor: iterable or number

        .. note:: An iterable *factor* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        return replace(self,
                       label=f'{self.label}:rmul',
                       samples=map(lambda a, b: a * b,
                                   vectorize(factor), self))

    def div(self, divisor: Operand) -> Trace:
        """ Returns a new trace with the quotients between the signal
        :attr:`samples` and the *divisor*.

        :parameter divisor: iterable or number

        .. note:: An iterable *divisor* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!

        .. note:: Zero-divisions between samples are resolved by returning
            zero for the samples in the new trace where the divisor is zero!
        """
        return replace(self,
                       label=f'{self.label}:div',
                       samples=map(lambda a, b: a / b if b != 0 else 0,
                                   self, vectorize(divisor)))

    def __truediv__(self, divisor: Operand) -> Trace:
        return self.div(divisor)

    def __rtruediv__(self, dividend: Operand) -> Trace:
        """ Returns a new trace with the quotients between the *dividend* and
        the signal :attr:`samples`.

        :parameter dividend: iterable or number

        .. note:: An iterable *dividend* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!

        .. note:: Zero-divisions between samples are resolved by returning
            zero for the samples in the new trace where the divisor is zero!
        """
        return replace(self,
                       label=f'{self.label}:rdiv',
                       samples=map(lambda a, b: a / b if b != 0 else 0,
                                   vectorize(dividend), self))

    def floordiv(self, divisor: Operand) -> Trace:
        """ Returns a new trace with the integer quotients between the signal
        :attr:`samples` and the *divisor*.

        :parameter divisor: iterable or number

        .. note:: An iterable *divisor* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!

        .. note:: Zero-divisions between samples are resolved by returning
            zero for the samples in the new trace where the divisor is zero!
        """
        return replace(self,
                       label=f'{self.label}:floordiv',
                       samples=map(lambda a, b: a // b if b != 0 else 0,
                                   self, vectorize(divisor)))

    def __floordiv__(self, divisor: Operand) -> Trace:
        return self.floordiv(divisor)

    def __rfloordiv__(self, dividend: Operand) -> Trace:
        """ Returns a new trace with the integer quotients between the
        *dividend* and the signal :attr:`samples`.

        :parameter dividend: iterable or number

        .. note:: An iterable *dividend* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!

        .. note:: Zero-divisions between samples are resolved by returning
            zero for the samples in the new trace where the divisor is zero!
        """
        return replace(self,
                       label=f'{self.label}:rfloordiv',
                       samples=map(lambda a, b: a // b if b != 0 else 0,
                                   vectorize(dividend), self))

    def mod(self, divisor: Operand) -> Trace:
        """ Returns a new trace with the remainders between the signal
        :attr:`samples` and the *divisor*.

        :parameter divisor: iterable or number

        .. note:: An iterable *divisor* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!

        .. note:: Zero-divisions between samples are resolved by returning
            zero for the samples in the new trace where the divisor is zero!
        """
        return replace(self,
                       label=f'{self.label}:mod',
                       samples=map(lambda a, b: a % b if b != 0 else 0,
                                   self, vectorize(divisor)))

    def __mod__(self, divisor: Operand) -> Trace:
        return self.mod(divisor)

    def __rmod__(self, dividend: Operand) -> Trace:
        """ Returns a new trace with the remainders between the *dividend* and
        the signal :attr:`samples`.

        :parameter dividend: iterable or number

        .. note:: An iterable *dividend* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!

        .. note:: Zero-divisions between samples are resolved by returning
            zero for the samples in the new trace where the divisor is zero!
        """
        return replace(self,
                       label=f'{self.label}:rmod',
                       samples=map(lambda a, b: a % b if b != 0 else 0,
                                   vectorize(dividend), self))

    def pow(self, exponent: Operand) -> Trace:
        """ Returns a new trace with the exponentiated values for the signal
        :attr:`samples` raised to the power of the *exponent*.

        :parameter exponent: iterable or number

        .. note:: An iterable *exponent* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        return replace(self,
                       label=f'{self.label}:pow',
                       samples=map(lambda a, b: a ** b,
                                   self, vectorize(exponent)))

    def __pow__(self, exponent: Operand) -> Trace:
        return self.pow(exponent)

    def __rpow__(self, base: Operand) -> Trace:
        """ Returns a new trace with the exponentiated values for the *base*
        raised to the power of the signal :attr:`samples`.

        :parameter base: iterable or number

        .. note:: An iterable *base* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        return replace(self,
                       label=f'{self.label}:rpow',
                       samples=map(lambda a, b: a ** b,
                                   vectorize(base), self))

    def bitwise_and(self, operand: Operand) -> Trace:
        """ Returns a new trace with the bitwise ANDed values of the signal
        :attr:`samples` and the *operand*.

        :parameter operand: iterable or number

        .. note:: An iterable *operand* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        return replace(self,
                       label=f'{self.label}:and',
                       samples=map(lambda a, b: int(a) & int(b),
                                   self, vectorize(operand)))

    def __and__(self, operand: Operand) -> Trace:
        return self.bitwise_and(operand)

    def __rand__(self, operand: Operand) -> Trace:
        """ Returns a new trace with the bitwise ANDed values of the *operand*
        and the signal :attr:`samples`.

        :parameter operand: iterable or number

        .. note:: An iterable *operand* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        return replace(self,
                       label=f'{self.label}:rand',
                       samples=map(lambda a, b: int(a) & int(b),
                                   vectorize(operand), self))

    def bitwise_or(self, operand: Operand) -> Trace:
        """ Returns a new trace with the bitwise ORed values of the signal
        :attr:`samples` and the *operand*.

        :parameter operand: iterable or number

        .. note:: An iterable *operand* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        return replace(self,
                       label=f'{self.label}:or',
                       samples=map(lambda a, b: int(a) | int(b),
                                   self, vectorize(operand)))

    def __or__(self, operand: Operand) -> Trace:
        return self.bitwise_or(operand)

    def __ror__(self, operand: Operand) -> Trace:
        """ Returns a new trace with the bitwise ORed values of the *operand*
        and the signal :attr:`samples`.

        :parameter operand: iterable or number

        .. note:: An iterable *operand* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        return replace(self,
                       label=f'{self.label}:ror',
                       samples=map(lambda a, b: int(a) | int(b),
                                   vectorize(operand), self))

    def bitwise_xor(self, operand: Operand) -> Trace:
        """ Returns a new trace with the bitwise XORed values of the signal
        :attr:`samples` and the *operand*.

        :parameter operand: iterable or number

        .. note:: An iterable *operand* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        return replace(self,
                       label=f'{self.label}:xor',
                       samples=map(lambda a, b: int(a) ^ int(b),
                                   self, vectorize(operand)))

    def __xor__(self, operand: Operand) -> Trace:
        return self.bitwise_xor(operand)

    def __rxor__(self, operand: Operand) -> Trace:
        """ Returns a new trace with the bitwise XORed values of the *operand*
        and the signal :attr:`samples`.

        :parameter operand: iterable or number

        .. note:: An iterable *operand* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        return replace(self,
                       label=f'{self.label}:rxor',
                       samples=map(lambda a, b: int(a) ^ int(b),
                                   vectorize(operand), self))

    def left_shift(self, operand: Operand) -> Trace:
        """ Returns a new trace with the bitwise left-shifted signal
        :attr:`samples` by the *operand*.

        :parameter operand: iterable or number

        .. note:: An iterable *operand* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        return replace(self,
                       label=f'{self.label}:shl',
                       samples=map(lambda a, b: int(a) << int(b),
                                   self, vectorize(operand)))

    def __lshift__(self, operand: Operand) -> Trace:
        return self.left_shift(operand)

    def __rlshift__(self, operand: Operand) -> Trace:
        """ Returns a new trace with the bitwise left-shifted *operand* by the
        signal :attr:`samples`.

        :parameter operand: iterable or number

        .. note:: An iterable *operand* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        return replace(self,
                       label=f'{self.label}:rshl',
                       samples=map(lambda a, b: int(a) << int(b),
                                   vectorize(operand), self))

    def right_shift(self, operand: Operand) -> Trace:
        """ Returns a new trace with the right shifted signal :attr:`samples`
        by the *operand*.

        :parameter operand: iterable or number

        .. note:: An iterable *operand* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        return replace(self,
                       label=f'{self.label}:shr',
                       samples=map(lambda a, b: int(a) >> int(b),
                                   self, vectorize(operand)))

    def __rshift__(self, operand: Operand) -> Trace:
        return self.right_shift(operand)

    def __rrshift__(self, operand: Operand) -> Trace:
        """ Returns a new trace with the right-shifted *operand* by the signal
        :attr:`samples`.

        :parameter operand: iterable or number

        .. note:: An iterable *operand* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        return replace(self,
                       label=f'{self.label}:rshr',
                       samples=map(lambda a, b: int(a) >> int(b),
                                   vectorize(operand), self))

    def bits(self, index: int, number: int = 1, **kwargs) -> Trace:
        """ Returns a new trace with the unpacked *number* of bits starting
        at the bit *index* from the signal :attr:`samples` of the trace.

        :param int index: start index of the bits to unpack [0..31]
        :param int number: number of bits to unpack [1..32-index].
            Default is ``1``.
        :keyword str label: optional trace label to set
        """
        if index < 0 or index > 31:
            raise ValueError(f"Bit index '{index}' invalid.")
        if number < 0 or number > 32 - index:
            raise ValueError(
                f"Number of bits '{number}' to unpack at index '{index}' invalid.")
        mask = 2 ** number - 1
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:bits'),
                       samples=map(lambda x: (int(x) >> index) & mask, self))

    def __iadd__(self, operand: Operand) -> Trace:
        for i, item in enumerate(zip(self, vectorize(operand))):
            self[i] += item[1]
        self.label += ':iadd'
        return self

    def __isub__(self, operand: Operand) -> Trace:
        for i, item in enumerate(zip(self, vectorize(operand))):
            self[i] -= item[1]
        self.label += ':isub'
        return self

    def __imul__(self, operand: Operand) -> Trace:
        for i, item in enumerate(zip(self, vectorize(operand))):
            self[i] *= item[1]
        self.label += ':imul'
        return self

    def __itruediv__(self, operand: Operand) -> Trace:
        for i, item in enumerate(zip(self, vectorize(operand))):
            self[i] /= item[1] if item[1] != 0 else 0
        self.label += ':idiv'
        return self

    def __ifloordiv__(self, operand: Operand) -> Trace:
        for i, item in enumerate(zip(self, vectorize(operand))):
            self[i] //= item[1] if item[1] != 0 else 0
        self.label += ':ifloordiv'
        return self

    def __imod__(self, operand: Operand) -> Trace:
        for i, item in enumerate(zip(self, vectorize(operand))):
            self[i] %= item[1] if item[1] != 0 else 0
        self.label += ':imod'
        return self

    def __ipow__(self, operand: Operand) -> Trace:
        for i, item in enumerate(zip(self, vectorize(operand))):
            self[i] **= item[1]
        self.label += ':ipow'
        return self

    def __iand__(self, operand: Operand) -> Trace:
        for i, item in enumerate(zip(self, vectorize(operand))):
            self[i] &= item[1]
        self.label += ':iand'
        return self

    def __ior__(self, operand: Operand) -> Trace:
        for i, item in enumerate(zip(self, vectorize(operand))):
            self[i] |= item[1]
        self.label += ':ior'
        return self

    def __ixor__(self, operand: Operand) -> Trace:
        for i, item in enumerate(zip(self, vectorize(operand))):
            self[i] ^= item[1]
        self.label += ':ixor'
        return self

    def __ilshift__(self, operand: Operand) -> Trace:
        for i, item in enumerate(zip(self, vectorize(operand))):
            self[i] <<= item[1]
        self.label += ':ishl'
        return self

    def __irshift__(self, operand: Operand) -> Trace:
        for i, item in enumerate(zip(self, vectorize(operand))):
            self[i] >>= item[1]
        self.label += ':ishr'
        return self

    def neg(self, **kwargs) -> Trace:
        """ Returns a new trace with the negated values of the signal
        :attr:`samples`.

        :keyword str label: optional trace label to set
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:neg'),
                       samples=map(lambda item: -item, self))

    def __neg__(self) -> Trace:
        return self.neg()

    def __pos__(self) -> Trace:
        return self

    def abs(self) -> Trace:
        """ Returns a new trace with the absolute values of the signal
        :attr:`samples`.
        """
        return replace(self,
                       label=f'{self.label}:abs',
                       samples=map(abs, self))

    def __abs__(self) -> Trace:
        """ Returns a new trace with the absolute values of the signal
        :attr:`samples`.
        """
        return self.abs()

    def invert(self, **kwargs) -> Trace:
        """ Returns a new trace with the bitwise inverted values of the signal
        :attr:`samples`.

        :keyword str label: optional trace label to set
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:not'),
                       samples=map(lambda item: ~item, self))

    def __invert__(self) -> Trace:
        return self.invert()

    def round(self, *args, **kwargs) -> Trace:
        """ Returns a new trace with the rounded values of the signal
        :attr:`samples`.
        """
        return replace(self,
                       label=f'{self.label}:round',
                       samples=map(lambda item: round(item, *args, **kwargs), self))

    def __round__(self, *args, **kwargs) -> Trace:
        """ Returns a new trace with the rounded values of the signal
        :attr:`samples`.
        """
        return self.round(*args, **kwargs)

    def trunc(self, **kwargs) -> Trace:
        """ Returns a new trace with the truncated values of the signal
        :attr:`samples`.

        :keyword str label: optional trace label to set
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:trunc'),
                       samples=map(math.trunc, self))

    def __trunc__(self) -> Trace:
        """ Returns a new trace with the truncated values of the signal
        :attr:`samples`.
        """
        return self.trunc()

    def floor(self, **kwargs) -> Trace:
        """ Returns a new trace with the floor, rounded integers of the signal
        :attr:`samples`.

        :keyword str label: optional trace label to set
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:floor'),
                       samples=map(math.floor, self))

    def __floor__(self) -> Trace:
        return self.floor()

    def ceil(self, **kwargs) -> Trace:
        """ Returns a new trace with the ceil, rounded integers of the signal
        :attr:`samples`.

        :keyword str label: optional trace label to set
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:ceil'),
                       samples=map(math.ceil, self))

    def __ceil__(self) -> Trace:
        return self.ceil()

    def sign(self, **kwargs) -> Trace:
        """ Returns a new trace with the signum values of the signal
        :attr:`samples` of the trace.

        :keyword str label: optional trace label to set
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:sign'),
                       samples=map(sign, self))

    def zero(self, **kwargs) -> Trace:
        """ Returns a new trace with the test results as integers for testing
        the signal :attr:`samples` to be zero or not.

        :keyword str label: optional trace label to set
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:zero'),
                       samples=map(lambda x: int(sign(x) == 0), self))

    def positive(self, **kwargs) -> Trace:
        """ Returns a new trace with the test results as integers for testing
        the signal :attr:`samples` to be positive or not.

        :keyword str label: optional trace label to set
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:positive'),
                       samples=map(lambda x: int(sign(x) == 1), self))

    def negative(self, **kwargs) -> Trace:
        """ Returns a new trace with the test results as integers for testing
        the signal :attr:`samples` to be negative or not.

        :keyword str label: optional trace label to set
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:negative'),
                       samples=map(lambda x: int(sign(x) == -1), self))

    def delta(self, **kwargs) -> Trace:
        """ Returns a new trace with the deltas between the consecutive signal
        :attr:`samples`.

        :keyword str label: optional trace label to set
        :keyword float preset: optional preset value to compute the delta.
            Default is the first value in the signal samples.
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:delta'),
                       samples=map(lambda x: x[1] - x[0], _pairwise(chain(
                           [kwargs.get('preset', self[0] if self else None)],
                           self))))

    def enter_positive(self, **kwargs) -> Trace:
        """ Returns a new trace with the test results as integers for checking
        the signal :attr:`samples` starts to be positive.


        :keyword str label: optional trace label to set
        :keyword float preset: optional preset value to compute the delta.
            Default is the first value in the signal samples.
        """
        signs = self.sign()
        deltas = signs.delta(kwargs=kwargs)
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:enter_positive'),
                       samples=map(
                           lambda signum, delta: int(signum == 1 and delta > 0),
                           signs, deltas))

    def left_positive(self, **kwargs) -> Trace:
        """ Returns a new trace with the test results as integers for checking
        the signal :attr:`samples` stops to be positive.

        :keyword str label: optional trace label to set
        :keyword float preset: optional preset value to compute the delta.
            Default is the first value in the signal samples.
        """
        signs = self.sign()
        deltas = signs.delta(kwargs=kwargs)
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:left_positive'),
                       samples=map(lambda signum, delta: int(
                           (signum == 0 and delta == -1) or (
                               signum == -1 and delta == -2)),
                                   signs, deltas))

    def enter_negative(self, **kwargs) -> Trace:
        """ Returns a new trace with the test results as integers for checking
        the signal :attr:`samples` starts to be negative.

        :keyword str label: optional trace label to set
        :keyword float preset: optional preset value to compute the delta.
            Default is the first value in the signal samples.
        """
        signs = self.sign()
        deltas = signs.delta(kwargs=kwargs)
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:enter_negative'),
                       samples=map(
                           lambda signum, delta: int(signum == -1 and delta < 0),
                           signs, deltas))

    def left_negative(self, **kwargs) -> Trace:
        """ Returns a new trace with the test results as integers for checking
        the signal :attr:`samples` stops to be negative.

        :keyword str label: optional trace label to set
        :keyword float preset: optional preset value to compute the delta.
            Default is the first value in the signal samples.
        """
        signs = self.sign()
        deltas = signs.delta(kwargs=kwargs)
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:left_negative'),
                       samples=map(lambda signum, delta: int(
                           (signum == 0 and delta == 1) or (
                               signum == 1 and delta == 2)),
                                   signs, deltas))

    def accumulate(self, func=operator.add, **kwargs) -> Trace:
        """ Returns a new trace with the accumulated signal :attr:`samples`.

        :param func: function to use for the accumulation of the samples.
            Default is the ``+`` operator.
        :keyword str label: optional trace label to set
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:accumulate'),
                       samples=accumulate(self,
                                          func=func))

    def sums_positive(self, **kwargs) -> Trace:
        """ Returns a new trace with the integrated signal :attr:`samples`
        limited to positive sums.

        :keyword str label: optional trace label to set
        """
        samples = accumulate(self, lambda s, x: s + x if s + x > 0 else 0)

        if self and self[0] < 0:
            samples = list(samples)
            samples[0] = 0

        return replace(self,
                       label=kwargs.get('label', f'{self.label}:sums_positive'),
                       samples=samples)

    def sums_negative(self, **kwargs) -> Trace:
        """ Returns a new trace with the integrated signal :attr:`samples`
        limited to negative sums.

        :keyword str label: optional trace label to set
        """
        samples = accumulate(self, lambda s, x: s + x if s + x < 0 else 0)

        if self and self[0] > 0:
            samples = list(samples)
            samples[0] = 0

        return replace(self,
                       label=kwargs.get('label', f'{self.label}:sums_negative'),
                       samples=samples)

    def sin(self, **kwargs) -> Trace:
        """ Returns a new trace with the sines of the signal :attr:`samples`
        in radians.

        :keyword str label: optional trace label to set
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:sin'),
                       samples=map(math.sin, self))

    def cos(self, **kwargs) -> Trace:
        """ Returns a new trace with the cosines of the signal :attr:`samples`
        in radians.

        :keyword str label: optional trace label to set
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:cos'),
                       samples=map(math.cos, self))

    def tan(self, **kwargs) -> Trace:
        """ Returns a new trace with the tangents of the signal :attr:`samples`
        in radians.

        :keyword str label: optional trace label to set
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:tan'),
                       samples=map(math.tan, self))

    def asin(self, **kwargs) -> Trace:
        """ Returns a new trace with the arc sines of the signal
        :attr:`samples`.

        :keyword str label: optional trace label to set
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:asin'),
                       samples=map(math.asin, self))

    def acos(self, **kwargs) -> Trace:
        """ Returns a new trace with the arc cosines of the signal
        :attr:`samples`.

        :keyword str label: optional trace label to set
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:acos'),
                       samples=map(math.acos, self))

    def atan(self, **kwargs) -> Trace:
        """ Returns a new trace with the arc tangents of the signal
        :attr:`samples`.

        :keyword str label: optional trace label to set
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:atan'),
                       samples=map(math.atan, self))

    def sinh(self, **kwargs) -> Trace:
        """ Returns a new trace with the hyperbolic sines of the signal
        :attr:`samples`.

        :keyword str label: optional trace label to set
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:sinh'),
                       samples=map(math.sinh, self))

    def cosh(self, **kwargs) -> Trace:
        """ Returns a new trace with the hyperbolic cosines of the signal
        :attr:`samples`.

        :keyword str label: optional trace label to set
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:cosh'),
                       samples=map(math.cosh, self))

    def tanh(self, **kwargs) -> Trace:
        """ Returns a new trace with the hyperbolic tangents of the signal
        :attr:`samples`.

        :keyword str label: optional trace label to set
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:tanh'),
                       samples=map(math.tanh, self))

    def asinh(self, **kwargs) -> Trace:
        """ Returns a new trace with the area hyperbolic sines of the
        signal :attr:`samples`.

        :keyword str label: optional trace label to set
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:asinh'),
                       samples=map(math.asinh, self))

    def acosh(self, **kwargs) -> Trace:
        """ Returns a new trace with the area hyperbolic cosines of the
        signal :attr:`samples`.

        :keyword str label: optional trace label to set
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:acosh'),
                       samples=map(math.acosh, self))

    def atanh(self, **kwargs) -> Trace:
        """ Returns a new trace with the area hyperbolic tangents of the
        signal :attr:`samples`.

        :keyword str label: optional trace label to set
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:atanh'),
                       samples=map(math.atanh, self))

    def sort(self, *args, **kwargs) -> Trace:
        """ Returns a new trace with the sorted signal :attr:`samples` :math:`N`
        in ascending order.
        """
        return replace(self,
                       label=f'{self.label}:sort',
                       samples=sorted(self, *args, **kwargs))

    def winsorize(self,
                  limits: Optional[
                      Union[float,
                            tuple[Optional[float], Optional[float]]]] = None,
                  **kwargs):
        """ Returns a new trace with the winsorized signal :attr:`samples`
        :math:`N`.

        The nth-lowest sample values are set to the ``limits[0]``-th percentile
        sample value, and the nth-highest sample values are set to the
        ``(1.0 - limits[1])``-th percentile sample value.

        :param limits: either a pair of the percentages as floats between
            ``0.0`` and ``1.0`` to cut on each side of the sorted signal
            samples in ascending order, or the percentage for both sides.

            The value of one limit can be set to ``None`` to indicate an open
            interval for this side.
        :keyword str label: optional trace label to set
        """
        if not self or limits is None:
            return self
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:winsorize'),
                       samples=winsorize(self, limits).data)

    def index_of(self, sample: Sample) -> int:
        """ Returns the *index* of the first occurrence of the *sample* :math:`x`
        in the signal :attr:`samples` :math:`N` or ``-1`` if no sample could be
        found.

        :param sample: sample value to look for
        """
        try:
            return operator.indexOf(self, sample)
        except ValueError:
            return -1

    def count(self, sample: Sample) -> int:
        """ Returns the *number* of occurrences of the *sample* :math:`x` in the
        signal :attr:`samples` :math:`N`.

        :param sample: sample value to count
        """
        return operator.countOf(self, sample)

    def sum(self, *operands, **kwargs) -> Union[Trace, float]:
        """ Returns either a new trace with the sums of the signal :attr:`samples`
        and the provided *operands*, or the sum :math:`\\sum\\limits_{i=0}^{N}{x_i}`
        of the signal :attr:`samples` :math:`N` of the trace in case no *operands*
        are provided.

        An *operand* can be either a fix number or an array-like iterable.

        :parameter operands: operands to sum up with each signal sample
        :keyword str label: optional trace label to set

        .. note:: An iterable *operand* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        if not operands:
            return sum(self)
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:sum'),
                       samples=map(lambda t: sum(t),
                                   zip(self, *map(vectorize, operands))))

    def min(self, *operands: Tuple[Operand], **kwargs) -> Union[Trace, Sample]:
        """ Returns either a new trace with the minimums of the signal
        :attr:`samples` and the provided *operands*, or the minimum :math:`x_{min}`
        in the signal :attr:`samples` :math:`N` of the trace in case no *operands*
        are provided.

        An *operand* can be either a fix number or an array-like iterable.

        :parameter operands: operands to compare with each signal sample
        :keyword str label: optional trace label to set

        .. note:: An iterable *operand* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        if not operands:
            return min(self)
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:min'),
                       samples=map(lambda t: min(t),
                                   zip(self, *map(vectorize, operands))))

    def max(self, *operands: Tuple[Operand], **kwargs) -> Union[Trace, Sample]:
        """ Returns either a new trace with the maximus of the signal
        :attr:`samples` and the provided *operands*, or the maximum :math:`x_{max}`
        in the signal :attr:`samples` :math:`N` of the trace in case no *operands*
        are provided.

        An *operand* can be either a fix number or an array-like iterable.

        :parameter operands: operands to compare with each signal sample
        :keyword str label: optional trace label to set

        .. note:: An iterable *operand* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        if not operands:
            return max(self)
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:max'),
                       samples=map(lambda t: max(t),
                                   zip(self, *map(vectorize, operands))))

    def range(self) -> Union[float, int]:
        """ Returns the *range* :math:`x_{max} - x_{min}` of the signal
        :attr:`samples` :math:`N`."""
        return max(self) - min(self)

    def midrange(self) -> Union[float, int]:
        """ Returns the *midrange* :math:`\\frac{x_{max} + x_{min}}{2}` of the
        signal :attr:`samples` :math:`N`."""
        return (max(self) + min(self)) / 2

    def average(self, *operands, **kwargs) -> Union[Trace, float]:
        """ Returns either a new trace with the averages of the signal
        :attr:`samples` and the provided *operands*, or the average
        :math:`\\overline{x}` of the signal :attr:`samples` :math:`N` of the
        trace in case no *operands* are provided.

        An *operand* can be either a fix number or an array-like iterable.

        :parameter operands: operands to compute with each signal sample
        :keyword str label: optional trace label to set

        .. note:: An iterable *operand* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        if not operands:
            return sum(self) / len(self) if self else 0.0
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:avg'),
                       samples=map(lambda t: sum(t) / len(t),
                                   zip(self, *map(vectorize, operands))))

    def mean(self) -> Union[float, int]:
        """ Returns the arithmetic *mean* :math:`\\overline{x}` of the signal
        :attr:`samples` :math:`N`."""
        return stats.mean(self) if self else 0.0

    def weighted_mean(self) -> Union[float, int]:
        """ Returns the linear weighted arithmetic *mean*
        :math:`\\overline{x}_{w}` of the signal :attr:`samples` :math:`N`."""
        n = len(self)
        if not n:
            return 0.0
        if n < 2:
            return self[0]
        return (2 / (n * (n + 1))) * sum([w * x for w, x in enumerate(self, 1)])

    def winsor_mean(self,
                    limits: Optional[
                        Union[float,
                              tuple[Optional[float], Optional[float]]]] = None
                    ) -> Union[float, int]:
        """ Returns the winsorized arithmetic *mean* :math:`\\overline{x}_{w\\alpha}`
        of the signal :attr:`samples` :math:`N`.

        :param limits: either a pair of the percentages as floats between
            ``0.0`` and ``1.0`` to cut on each side of the sorted signal
            samples in ascending order, or the percentage for both sides.

            The value of one limit can be set to ``None`` to indicate an open
            interval for this side.
        """
        samples = self.winsorize(limits)
        return stats.mean(samples) if samples else 0.0

    def median(self) -> Union[float, int]:
        """ Returns the median :math:`\\overline{x}_{med}` of the signal
        :attr:`samples` :math:`N`."""
        return stats.median(self) if self else 0.0

    def mode(self) -> Union[float, int]:
        """ Returns the mode :math:`\\overline{x}_{mod}` of the signal
        :attr:`samples` :math:`N`."""
        return stats.mode(self) if self else 0.0

    def rms(self) -> float:
        """ Returns the *root-mean-square* :math:`x_{rms}` of the signal
        :attr:`samples` :math:`N`."""
        return math.sqrt(sum(self ** 2) / len(self)) if self else 0.0

    def aad(self) -> float:
        """ Returns the *average absolute deviation* :math:`D_{mean}` of the
        signal :attr:`samples` :math:`N`."""
        if self:
            center = self.mean()
            return sum(map(lambda x: abs(x - center), self)) / len(self)
        else:
            return 0.0

    def mad(self) -> float:
        """ Returns the *median absolute deviation* :math:`D_{median}` of the
        signal :attr:`samples` :math:`N`."""
        if self:
            center = self.median()
            return sum(map(lambda x: abs(x - center), self)) / len(self)
        else:
            return 0.0

    def variance(self, **kwargs) -> float:
        """ Returns the biased sample *variance* :math:`\sigma^2` of the signal
        :attr:`samples` :math:`N`.

        :keyword center: optional center value.
            Default is the arithmetic :attr:`mean` of the signal :attr:`samples`.
        :keyword bool unbiased: optional if ``True`` computes the unbiased
            *variance* :math:`\sigma^2`. Default is ``False``.
        """
        center = kwargs.get('center', self.mean())
        count = len(self)

        if count < 2:
            return 0.0
        if kwargs.get('unbiased', False):
            count -= 1
        return sum(map(lambda x: (x - center) ** 2, self)) / count

    def std(self, **kwargs) -> float:
        """ Returns the biased sample *standard deviation* :math:`\sigma` of the
        signal :attr:`samples` :math:`N`.

        :keyword center: optional center value.
            Default is the arithmetic :attr:`mean` of the signal :attr:`samples`.
        :keyword bool unbiased: optional if ``True`` computes the unbiased
            *standard deviation* :math:`\sigma`. Default is ``False``.
        """
        return math.sqrt(self.variance(**kwargs))

    def coefficient(self, **kwargs) -> float:
        """ Returns the *coefficient of variation* :math:`c_v` of the signal
        :attr:`samples` :math:`N`.

        :keyword center: optional center value.
            Default is the arithmetic :attr:`mean` of the signal :attr:`samples`.
        :keyword std: optional standard deviation.
            Default is the biased standard deviation :attr:`std` of the signal
            :attr:`samples`.
        :keyword bool unbiased: optional if ``True`` uses the unbiased
            *standard deviation* :math:`\sigma`. Default is ``False``.
        """
        center = kwargs.get('center', self.mean())
        std = kwargs.get('std', self.std(**kwargs))
        return std / center if center else 0.0

    def skew(self, **kwargs) -> float:
        """ Returns the biased sample *skew* of the signal :attr:`samples`
        :math:`N`.

        :keyword center: optional center value.
            Default is the arithmetic :attr:`mean` of the signal :attr:`samples`.
        :keyword std: optional standard deviation.
            Default is the biased standard deviation :attr:`std` of the signal
            :attr:`samples`.
        :keyword bool unbiased: optional if ``True`` uses the unbiased
            *standard deviation* :math:`\sigma`. Default is ``False``.
        """
        center = kwargs.get('center', self.mean())
        std = kwargs.get('std', self.std(**kwargs))
        count = len(self)
        if count < 2 or not std:
            return 0.0
        return sum(map(lambda x: ((x - center) / std) ** 3, self)) / count

    def kurtosis(self, **kwargs) -> float:
        """ Returns the biased sample *kurtosis* of the signal :attr:`samples`
        :math:`N`.

        :keyword center: optional center value.
            Default is the arithmetic :attr:`mean` of the signal :attr:`samples`.
        :keyword std: optional standard deviation.
            Default is the biased standard deviation :attr:`std` of the signal
            :attr:`samples`.
        :keyword bool unbiased: optional if ``True`` uses the unbiased
            *standard deviation* :math:`\sigma`. Default is ``False``.
        """
        center = kwargs.get('center', self.mean())
        std = kwargs.get('std', self.std(**kwargs))
        count = len(self)
        if count < 2 or not std:
            return 0.0
        return sum(map(lambda x: ((x - center) / std) ** 4, self)) / count

    def zscore(self, **kwargs) -> Trace:
        """ Returns a new trace with the biased z-scored signal :attr:`samples`
        :math:`N`.

        :keyword center: optional center value.
            Default is the arithmetic :attr:`mean` of the signal :attr:`samples`.
        :keyword std: optional biased standard deviation.
            Default is the biased standard deviation :attr:`std` of the signal
            :attr:`samples`.
        :keyword str label: optional trace label to set
        """
        center = kwargs.get('center', self.mean())
        std = kwargs.get('std', self.std(**kwargs))
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:zscore'),
                       samples=map(lambda x: ((x - center) / std) if std else 0.0,
                                   self))

    def clip(self,
             lower: Optional[Operand] = None,
             upper: Optional[Operand] = None, **kwargs) -> Trace:
        """ Returns either a new trace with the signal :attr:`samples` limited
        between the provided *lower* and *upper* bound, or the same trace in case
        no bounds are provided.

        A *bound* can be either a fix number or an array-like iterable.

        :param Operand lower: optional lower bound to clip at.
            Default is ``None``, this means the bound is not considered.
        :param Operand upper: optional upper bound to clip at.
            Default is ``None``, this means the bound is not considered.
        :keyword str label: optional trace label to set

        .. note:: The *upper* bound is dominant over the *lower* bound.

        .. note:: An iterable *bound* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        if lower is None and upper is None:
            return self
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:clip'),
                       samples=map(_clip,
                                   self, *map(vectorize, (lower, upper))))

    def clamp(self, bound: Optional[Operand] = None, **kwargs) -> Trace:
        """ Returns either a new trace with the signal :attr:`samples` symmetrically
        clamped at the provided *bound*, or the same trace in case no bound is
        provided.

        A *bound* can be either a fix number or an array-like iterable.

        :param Operand bound: optional bound to clamp at.
            Default is ``None``, this means the bound is not considered.
        :keyword str label: optional trace label to set

        .. note:: An iterable *bound* should have at least the same length
            as the signal :attr:`samples`, otherwise only a subset of the signal
            :attr:`samples` is returned!
        """
        if bound is None:
            return self
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:clamp'),
                       samples=map(_clamp, self, vectorize(bound)))

    def ramp(self,
             limits: Optional[tuple[Optional[Operand], Optional[Operand]]] = None,
             **kwargs) -> Trace:
        """ Returns either a new trace with the signal :attr:`samples` limited
        by the maximal allowed positive and/or negative delta *limits* between
        consecutive :attr:`samples`, or the same trace in case no *limits* are
        provided.

        The maximal allowed *positive* delta limit can be either a fix number
        or an array-like iterable.

        The maximal allowed *negative* delta limit can be either a fix number
        or an array-like iterable.

        :param limits: optional a pair with the maximal allowed positive and
            negative deltas between consecutive samples.

            The value of one limit can be set to ``None`` to indicate an
            unlimited ramp for this side.
        :keyword str label: optional trace label to set
        :keyword float preset: optional preset value of the ramp.
            Default is the first value in the signal samples.

        .. note:: An iterable maximal allowed *positive* or *negative* step
            should have at least the same length as the signal :attr:`samples`,
            otherwise only a subset of the signal :attr:`samples` is returned!
        """
        if not limits:
            return replace(self,
                           label=f'{self.label}',
                           samples=self[:])

        level = kwargs.get('preset', self[0] if self else 0)
        samples = list()
        for values in zip(self, vectorize(limits[0]), vectorize(limits[1])):
            sample, delta_positive, delta_negative = values

            if delta_positive is not None:
                delta_positive = max(delta_positive, 0)

            if delta_negative is not None:
                delta_negative = min(delta_negative, 0)

            delta = sample - level

            if delta_positive is not None and delta > delta_positive:
                level += delta_positive
            elif delta_negative is not None and delta < delta_negative:
                level += delta_negative
            else:
                level = sample
            samples.append(level)

        return replace(self,
                       label=kwargs.get('label', f'{self.label}:ramp'),
                       samples=samples)

    def slew(self,
             limits: Optional[tuple[Optional[Operand], Optional[Operand]]],
             hold: Optional[Operand] = None,
             **kwargs) -> SlewRateLimiterTraces:
        """ Slew-rate limiter over the signal :attr:`samples` of the trace.

        The maximal allowed *positive* delta limit can be either a fix number
        or an array-like iterable.

        The maximal allowed *negative* delta limit can be either a fix number
        or an array-like iterable.

        The number of samples to hold the previous sample value when the one of
        the configured slew-rates becomes violated can be either a fix number
        or an array-like iterable.

        :param limits: a pair with the maximal allowed positive and negative
            deltas between consecutive samples.

            The value of one limit can be set to ``None`` to indicate an
            unlimited ramp for this side.
        :param Operand hold: optional number of samples to hold the previous
            sample value when one of the configured slew-rates becomes violated.
        :keyword float preset: optional preset value of the limiter.
            Default is the first value in the signal samples.
        :keyword str label: optional trace label to set
        """
        level = kwargs.get('preset', self[0] if self else 0)
        counter = 0

        samples = list()
        for values in zip(self,
                          vectorize(limits[0]),
                          vectorize(limits[1]),
                          vectorize(hold)):
            sample, delta_positive, delta_negative, count = values

            if delta_positive is not None:
                delta_positive = max(delta_positive, 0)

            if delta_negative is not None:
                delta_negative = min(delta_negative, 0)

            count = 0 if count is None else max(count, 0)

            delta = sample - level

            if delta_positive is not None and delta > delta_positive:
                if counter >= count:
                    level += delta_positive
                else:
                    counter += 1
                active = 1
            elif delta_negative is not None and delta < delta_negative:
                if counter >= count:
                    level += delta_negative
                else:
                    counter += 1
                active = 1
            else:
                level = sample
                active = 0
                counter = 0

            results = SlewRateLimiter(
                level=level,
                deviation=sample - level if active else 0,
                active=active)

            samples.append(asdict(results))

        traces = dict()
        label = kwargs.get('label', f'{self.label}:slew')
        for key, value in as_traces(samples).items():
            traces[key] = replace(self,
                                  label=f'{label}:{key}',
                                  samples=value)
        return SlewRateLimiterTraces(**traces)

    def band_pass(self, dt: float, f0: float, q: float = 1 / math.sqrt(2),
                  **kwargs) -> Trace:
        """ Returns a new trace with the signal :attr:`samples` filtered with a
        second-order IIR band-pass filter.

        :param dt: sampling-time of the :attr:`~Trace.samples` (filter) in seconds
        :param f0: center frequency of the filter in Hertz
        :param q: inverse of bandwidth factor of the filter
        :keyword str label: optional trace label to set
        """
        _filter = IIRFilter.band_pass(dt, f0, q)
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:band-pass'),
                       samples=map(_filter.compute, self))

    def low_pass(self, dt: float, f0: float, q: float = 1 / math.sqrt(2),
                 **kwargs) -> Trace:
        """ Returns a new trace with the signal :attr:`samples` filtered with a
        second-order IIR low-pass filter.

        :param dt: sampling-time of the :attr:`~Trace.samples` (filter) in seconds
        :param f0: cutoff frequency of the filter in Hertz
        :param q: inverse of bandwidth factor of the filter
        :keyword str label: optional trace label to set
        """
        _filter = IIRFilter.low_pass(dt, f0, q)
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:low-pass'),
                       samples=map(_filter.compute, self))

    def high_pass(self, dt: float, f0: float, q: float = 1 / math.sqrt(2),
                  **kwargs) -> Trace:
        """ Returns a new trace with the signal :attr:`samples` filtered with a
        second-order IIR high-pass filter.

        :param dt: sampling-time of the :attr:`~Trace.samples` (filter) in seconds
        :param f0: cutoff frequency of the filter in Hertz
        :param q: inverse of bandwidth factor of the filter
        :keyword str label: optional trace label to set
        """
        _filter = IIRFilter.high_pass(dt, f0, q)
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:high-pass'),
                       samples=map(_filter.compute, self))

    def notch(self, dt: float, f0: float, q: float = 1 / math.sqrt(2),
              **kwargs) -> Trace:
        """ Returns a new trace with the signal :attr:`samples` filtered with a
        second-order IIR notch filter.

        :param dt: sampling-time of the :attr:`~Trace.samples` (filter) in seconds
        :param f0: center frequency of the filter in Hertz
        :param q: inverse of bandwidth factor of the filter
        :keyword str label: optional trace label to set
        """
        _filter = IIRFilter.notch(dt, f0, q)
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:notch'),
                       samples=map(_filter.compute, self))

    def all_pass(self, dt: float, f0: float, q: float = 1 / math.sqrt(2),
                 **kwargs) -> Trace:
        """ Returns a new trace with the signal :attr:`samples` filtered with a
        second-order IIR all-pass filter.

        :param dt: sampling-time of the :attr:`~Trace.samples` (filter) in seconds
        :param f0: center frequency of the filter in Hertz
        :param q: inverse of bandwidth factor of the filter
        :keyword str label: optional trace label to set
        """
        _filter = IIRFilter.all_pass(dt, f0, q)
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:all-pass'),
                       samples=map(_filter.compute, self))

    @staticmethod
    def _damping_factor(ratio: Union[int, float]) -> float:
        if isinstance(ratio, int):
            factor = 1.0 - (1 / ratio) if ratio > 1 else 0.0
        else:
            factor = _clip(1.0 - ratio, 0.0, 1.0)
        return factor

    def dt1(self,
            ratio: Operand,
            gain: Operand = 1,
            **kwargs) -> Trace:
        """ Returns a new trace with the signal :attr:`samples` of the trace
        processed by the transfer function of a DT1-element.

        :param ratio: integer ratios between damping time and sampling time,
            or floating-point ratios between sampling time and damping time.
        :type ratio: int, float
        :param Operand gain: proportional gain of the DT1-element.
        :keyword float preset: optional preset value of the DT1-element.
            Default is the first value in the signal samples.
        :keyword str label: optional trace label to set
        """
        y = kwargs.get('preset', self[0] if self else 0.0)
        previous = self[0] if self else 0.0
        samples = list()
        for value, factor, p in zip(self.samples,
                                    map(self._damping_factor,
                                        vectorize(ratio)),
                                    vectorize(gain)):
            y = y * factor + (value - previous)
            previous = value
            samples.append(p * y)

        return replace(self,
                       label=kwargs.get('label', f'{self.label}:dt1'),
                       samples=samples)

    @staticmethod
    def _smoothing_factor(ratio: Union[int, float]) -> float:
        if isinstance(ratio, int):
            factor = 1.0 / ratio if ratio > 1 else 1.0
        else:
            factor = _clip(ratio, 0.0, 1.0)
        return factor

    def pt1(self,
            ratio: Operand,
            gain: Operand = 1,
            **kwargs) -> Trace:
        """ Returns a new trace with the signal :attr:`samples` of the
        trace processed by the transfer function of a PT1-element.

        :param ratio: integer ratio between smoothing time and sampling time,
            or floating-point ratio between sampling time and smoothing time.
        :type ratio: Operand
        :param Operand gain: proportional gain of the PT1-element.
        :keyword float preset: optional preset value of the PT1-element.
            Default is the first value in the signal samples.
        :keyword str label: optional trace label to set
        """
        y = kwargs.get('preset', self[0] if self else 0.0)
        samples = list()
        for value, factor, p in zip(self.samples,
                                    map(self._smoothing_factor,
                                        vectorize(ratio)),
                                    vectorize(gain)):
            y += (value - y) * factor
            samples.append(p * y)

        return replace(self,
                       label=kwargs.get('label', f'{self.label}:pt1'),
                       samples=samples)

    def exponential(self, alpha: float, **kwargs) -> ExponentialSmoothingTraces:
        """ Second-order exponential smoothing over the signal
        :attr:`samples` of the trace.

        :param float alpha: smoothing factor ``[0.0:freeze..1.0:transparent]``
        :keyword float level: optional initial level of the exponential smoothing.
            Default is the first value in the signal samples.
        :keyword float trend: optional initial trend of the exponential smoothing.
            Default is ``0.0``.
        :keyword str label: optional trace label to set
        """
        # initialize exponential smoothing
        level = kwargs.get('level', self.samples[0])
        trend = kwargs.get('trend', 0.0)
        alpha = _clip(alpha, 0.0, 1.0)
        prognosis = [
            (level - ((1 - alpha) / alpha) * trend if alpha > 0 else 0),
            (level - 2 * ((1 - alpha) / alpha) * trend if alpha > 0 else 0)
        ]

        # initialize signal statistic
        absolute = 0.0
        variance = 0.0
        skew = 0.0
        kurtosis = 0.0
        samples = list()
        for value in self.samples:
            # prognosis error
            error = value - ((2 * prognosis[0] - prognosis[1]) + trend)
            # empirical absolute error of the distribution (1st central moment)
            absolute_error = (1 - alpha) * (absolute + alpha * abs(error))
            # empirical variance of the distribution (2nd central moment)
            variance = (1 - alpha) * (variance + alpha * (error ** 2))
            # empirical standard deviation of the distribution
            deviation = math.sqrt(variance)
            # empirical skew of the distribution (3rd central moment)
            skew = (1.0 - alpha) * (skew + alpha * (
                (error / deviation) ** 3 if deviation != 0.0 else 0.0))
            # empirical kurtosis of the distribution (4th central moment)
            kurtosis = (1.0 - alpha) * (kurtosis + alpha * (
                (error / deviation) ** 4 if deviation != 0.0 else 0.0))
            # first-order exponentially smoothed value
            smoothed1 = (1.0 - alpha) * prognosis[0] + alpha * value
            # second-order exponentially smoothed value
            smoothed2 = (1.0 - alpha) * prognosis[1] + alpha * smoothed1
            # prognosis level (exponentially smoothed signal value)
            level = 2 * smoothed1 - smoothed2
            # prognosis trend
            trend = (alpha / (1 - alpha)) * (
                smoothed1 - smoothed2) if alpha < 1 else 0
            # prognosis forecast
            forecast = level + trend
            # results of the 2nd-order exponential smoothing
            results = ExponentialSmoothing(
                forecast=forecast,
                forecast_sign=sign(forecast),
                level=level,
                level_sign=sign(level),
                prognosis1=prognosis[0],
                prognosis2=prognosis[1],
                prognosis=2 * prognosis[0] - prognosis[1],
                smoothed1=smoothed1,
                smoothed2=smoothed2,
                trend=trend,
                trend_sign=sign(trend),
                trend_inflection=sign(forecast - level),
                error=error,
                correction=alpha * error,
                absolute_error=absolute_error,
                variance=variance,
                deviation=deviation,
                skew=skew,
                kurtosis=kurtosis)
            # new prognosis values
            prognosis = [smoothed1, smoothed2]
            samples.append(asdict(results))

        traces = dict()
        label = kwargs.get('label', f'{self.label}:exponential')
        for key, value in as_traces(samples).items():
            traces[key] = replace(self,
                                  label=f'{label}:{key}',
                                  samples=value)
        return ExponentialSmoothingTraces(**traces)

    def window(self, size: int, **kwargs) -> Iterator[Tuple[Sample, ...]]:
        """ Moving window generator over the signal :attr:`samples` of the trace.

        :param int size: moving window size (number of samples)
        :keyword float preset: optional preset value to fill the moving window.
            Default is the first value in the signal samples.
        """
        if not self or size <= 0:
            yield from self.samples
        else:
            # moving windows iterator
            windows = tee(
                chain(repeat(kwargs.get('preset', self[0]), size - 1),
                      iter(self)), size)
            yield from zip(
                *(islice(window, i, None) for i, window in enumerate(windows)))

    def moving_average(self, size: int, **kwargs) -> MovingAverageTraces:
        """ Moving average over the signal :attr:`samples` of the trace.

        :param int size: moving window size (number of samples)
        :keyword float preset: optional preset value to fill the moving window.
            Default is the first value in the signal samples.
        """
        samples = list()
        for values in self.window(size, **kwargs):
            trace = Trace(samples=values)
            mean = trace.mean()
            minimum = trace.min()
            maximum = trace.max()
            deviation = trace.std(center=mean)
            result = Statistics(
                mean=mean,
                weighted_mean=trace.weighted_mean(),
                median=trace.median(),
                mode=trace.mode(),
                rms=trace.rms(),
                minimum=trace.min(),
                maximum=trace.max(),
                range=maximum - minimum,
                midrange=trace.midrange(),
                absolute_error=sum(abs(trace - mean)),
                variance=trace.variance(center=mean),
                deviation=trace.std(center=mean),
                coefficient=trace.coefficient(center=mean, std=deviation),
                skew=trace.skew(center=mean, std=deviation),
                kurtosis=trace.kurtosis(center=mean, std=deviation)
            )
            samples.append(asdict(result))
        traces = dict()
        label = kwargs.get('label', f'{self.label}:average')
        for key, value in as_traces(samples).items():
            traces[key] = Trace(label=f'{label}:{key}',
                                samples=value)
        return MovingAverageTraces(**traces)

    def moving_differential(self, size: int, **kwargs) -> Trace:
        """ Moving differential over the signal :attr:`samples` of the trace.

        :param int size: moving window size (number of samples)
        :keyword float preset: optional preset value to fill the moving window.
            Default is the first value in the signal samples.
        :keyword str label: optional trace label to set
        """
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:differential'),
                       samples=[((y[-1] - y[0]) / (size - 1)) if
                                size > 1 else 0 for y in
                                self.window(size, **kwargs)])

    def moving_regression(self, size: int, **kwargs) -> LinearRegressionTraces:
        """ Moving linear regression over the signal :attr:`samples` of the
        trace.

        :param int size: moving window size
        :keyword float preset: optional preset value to fill the moving window.
            Default is the first value in the signal samples.
        :keyword str label: optional trace label to set
        """
        samples = list()
        # x-coordinate values
        x_values = list(range(size))
        for y_values in self.window(size, **kwargs):
            # arithmetic mean of the x-coordinate values
            mean_x = stats.mean(x_values)
            # arithmetic mean of the y-coordinate values (1st central moment)
            mean_y = stats.mean(y_values)
            # median of the y-coordinate values
            median_y = stats.median(y_values)
            # residuals of the x-coordinate values
            residuals_x = list(map(lambda x: x - mean_x,
                                   x_values))
            # residuals of the y-coordinate values
            residuals_y = list(map(lambda y: y - mean_y,
                                   y_values))
            # sum of the squared x-coordinate residuals
            dxdx_sum = sum(map(lambda x: x ** 2,
                               residuals_x))
            # sum of the xy-coordinate residual products
            dxdy_sum = sum(map(lambda p: p[0] * p[1],
                               zip(residuals_x, residuals_y)))
            # slope of the approximated line
            slope = dxdy_sum / dxdx_sum
            # y-intercept of the approximated line
            intercept = mean_y - slope * mean_x
            # current y-coordinate of the approximated line
            level = slope * x_values[-1] + intercept
            # minimum of the y-coordinate values
            minimum = min(y_values)
            # maximum of the y-coordinate values
            maximum = max(y_values)
            # deviations of the y-coordinates from the approximated line
            errors = list(
                map(lambda point: point[1] - (slope * point[0] + intercept),
                    enumerate(y_values)))
            # maximal positive y-coordinate deviation from the approximated line
            positive_error = max(errors)
            # maximal negative y-coordinate deviation from the approximated line
            negative_error = min(errors)
            # empirical absolute error of the distribution (1st central moment)
            absolute_error = sum(map(abs, errors))
            # empirical variance of the distribution (2nd central moment)
            variance = sum(map(lambda e: e ** 2, errors))
            # empirical standard deviation of the distribution
            deviation = math.sqrt(variance)
            # empirical skew of the distribution (3rd central moment)
            skew = sum(
                map(lambda e: (e / deviation) ** 3 if deviation != 0.0 else 0.0,
                    errors))
            # empirical kurtosis of the distribution (4th central moment)
            kurtosis = sum(
                map(lambda e: (e / deviation) ** 4 if deviation != 0.0 else 0.0,
                    errors))
            # results of the linear regression
            results = LinearRegression(
                level=level,
                slope=slope,
                intercept=intercept,
                mean=mean_y,
                median=median_y,
                error=errors[-1],
                minimum=minimum,
                maximum=maximum,
                range=maximum - minimum,
                negative_error=negative_error,
                positive_error=positive_error,
                absolute_error=absolute_error,
                variance=variance,
                deviation=deviation,
                skew=skew,
                kurtosis=kurtosis)
            samples.append(asdict(results))

        traces = dict()
        label = kwargs.get('label', f'{self.label}:regression')
        for key, value in as_traces(samples).items():
            traces[key] = replace(self,
                                  label=f'{label}:{key}',
                                  samples=value)
        return LinearRegressionTraces(**traces)

    def move(self, number: int, **kwargs) -> Trace:
        """ Returns a new trace with the moved signal :attr:`samples` by the
        number of samples either to the right or to the left.

        A positive *number* moves the signal :attr:`samples` to the right. This
        means a *number* of the first value in signal :attr:`samples` is inserted
        at the beginning of the signal :attr:`samples` to move as the *fill*
        value, and the *number* of the last signal :attr:`samples` are removed
        from the signal :attr:`samples` to move.

        A negative *number* moves the signal :attr:`samples` to the left. This
        means a *number* of the last value in the signal :attr:`samples` is
        appended at end of the signal :attr:`samples` to move as the *fill*
        value, and the *number* of the first signal :attr:`samples` are removed
        from the signal :attr:`samples` to move.

        :param int number: number of samples to move to the right (``> 0``) or
            to the left (``< 0``).
        :keyword str label: optional trace label to set
        :keyword float fill: optional fill value.
            Default is the first or last value in the signal samples.
        """
        # copy samples
        samples = self[:]
        if not samples or not number:
            # nothing to move
            pass
        elif number > 0:
            # move to right
            number = min(number, len(samples))
            fill = kwargs.get('fill', self[0])
            samples = [fill] * number + samples[:-number]
        elif number < 0:
            # move to left
            number = min(-number, len(samples))
            fill = kwargs.get('fill', self[-1])
            samples = samples[number:] + [fill] * number

        return replace(self,
                       label=kwargs.get('label', f'{self.label}:move'),
                       samples=samples)

    def slice(self, *args, **kwargs) -> Trace:
        """ Returns a new trace with the signal :attr:`samples` sliced with the
        built-in function :func:`slice` in the range given by the arguments
        *args*.

        :param args: optional *start*, *stop* index and *step* for slicing the
            signal :attr:`samples`.
        :keyword str label: optional trace label to set
        """
        if not args:
            samples = self.samples[:]
        else:
            samples = self.samples[slice(*args)]
        return replace(self,
                       label=kwargs.get('label', f'{self.label}:slice'),
                       samples=samples if samples else list())

    def iter_x(self) -> Iterator[int]:
        """ Returns an iterator for the x-coordinates of the trace.
        """
        return range(len(self))

    def iter_point(self) -> Iterator[Point2D]:
        """ Returns an iterator for the x,y-points of the trace.
        """
        for x, y in zip(self.iter_x(), self):
            yield Point2D(x, y)

    @property
    def x_values(self) -> List[int]:
        """ Returns a list with the x-coordinates of the trace.
        """
        return list(self.iter_x())

    @property
    def y_values(self) -> List(Sample):
        """ Returns a list with the y-coordinates of the trace.
        """
        return list(self)

    @property
    def digital(self) -> Digital:
        """ Returns a new digital trace with *shared* signal :attr:`samples`.
        """
        return Digital(**asdict(self))

    def plot(self,
             index: Optional[int] = None,
             n: Optional[int] = None,
             **kwargs) -> go.Scatter:
        """ Returns the scatter plot of the trace.

        :param int index: start index of the samples to plot
        :param n: number of samples to plot
        """
        # pack x,y-pairs
        pairs = list(zip(self.iter_x(), self))
        if pairs:
            # slice pairs
            index = 0 if index is None else max(0, index)
            if n is None:
                pairs = pairs[index:]
            elif n <= 0:
                pairs = pairs[index:index + 1]
            else:
                pairs = pairs[index:index + n]

            # unpack x,y-pairs
            x, y = zip(*pairs)
        else:
            x = list()
            y = list()

        # default settings
        settings = dict(
            x=x,
            y=y,
            name=self.label,
            mode='lines',
        )
        # create plot with default settings
        _plot = go.Scatter(**settings)
        # update plot
        return _plot.update(kwargs)

    def figure(self,
               index: Optional[int] = None,
               n: Optional[int] = None,
               **kwargs) -> go.Figure:
        """ Returns a figure with the scatter plot of the trace.

        :param int index: start index of the samples to plot
        :param n: number of samples to plot
        """
        return go.Figure(self.plot(index, n, **kwargs))


@dataclass
class Digital(Trace):
    """ Trace data class for time-discrete digital signal samples.
    """

    def plot(self,
             index: Optional[int] = None,
             n: Optional[int] = None,
             **kwargs) -> go.Scatter:
        """ Returns the plot of the digital signal trace.

        :param int index: start index of the samples to plot
        :param n: number of samples to plot
        """
        # pack x,y-pairs
        pairs = list(zip(self.iter_x(), self))

        if pairs:
            # slice pairs
            index = 0 if index is None else max(0, index)
            if n is None:
                pairs = pairs[index:]
            elif n <= 0:
                pairs = pairs[index:index + 1]
            else:
                pairs = pairs[index:index + n]

            # unpack x,y-pairs
            x, y = zip(*pairs)
        else:
            x = list()
            y = list()

        # default settings
        settings = dict(
            x=x,
            y=y,
            name=self.label,
            mode='lines',
            line=dict(shape='hv')
        )

        # create plot with default settings
        _plot = go.Scatter(**settings)
        # update plot
        return _plot.update(kwargs)


def as_traces(samples: List[Dict[str, Any]]) -> Dict[str, List[Any]]:
    """ Converts the list of samples into the trace format."""
    if not samples:
        return dict()
    samples = samples
    names = list(samples[0].keys())
    trace = defaultdict(list)
    for sample in samples:
        for name in names:
            trace[name].append(sample[name])
    return dict(trace)


@dataclass(eq=False)
class Traces(MutableMapping):
    """ Base data class for a collection of traces with mutable mapping support.
    """

    def labels(self) -> Tuple[str, ...]:
        """ Returns a tuple of the trace labels in the collection."""
        return tuple([trace.label for trace in self.values()])

    def relabel(self, label: str) -> Traces:
        """ Relabels the all traces with in the collection by keeping the last
        part of the trace :attr:`~Trace.label` unchanged and the rest replaced
        by the base *label*.

        :param str label: base label to set for the traces in the collection.
        """
        for field_ in fields(self):
            trace = getattr(self, field_.name)
            if isinstance(trace, Trace):
                trace.label = f"{label}:{trace.label.split(':')[-1]}"
        return self

    def __setitem__(self, key: str, value: Trace):
        self.__dict__[key] = value

    def __getitem__(self, key) -> Trace:
        return self.__dict__[key]

    def __delitem__(self, key):
        raise NotImplemented()

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self) -> int:
        return len(self.__dict__)

    def fields(self) -> Tuple[Any, ...]:
        """ Returns a tuple describing the fields of the data class."""
        return fields(self)

    def as_dict(self) -> Dict[str, Any]:
        """ Returns the collection of traces as a dictionary.
        """
        return asdict(self)

    def as_tuple(self) -> tuple[Any, ...]:
        """ Returns the collection of traces as a tuple.
        """
        return astuple(self)


@dataclass(eq=False)
class StatisticsTraces(Traces):
    """ Collection of :class:`Statistics` traces for a set of signal samples
    statistically analyzed."""

    #: Arithmetic mean of the set (1st common moment).
    mean: Trace = field(default_factory=Trace)
    #: Linear weighted mean of the set.
    weighted_mean: Trace = field(default_factory=Trace)
    #: Median of the set.
    median: Trace = field(default_factory=Trace)
    #: Mode of the set.
    mode: Trace = field(default_factory=Trace)
    #: Root mean square of the set
    rms: Trace = field(default_factory=Trace)
    #: Minimum in the set.
    minimum: Trace = field(default_factory=Trace)
    #: Maximum in the set
    maximum: Trace = field(default_factory=Trace)
    #: Range of the set.
    range: Trace = field(default_factory=Trace)
    #: Mid-range of the set.
    midrange: Trace = field(default_factory=Trace)
    #: Empirical absolute error of the set (1st central moment).
    absolute_error: Trace = field(default_factory=Trace)
    #: Empirical biased sample variance of the set (2nd central moment).
    variance: Trace = field(default_factory=Trace)
    #: Empirical biased sample standard deviation of the set.
    deviation: Trace = field(default_factory=Trace)
    #: Empirical biased sample coefficient of variation of the set.
    coefficient: Trace = field(default_factory=Trace)
    #: Empirical biased sample skew of the set (3rd central moment).
    skew: Trace = field(default_factory=Trace)
    #: Empirical biased sample kurtosis of the set (4th central moment).
    kurtosis: Trace = field(default_factory=Trace)

    def figure(self,
               index: Optional[int] = None,
               n: Optional[int] = None,
               original: Optional[Trace] = None,
               subplots: Optional[Dict[str, Any]] = None) -> go.Figure:
        """ Returns a figure of subplots for the traces in the collection.

        :param int index: start index of the samples to plot
        :param n: number of samples to plot
        :param Trace original: optional original trace to add to the plot
        :param dict subplots: dictionary with the settings for the subplots
        """
        # base subplots configuration
        subplots_ = dict(
            rows=6,
            cols=1,
            shared_xaxes=True,
            row_heights=(3, 1, 1, 1, 1, 1),
            vertical_spacing=0.01,
            x_title='samples')

        if subplots is not None:
            subplots_.update(subplots)
        fig = make_subplots(**subplots_)

        # row 1
        if isinstance(original, Trace):
            fig.add_trace(original.plot(index, n),
                          row=1, col=1)
        fig.add_trace(self.mean.plot(index, n),
                      row=1, col=1)
        fig.add_trace(self.weighted_mean.plot(index, n),
                      row=1, col=1)
        fig.add_trace(self.median.plot(index, n),
                      row=1, col=1)
        fig.add_trace(self.mode.plot(index, n),
                      row=1, col=1)
        fig.add_trace(self.midrange.plot(index, n),
                      row=1, col=1)
        fig.add_trace(self.rms.plot(index, n),
                      row=1, col=1)
        fig.add_trace(self.minimum.plot(index, n),
                      row=1, col=1)
        fig.add_trace(self.maximum.plot(index, n),
                      row=1, col=1)
        # row 2
        fig.add_trace(self.range.plot(index, n, fill='tozeroy'),
                      row=2, col=1)
        # row 3
        fig.add_trace(self.absolute_error.plot(index, n),
                      row=3, col=1)
        fig.add_trace(self.variance.plot(index, n),
                      row=3, col=1)
        fig.add_trace(self.deviation.plot(index, n),
                      row=3, col=1)
        # row 4
        fig.add_trace(self.coefficient.plot(index, n, fill='tozeroy'),
                      row=4, col=1)
        # row 5
        fig.add_trace(self.skew.plot(index, n, fill='tozeroy'),
                      row=5, col=1)
        # row 6
        fig.add_trace(self.kurtosis.plot(index, n, fill='tozeroy'),
                      row=6, col=1)

        # base layout configuration
        fig.update_layout(
            height=960,
            margin=dict(t=50, b=60, l=50, r=50)
        )

        return fig


@dataclass(eq=False)
class MovingAverageTraces(StatisticsTraces):
    """ Collection of :class:`Statistics` traces for signal samples processed
    with a simple moving average.
    """


@dataclass(eq=False)
class SetTraces(StatisticsTraces):
    """ Collection of :class:`Statistics` traces for the combined set of
    multiple signal samples."""

    @classmethod
    def from_traces(cls, *operands: Tuple[Operand], **kwargs) -> SetTraces:
        """ Returns the collection of :class:`Statistics` traces computed over
        the combined sets of the *operands*.

        An operand can be either a number or an array-like iterable.

        :param operands: operands to compute the statistics with
        :keyword str label: optional traces base label to set

        .. note:: All iterable *operands* must have the same length, otherwise
            only a subset of the operand values is returned!
        """
        instance = cls(**combine(*operands, **kwargs))
        label = kwargs.get('label')
        if label is not None:
            return instance.relabel(label)
        else:
            return instance


def combine(*operands: Tuple[Operand], **kwargs) -> Dict[str, Trace]:
    """ Returns a dictionary with the traces for the statistics results computed
    over the combined sets of *operands*.

    An operand can be either a number or an array-like iterable.

    :param operands: operands to compute the statistics with
    :keyword str label: optional trace label stem to set

    .. note:: All iterable *operands* must have the same length, otherwise
        only a subset of the operand values is returned!
    """
    if not operands:
        return dict()
    samples = list()
    for values in zip(*map(vectorize, operands)):
        trace = Trace(samples=values)
        mean = trace.mean()
        minimum = trace.min()
        maximum = trace.max()
        deviation = trace.std(center=mean)
        result = Statistics(
            mean=mean,
            weighted_mean=trace.weighted_mean(),
            median=trace.median(),
            mode=trace.mode(),
            rms=trace.rms(),
            minimum=trace.min(),
            maximum=trace.max(),
            range=maximum - minimum,
            midrange=trace.midrange(),
            absolute_error=sum(abs(trace - mean)),
            variance=trace.variance(center=mean),
            deviation=trace.std(center=mean),
            coefficient=trace.coefficient(center=mean, std=deviation),
            skew=trace.skew(center=mean, std=deviation),
            kurtosis=trace.kurtosis(center=mean, std=deviation)
        )
        samples.append(asdict(result))

    traces = dict()
    label = kwargs.get('label', 'SetTrace')
    for key, value in as_traces(samples).items():
        traces[key] = Trace(label=f'{label}:{key}',
                            samples=value)
    return traces


@dataclass(eq=True, order=True, frozen=True)
class Statistics:
    """ Statistics results."""
    #: Arithmetic mean of the set (1st common moment)
    mean: float = 0.0
    #: Weighted mean of the set
    weighted_mean: float = 0.0
    #: Median of the set
    median: float = 0.0
    #: Mode of the set
    mode: float = 0.0
    #: Root mean square of the set
    rms: float = 0.0
    #: Minimum in the set
    minimum: float = 0.0
    #: Maximum in the set
    maximum: float = 0.0
    #: Range of the set
    range: float = 0.0
    #: Mid-range of the set
    midrange: float = 0.0
    #: Empirical absolute error of the set (1st central moment).
    absolute_error: float = 0.0
    #: Empirical biased sample variance of the set (2nd central moment).
    variance: float = 0.0
    #: Empirical biased sample standard deviation of the set.
    deviation: float = 0.0
    #: Empirical biased sample coefficient of variation of the set.
    coefficient: float = 0.0
    #: Empirical biased sample skew of the set (3rd central moment).
    skew: float = 0.0
    #: Empirical biased sample kurtosis of the set (4th central moment).
    kurtosis: float = 0.0


@dataclass(eq=False)
class VectorTraces(Traces):
    """ Collection of traces for two signal samples converted into a vector
    represented in polar coordinates.
    """
    #: Trace with cartesian x-coordinates of the vector
    x: Trace = field(default_factory=Trace)
    #: Trace with cartesian y-coordinates of the vector
    y: Trace = field(default_factory=Trace)
    #: Trace with radii of the vector
    r: Optional[Trace] = field(default=None)
    #: Trace with angles of the vector in radians [-pi..pi]
    phi: Optional[Trace] = field(default=None)
    #: Trace with angles of the vector in degree [0..360].
    theta: Optional[Trace] = field(default=None)
    #: Trace with euclidean distances of the consecutive x,y-points.
    distance: Optional[Trace] = field(default=None)
    #: Trace with dot products of the consecutive x,y-points.
    dot: Optional[Trace] = field(default=None)

    def __post_init__(self):
        # dictionary with the vector results
        vector = polar(self.x, self.y)
        if self.r is None:
            self['r'] = vector.get('r', Trace(label='Vector:r'))
        if self.phi is None:
            self['phi'] = vector.get('phi', Trace(label='Vector:phi'))
        if self.theta is None:
            self['theta'] = vector.get('theta', Trace(label='Vector:theta'))
        self.distance = Trace('Vector:distance')
        self.dot = Trace('Vector:dot')
        for coordinates in zip(self.x.window(2), self.y.window(2)):
            points = [(x, y) for x, y in zip(coordinates[0], coordinates[1])]
            self.distance.samples.append(math.dist(*points))
            self.dot.samples.append(np.dot(*points))

    def plot(self,
             index: Optional[int] = None,
             n: Optional[int] = None,
             **kwargs) -> go.Scatterpolar:
        """ Returns the scatter polar plot of the vector traces.

        :param int index: start index of the samples to plot
        :param n: number of samples to plot
        """
        # pack r,theta-pairs
        pairs = list(zip(self.r, self.theta))

        if pairs:
            # slice pairs
            index = 0 if index is None else max(0, index)
            if n is None:
                pairs = pairs[index:]
            elif n <= 0:
                pairs = pairs[index:index + 1]
            else:
                pairs = pairs[index:index + n]

            # unpack r,theta-pairs
            r, theta = zip(*pairs)
        else:
            r = list()
            theta = list()

        # default settings
        settings = dict(
            r=r,
            theta=theta,
            name='Vector',
            mode='lines+markers'
        )
        # create plot with default settings
        _plot = go.Scatterpolar(**settings)
        # update plot
        return _plot.update(kwargs)


def polar(x: Trace, y: Trace, **kwargs) -> Dict[str, Trace]:
    """ Returns a dictionary with the traces for the two *x*, *y* signal samples
    converted into a vector represented in polar coordinates.

    :param Trace x: cartesian x-coordinate signal trace of the vector
    :param Trace y: cartesian y-coordinate signal trace of the vector
    :keyword str label: optional traces base label to set.
        Default is ``Vector``.
    """
    samples = list()
    for p in zip(x, y):
        vector = Point2D(*p).as_vector()
        samples.append(asdict(vector))

    traces = dict()
    label = kwargs.get('label', 'Vector')
    for key, value in as_traces(samples).items():
        traces[key] = Trace(label=f'{label}:{key}',
                            samples=value)
    if not traces:
        for item in fields(Vector):
            traces[item.name] = Trace(label=f'{label}:{item.name}')

    return traces


@dataclass(eq=False)
class Vector:
    """ Vector representation by polar coordinates."""
    #: Radius of the vector.
    r: float = 0.0
    #: Angle of the vector in radians [-pi..+pi].
    phi: float = 0.0
    #: Angle of the vector in degrees [0..360].
    theta: Optional[float] = None

    def __post_init__(self):
        if self.theta is None:
            angel = float(np.degrees(self.phi))
            self.theta = angel + 360.0 if angel < 0.0 else angel


@dataclass(eq=True, order=True)
class Point2D:
    """ 2-dimensional point representation by cartesian coordinates."""
    #: X-coordinate of the 2-dimensional point.
    x: int = 0.0
    #: Y-coordinate of the 2-dimensional point.
    y: float = 0.0

    @property
    def r(self):
        """ Radius of the 2-dimensional point."""
        return math.sqrt(self.x ** 2 + self.y ** 2)

    @property
    def phi(self):
        """ Angle of the 2-dimensional point in radians [-pi..+pi]."""
        return float(np.arctan2(self.y, self.x))

    @property
    def theta(self):
        """ Angle of the 2-dimensional point in degrees [0..360]."""
        angel = float(np.degrees(self.phi))
        return angel + 360.0 if angel < 0 else angel

    def as_vector(self):
        """ Returns a :class:`Vector` for the 2-dimensional point."""
        return Vector(self.r, self.phi)

    def as_dict(self) -> Dict[str, Any]:
        """ Returns the 2-dimensional point as a dictionary."""
        return asdict(self)

    def as_tuple(self) -> tuple[Any, ...]:
        """ Returns the 2-dimensional point as a tuple."""
        return astuple(self)

    def __iter__(self):
        """ Returns an iterator over the coordinates of the 2-dimensional point.
        """
        return iter(astuple(self))

    def __reversed__(self):
        """ Returns a reverse iterator over the coordinates of the 2-dimensional
        point.
        """
        return reversed(astuple(self))


@dataclass(eq=True, order=True)
class Point3D(Point2D):
    """ 3-dimensional point representation by cartesian coordinates."""
    #: X-coordinate of the 3-dimensional point.
    x: int = 0.0
    #: Y-coordinate of the 3-dimensional point.
    y: float = 0.0
    #: Z-coordinate of the 3-dimensional point.
    z: float = 0.0

    @property
    def r(self):
        """ Radius of the 3-dimensional point."""
        return math.hypot(self.x, self.y, self.z)

    def as_dict(self) -> Dict[str, Any]:
        """ Returns the 3-dimensional point as a dictionary."""
        return asdict(self)

    def as_tuple(self) -> tuple[Any, ...]:
        """ Returns the 3-dimensional point as a tuple."""
        return astuple(self)

    def __iter__(self):
        """ Returns an iterator over the coordinates of the 3-dimensional point.
        """
        return iter(astuple(self))

    def __reversed__(self):
        """ Returns a reverse iterator over the coordinates of the 3-dimensional
        point.
        """
        return reversed(astuple(self))


@dataclass(eq=False)
class SlewRateLimiterTraces(Traces):
    """ Collection of :class:`SlewRateLimiter` traces for signal samples
    processed with a slew-rate limiter. """
    #: Slew-rate limited signal level value.
    level: Trace = field(default_factory=Trace)
    #: Signal deviation.
    deviation: Trace = field(default_factory=Trace)
    #: Slew-rate limiter active ``(0: signal unlimited, 1: signal limited)``.
    active: Trace = field(default_factory=Trace)

    def figure(self,
               index: Optional[int] = None,
               n: Optional[int] = None,
               original: Optional[Trace] = None,
               subplots: Optional[Dict[str, Any]] = None) -> go.Figure:
        """ Returns a figure of subplots for the traces.

        :param int index: start index of the samples to plot
        :param n: number of samples to plot
        :param Trace original: optional original trace to add to the plot
        :param dict subplots: dictionary with the settings for the subplots
        """
        # base subplots configuration
        subplots_ = dict(
            rows=3,
            cols=1,
            shared_xaxes=True,
            row_heights=(2, 0.5, 0.25),
            vertical_spacing=0.01,
            x_title='samples')

        if subplots is not None:
            subplots_.update(subplots)
        fig = make_subplots(**subplots_)

        # row 1
        if isinstance(original, Trace):
            fig.add_trace(original.plot(index, n),
                          row=1, col=1)
        fig.add_trace(self.level.plot(index, n),
                      row=1, col=1)

        # row 2
        fig.add_trace(self.deviation.plot(index, n, fill='tozeroy'),
                      row=2, col=1)
        # row 3
        fig.add_trace(self.active.digital.plot(index, n, fill='tozeroy'),
                      row=3, col=1)

        # base layout configuration
        fig.update_layout(
            height=800,
            margin=dict(t=50, b=60, l=50, r=50)
        )

        return fig


@dataclass(eq=True, frozen=True)
class SlewRateLimiter:
    """ Slew-rate limiter results."""
    #: Slew-rate limited signal level value.
    level: float = 0.0
    #: Signal deviation.
    deviation: float = 0.0
    #: Slew-rate limiter active ``(0: signal unlimited, 1: signal limited)``.
    active: int = 0


@dataclass(eq=False)
class ExponentialSmoothingTraces(Traces):
    """ Collection of :class:`ExponentialSmoothing` traces for signal samples
    processed with a 2nd-order exponential smoothing. """
    #: Signal forecast value.
    forecast: Trace = field(default_factory=Trace)
    #: Sign of the signal forecast ``(-1: negative, 0: zero, 1: positive)``.
    forecast_sign: Trace = field(default_factory=Trace)
    #: Signal level value.
    level: Trace = field(default_factory=Trace)
    #: Sign of the signal level ``(-1: negative, 0: zero, 1: positive)``.
    level_sign: Trace = field(default_factory=Trace)
    #: Signal prognosis value for the first-order exponential smoothing.
    prognosis1: Trace = field(default_factory=Trace)
    #: Signal prognosis value for the second-order exponential smoothing.
    prognosis2: Trace = field(default_factory=Trace)
    #: Signal prognosis value of the exponential smoothing.
    prognosis: Trace = field(default_factory=Trace)
    #: First-order exponentially smoothed signal value.
    smoothed1: Trace = field(default_factory=Trace)
    #: Second-order exponentially smoothed signal value.
    smoothed2: Trace = field(default_factory=Trace)
    #: Signal prognosis trend value.
    trend: Trace = field(default_factory=Trace)
    #: Sign of the signal trend ``(-1: negative, 0: zero, 1: positive)``.
    trend_sign: Trace = field(default_factory=Trace)
    #: Inflection of the signal prognosis trend ``(1: increase, -1: decrease)``.
    trend_inflection: Trace = field(default_factory=Trace)
    #: Signal prognosis error.
    error: Trace = field(default_factory=Trace)
    #: Signal prognosis correction.
    correction: Trace = field(default_factory=Trace)
    #: Empirical absolute error of the distribution (1st central moment).
    absolute_error: Trace = field(default_factory=Trace)
    #: Empirical variance of the distribution (2nd central moment).
    variance: Trace = field(default_factory=Trace)
    #: Empirical standard deviation of the distribution.
    deviation: Trace = field(default_factory=Trace)
    #: Empirical skew of the distribution (3rd central moment).
    skew: Trace = field(default_factory=Trace)
    #: Empirical kurtosis of the distribution (4th central moment).
    kurtosis: Trace = field(default_factory=Trace)

    def figure(self,
               index: Optional[int] = None,
               n: Optional[int] = None,
               original: Optional[Trace] = None,
               subplots: Optional[Dict[str, Any]] = None) -> go.Figure:
        """ Returns a figure of subplots for the traces.

        :param int index: start index of the samples to plot
        :param n: number of samples to plot
        :param Trace original: optional original trace to add to the plot
        :param dict subplots: dictionary with the settings for the subplots
        """
        # base subplots configuration
        subplots_ = dict(
            rows=10,
            cols=1,
            shared_xaxes=True,
            row_heights=(3, 0.25, 0.25, 1.25, 0.25, 0.25, 1, 1, 1, 0.75),
            vertical_spacing=0.01,
            x_title='samples')

        if subplots is not None:
            subplots_.update(subplots)
        fig = make_subplots(**subplots_)

        # row 1
        if isinstance(original, Trace):
            fig.add_trace(original.plot(index, n),
                          row=1, col=1)
        fig.add_trace(self.forecast.plot(index, n),
                      row=1, col=1)
        fig.add_trace(self.level.plot(index, n),
                      row=1, col=1)
        fig.add_trace(self.prognosis1.plot(index, n),
                      row=1, col=1)
        fig.add_trace(self.prognosis2.plot(index, n),
                      row=1, col=1)
        fig.add_trace(self.smoothed1.plot(index, n),
                      row=1, col=1)
        fig.add_trace(self.smoothed2.plot(index, n),
                      row=1, col=1)
        # row 2
        fig.add_trace(self.forecast_sign.digital.plot(index, n, fill='tozeroy'),
                      row=2, col=1)
        # row 3
        fig.add_trace(self.level_sign.digital.plot(index, n, fill='tozeroy'),
                      row=3, col=1)
        # row 4
        fig.add_trace(self.trend.plot(index, n, fill='tozeroy'),
                      row=4, col=1)
        # row 5
        fig.add_trace(self.trend_sign.digital.plot(index, n, fill='tozeroy'),
                      row=5, col=1)
        # row 6
        fig.add_trace(self.trend_inflection.digital.plot(index, n, fill='tozeroy'),
                      row=6, col=1)
        # row 7
        fig.add_trace(self.error.plot(index, n),
                      row=7, col=1)
        fig.add_trace(self.correction.plot(index, n),
                      row=7, col=1)
        # row 8
        fig.add_trace(self.absolute_error.plot(index, n),
                      row=8, col=1)
        fig.add_trace(self.variance.plot(index, n),
                      row=8, col=1)
        fig.add_trace(self.deviation.plot(index, n, fill='tozeroy'),
                      row=8, col=1)
        # row 9
        fig.add_trace(self.skew.plot(index, n, fill='tozeroy'),
                      row=9, col=1)
        # row 10
        fig.add_trace(self.kurtosis.plot(index, n, fill='tozeroy'),
                      row=10, col=1)

        # base layout configuration
        fig.update_layout(
            height=1440,
            margin=dict(t=50, b=60, l=50, r=50)
        )

        return fig


@dataclass(eq=True, frozen=True)
class ExponentialSmoothing:
    """ 2nd-order exponential smoothing results."""
    #: Signal forecast value.
    forecast: float = 0.0
    #: Sign of the signal level ``(-1: negative, 0: zero, 1: positive)``.
    forecast_sign: float = 0
    #: Signal level value.
    level: float = 0.0
    #: Sign of the signal level ``(-1: negative, 0: zero, 1: positive)``.
    level_sign: float = 0.0
    #: Signal prognosis value for the first-order exponential smoothing.
    prognosis1: float = 0.0
    #: Signal prognosis value for the second-order exponential smoothing.
    prognosis2: float = 0.0
    #: Signal prognosis value of the exponential smoothing.
    prognosis: float = 0.0
    #: First-order exponentially smoothed signal value.
    smoothed1: float = 0.0
    #: Second-order exponentially smoothed signal value.
    smoothed2: float = 0.0
    #: Signal prognosis trend value.
    trend: float = 0.0
    #: Sign of the signal trend ``(-1: negative, 0: zero, 1: positive)``.
    trend_sign: float = 0.0
    #: Inflection of the signal prognosis trend ``(1: increase, -1: decrease)``.
    trend_inflection: float = 0.0
    #: Signal prognosis error.
    error: float = 0.0
    #: Signal prognosis correction.
    correction: float = 0.0
    #: Empirical absolute error of the distribution (1st central moment).
    absolute_error: float = 0.0
    #: Empirical variance of the distribution (2nd central moment).
    variance: float = 0.0
    #: Empirical standard deviation of the distribution.
    deviation: float = 0.0
    #: Empirical skew of the distribution (3rd central moment).
    skew: float = 0.0
    #: Empirical kurtosis of the distribution (4th central moment).
    kurtosis: float = 0.0


@dataclass(eq=False)
class LinearRegressionTraces(Traces):
    """ Collection of :class:`LinearRegression` traces for signal samples
    processed with a moving linear regression. """
    #: Current y-coordinate of the approximated line.
    level: Trace = field(default_factory=Trace)
    #: Slope of the approximated line.
    slope: Trace = field(default_factory=Trace)
    #: Y-intercept of the approximated line.
    intercept: Trace = field(default_factory=Trace)
    #: Arithmetic mean of the y-coordinate values of the approximated line.
    mean: Trace = field(default_factory=Trace)
    #: Median of the y-coordinate values of the approximated line.
    median: Trace = field(default_factory=Trace)
    #: Minimum of the y-coordinate values of the approximated line.
    minimum: Trace = field(default_factory=Trace)
    #: Maximum of the y-coordinate values of the approximated line.
    maximum: Trace = field(default_factory=Trace)
    #: Range of the y-coordinate values of the approximated line.
    range: Trace = field(default_factory=Trace)
    #: Current error from the approximated line.
    error: Trace = field(default_factory=Trace)
    #: Maximal negative y-coordinate error from the approximated line.
    negative_error: Trace = field(default_factory=Trace)
    #: Maximal positive y-coordinate error from the approximated line.
    positive_error: Trace = field(default_factory=Trace)
    #: Empirical absolute error of the distribution (1st central moment).
    absolute_error: Trace = field(default_factory=Trace)
    #: Empirical variance of the distribution (2nd central moment).
    variance: Trace = field(default_factory=Trace)
    #: Empirical standard deviation of the distribution.
    deviation: Trace = field(default_factory=Trace)
    #: Empirical skew of the distribution (3rd central moment).
    skew: Trace = field(default_factory=Trace)
    #: Empirical kurtosis of the distribution (4th central moment).
    kurtosis: Trace = field(default_factory=Trace)

    def figure(self,
               index: Optional[int] = None,
               n: Optional[int] = None,
               original: Optional[Trace] = None,
               subplots: Optional[Dict[str, Any]] = None) -> go.Figure:
        """ Returns a figure of subplots for the traces in the collection.

        :param int index: start index of the samples to plot
        :param n: number of samples to plot
        :param Trace original: optional original trace to add to the plot
        :param dict subplots: dictionary with the settings for the subplots
        """
        # base subplots configuration
        subplots_ = dict(
            rows=7,
            cols=1,
            shared_xaxes=True,
            row_heights=(5, 1, 1, 1, 1, 1, 1),
            vertical_spacing=0.01,
            x_title='samples')

        if subplots is not None:
            subplots_.update(subplots)
        fig = make_subplots(**subplots_)

        # row 1
        if isinstance(original, Trace):
            fig.add_trace(original.plot(index, n),
                          row=1, col=1)
        fig.add_trace(self.level.plot(index, n),
                      row=1, col=1)
        fig.add_trace(self.mean.plot(index, n),
                      row=1, col=1)
        fig.add_trace(self.median.plot(index, n),
                      row=1, col=1)
        fig.add_trace(self.maximum.plot(index, n),
                      row=1, col=1)
        fig.add_trace(self.minimum.plot(index, n),
                      row=1, col=1)
        fig.add_trace(self.intercept.plot(index, n),
                      row=1, col=1)
        # row 2
        fig.add_trace(self.range.plot(index, n, fill='tozeroy'),
                      row=2, col=1)
        # row 3
        fig.add_trace(self.slope.plot(index, n, fill='tozeroy'),
                      row=3, col=1)
        # row 4
        fig.add_trace(self.error.plot(index, n, fill='tozeroy'),
                      row=4, col=1)
        fig.add_trace(self.positive_error.plot(index, n),
                      row=4, col=1)
        fig.add_trace(self.negative_error.plot(index, n),
                      row=4, col=1)
        # row 5
        fig.add_trace(self.absolute_error.plot(index, n),
                      row=5, col=1)
        fig.add_trace(self.variance.plot(index, n),
                      row=5, col=1)
        fig.add_trace(self.deviation.plot(index, n),
                      row=5, col=1)
        # row 6
        fig.add_trace(self.skew.plot(index, n, fill='tozeroy'),
                      row=6, col=1)
        # row 7
        fig.add_trace(self.kurtosis.plot(index, n, fill='tozeroy'),
                      row=7, col=1)

        # base layout configuration
        fig.update_layout(
            height=1000,
            margin=dict(t=50, b=60, l=50, r=50)
        )

        return fig


@dataclass(eq=True, frozen=True)
class LinearRegression:
    """ Linear regression results."""
    #: Current y-coordinate of the approximated line.
    level: float = 0.0
    #: Slope of the approximated line.
    slope: float = 0.0
    #: Y-intercept of the approximated line.
    intercept: float = 0.0
    #: Arithmetic mean of the y-coordinate values of the approximated line.
    mean: float = 0.0
    #: Median of the y-coordinate values of the approximated line.
    median: float = 0.0
    #: Minimum of the y-coordinate values of the approximated line.
    minimum: float = 0.0
    #: Maximum of the y-coordinate values of the approximated line.
    maximum: float = 0.0
    #: Range of the y-coordinate values of the approximated line.
    range: float = 0.0
    #: Current error from the approximated line.
    error: float = 0.0
    #: Maximal negative y-coordinate error from the approximated line.
    negative_error: float = 0.0
    #: Maximal positive y-coordinate error from the approximated line.
    positive_error: float = 0.0
    #: Empirical absolute error of the distribution (1st central moment).
    absolute_error: float = 0.0
    #: Empirical variance of the distribution (2nd central moment).
    variance: float = 0.0
    #: Empirical standard deviation of the distribution.
    deviation: float = 0.0
    #: Empirical skew of the distribution (3rd central moment).
    skew: float = 0.0
    #: Empirical kurtosis of the distribution (4th central moment).
    kurtosis: float = 0.0
