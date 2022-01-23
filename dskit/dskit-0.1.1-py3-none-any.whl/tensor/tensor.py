from typing import Callable, Iterable, Optional, Tuple, Union

import operator as op

from itertools import product
from itertools import starmap

import numpy as np

from nonion import padr
from nonion import replicate
from nonion import slide

Coordinate = Tuple[int, ...]
RawSlice = Union[
  Tuple[Optional[int]],
  Tuple[Optional[int], Optional[int]],
  Tuple[Optional[int], Optional[int], Optional[int]]
]
Shape = Tuple[int, ...]

def slices(xs: Iterable[RawSlice]) -> Tuple[slice, ...]:
  return tuple(starmap(slice, xs))

def batches(
  n: int = 32,
  step: Optional[int] = None,
  exact: bool = True
  ) -> Callable[[Iterable[Tuple[np.ndarray, ...]]], Iterable[Tuple[np.ndarray, ...]]]:

  return lambda xs: map(batch, slide(n, step or n, exact)(xs))

def batch(ys: Tuple[Tuple[np.ndarray, ...], ...]) -> Tuple[np.ndarray, ...]:
  return tuple(map(np.stack, zip(*ys)))

def cycle(tensor: Union[np.ndarray, float], shape: Shape) -> np.ndarray:
  tensor = tensor if isinstance(tensor, np.ndarray) else np.array(tensor)

  s = tuple(padr(len(shape), 1)(tensor.shape))
  t = tensor.reshape(s)

  for axis, n in enumerate(shape):
    t = np.concatenate(tuple(replicate(n)(t)), axis=axis)

  return t

def gridrange(
  start: Coordinate,
  end: Optional[Coordinate] = None,
  step: Optional[Coordinate] = None
  ) -> Iterable[Coordinate]:

  if end is None:
    end = start
    start = tuple(replicate(len(end))(0))

  step = step or tuple(replicate(len(start))(1))

  ranges = map(range, start, end, step)
  return product(*ranges)

def iteraxis(tensor: np.ndarray, axis: int = 0) -> Iterable[np.ndarray]:
  t = np.moveaxis(tensor, axis, -1)
  return map(lambda x: t[x], np.ndindex(t.shape[:-1]))

def move(
  source: np.ndarray,
  destination: np.ndarray,
  coordinate: Optional[Coordinate] = None,
  inplace: bool = False
  ) -> np.ndarray:

  destination = destination if inplace else destination.copy()
  coordinate = coordinate or ()

  start: Coordinate = tuple(padr(source.ndim, 0)(coordinate))
  end = map(op.add, start, source.shape)

  raw_subslices = zip(start, end)
  subslices = slices(raw_subslices)

  destination[subslices] = source

  return destination
