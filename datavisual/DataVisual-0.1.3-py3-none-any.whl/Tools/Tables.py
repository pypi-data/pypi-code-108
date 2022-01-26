from itertools import product
import DataVisual
import numpy as np

from DataVisual.Tools.utils import _ToList


class YParameter(object):
    def __init__(self, Name):
        self.dict        = DataVisual.Yconf[Name]
        self.Name        = self.dict['name']
        self.Label       = self.dict['label']
        self.Format      = self.dict['format']
        self.Unit        = self.dict['unit']
        self.Legend      = f"{self.dict['legend']:<9} "

    def str(self, Val):
        if self.Name == 'material' :
            Val = Val.__str__()
        return f"{self.Name}: {Val:{self.Format}}"

    def __repr__(self):
        return self.Name


class _XTable(object):
    def __init__(self, X):
        self.X         = X
        self.Shape     = self.GetShape()
        self.NameTable = self.GetNameTable()

    def GetShape(self):
        return [x.GetSize() for x in self.X]

    def GetNameTable(self):
        return { x.Name: order for order, x in enumerate(self.X) }

    def GetPosition(self, Value):
        for order, x in enumerate(self.X):
            if x.Name == Value:
                return order

    def __getitem__(self, Val):
        if Val is None: return None
        if isinstance(Val, str):
            Val = Val
            idx = self.NameTable[Val]
            return self.X[idx]
        else:
            return self.X[Val]


    def GetSlicer(self, x, Exclude=None):
        Xidx             = self.NameTable[x]

        self.Shape[Xidx] = None

        xval             = self.X[Xidx].Value

        Shape            = self.Shape

        if Exclude:
            Shape = np.delete(Shape, self.GetPosition(Exclude))

        DimSlicer        = [range(s) if s is not None else [slice(None)] for s in Shape]

        return zip( product(*DimSlicer), self.X)


    def Remove(self, axis):
        lst = [x for x in self if x.Name != axis]

        newXtable = _XTable(X=lst)

        return newXtable

    def GetCommonLegend(self):
        common  = ''

        for order, Parameter in enumerate(self.X):

            if Parameter.GetSize() == 1:
                common += Parameter.str(0)

        return common


    def GetLabels(self, idx, Exclude=None):
        Exclude = _ToList(Exclude)
        common  = ''
        diff    = ''

        for order, Parameter in enumerate(self.X):
            if Parameter in Exclude:
                continue
            if Parameter.GetSize() == 1:
                common += Parameter.str(idx[order])
            else:
                diff += Parameter.str(idx[order])

        return diff, common


class _YTable(object):
    def __init__(self, Y=[]):
        self.Y = Y
        self.NameTable = self.GetNameTable()


    def GetShape(self):
        return [x.Size for x in self.Y] + [1]

    def GetNameTable(self):
        return { x.Name: order for order, x in enumerate(self.Y) }


    def __getitem__(self, Val):
        if isinstance(Val, str):
            Val = Val
            idx = self.NameTable[Val]
            return self.Y[idx]
        else:
            return self.Y[Val]

    def GetSlicer(self, x):
        Xidx        = self.NameTable[x]

        self.Shape[Xidx] = None

        xval        = self.Y[Xidx].Array

        DimSlicer   = [range(s) if s is not None else [slice(None)] for s in self.Shape[:-1]]

        return product(*DimSlicer), xval
