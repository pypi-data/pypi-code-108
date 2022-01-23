from typing import Callable, Dict, Tuple, Union

import warnings

from dataclasses import dataclass
from functools import partial

import numpy as np
import pandas as pd

from nonion import Maybe
from nonion import Pipeline
from nonion import as_catch
from nonion import in_
from nonion import star
from nonion import wraptry

from sklearn.preprocessing import OneHotEncoder

Dummifier = Callable[[pd.DataFrame], pd.DataFrame]

ENCODER_PARAMETERS = {
  "sparse": False,
  "handle_unknown": "ignore"
}

def dummifier(
  xys: Dict[str, Tuple[object, ...]],
  name: Callable[[str, object], str] = lambda n, x: n + "_" + str(x)
  ) -> Dummifier:

  to_encoder = (
    Pipeline(xys.items())
    / star(lambda x, y: (x, encoder(y, partial(name, x))))
    >> as_catch(lambda _: pd.DataFrame)
  )

  def g(xs: pd.DataFrame) -> pd.DataFrame:
    frame = (
      Pipeline(xs.iteritems())
      / star(lambda n, x: to_encoder(n)(x))
      >> partial(pd.concat, axis=1)
    )
    frame.index = xs.index
    return frame

  return g

@dataclass
class RawEncoder:
  encode: Callable[[np.ndarray], Maybe[np.ndarray]]
  invert: Callable[[np.ndarray], Maybe[np.ndarray]]
  categories: np.ndarray
  columns: Tuple[str, ...]
  dtype: type

class BaseEncoder:
  def __init__(self, raw: RawEncoder):
    self._raw = raw

    self.categories = raw.categories
    self.columns = raw.columns
    self.dtype = raw.dtype

class InverseEncoder:
  pass

class Encoder(BaseEncoder):
  def __init__(self, raw: RawEncoder):
    super().__init__(raw)

  def encode(self, xs: Tuple[object, ...]) -> pd.DataFrame:
    ys = np.expand_dims(xs, axis=-1)

    with warnings.catch_warnings():
      warnings.simplefilter("ignore")
      frame, *_ = self._raw.encode(ys) or (np.zeros((len(xs), len(self.columns))),)

    return pd.DataFrame(frame, columns=self.columns)

  def invert(self) -> InverseEncoder:
    return InverseEncoder(self._raw)

  def __call__(self, xs: Tuple[object, ...]) -> pd.DataFrame:
    return self.encode(xs)

  def __invert__(self) -> InverseEncoder:
    return self.invert()

class InverseEncoder(BaseEncoder):
  def __init__(self, raw: RawEncoder):
    super().__init__(raw)

  def encode(self, xs: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
    if isinstance(xs, pd.DataFrame):
      cs = Pipeline(self.columns) % in_(tuple(xs.columns)) >> list
      xs = xs.loc[:, cs].to_numpy()

    k = xs.shape[1] if xs.ndim == 2 else 0

    if k == len(self.columns):
      frame, *_ = self._raw.invert(xs) or (np.empty((0,), dtype=self.dtype),)
      return frame.reshape(-1)
    else:
      return np.empty((0,), dtype=self.dtype)

  def invert(self) -> Encoder:
    return Encoder(self._raw)

  def __call__(self, xs: Tuple[object, ...]) -> pd.DataFrame:
    return self.encode(xs)

  def __invert__(self) -> Encoder:
    return self.invert()

def encoder(xs: Tuple[object, ...], name: Callable[[object], str] = str) -> Encoder:
  e = OneHotEncoder(**ENCODER_PARAMETERS)
  e.fit(np.expand_dims(xs, axis=-1))

  categories, *_ = e.categories_
  raw = RawEncoder(
    encode=wraptry(e.transform),
    invert=wraptry(e.inverse_transform),
    categories=categories,
    columns=tuple(map(name, categories)),
    dtype=e.dtype
  )

  return Encoder(raw)
