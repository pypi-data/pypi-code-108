import numpy as np
from collections.abc import Iterable
from typing import Generator, Callable

# Generator class that takes either an existing generator and updates it or an iterable object and creates a generator
class TransformGenerator(Generator):
    def __init__(self, original:Iterable, transformFn:Callable=lambda x : x):
        assert isinstance(original, (list, tuple, np.ndarray))
        self.original = original
        self.res = []
        self.buildTransformedItems()
        super().__init__(self.res)

    def buildTransformedItems(self):
        for i in trange(len(original), desc="[TransformGenerator] Applying transform fn"):
            item = original[i]
            transformedItem = transformFn(i)
            if isinstance(transformedItem, Generator):
                self.res.extend([subItem for subItem in transformedItem])
            else:
                self.res.append(transformedItem)

# TODO: instantaite vs returning modulo (for random index generator, for example?)
class NWGenerator:
    def __init__(self, baseIterator):
        self.baseIterator = baseIterator
        self.ix = -1

    def __next__(self):
        self.ix += 1
        return self.baseIterator[self.ix % len(self.baseIterator)] #if self.modulo else self.baseIterator()[self.ix]
    
    def __len__(self):
        return len(self.baseIterator)
