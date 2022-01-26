#  Copyright (c) 2021. Davi Pereira dos Santos
#  This file is part of the i-dict project.
#  Please respect the license - more about this in the section (*) below.
#
#  i-dict is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  i-dict is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with i-dict.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is illegal and it is unethical regarding the effort and
#  time spent here.
#

"""
Functions to be used directly within an idict workflow
"""

# TODO: break down all sklearn and numpy used inside binarize,
#  so e.g. the fit-wrapper can be used for OHE; and binarize can be a composition.

from idict.macro import isnumber


def nomcols(input="X", output="nomcols", **kwargs):
    """
    >>> import numpy as np
    >>> X = np.array([[0, "a", 1.6], [3.2, "b", 2], [8, "c", 3]])
    >>> nomcols(X=X)
    {'nomcols': [1], '_history': Ellipsis}
    """
    X = kwargs[input]
    idxs = []
    for i, x in enumerate(X.iloc[0] if hasattr(X, "iloc") else X[0]):
        if not isnumber(x):
            idxs.append(i)
    return {output: idxs, "_history": ...}


def binarize(input="X", idxsin="nomcols", output="Xbin", **kwargs):
    """
    >>> import numpy as np
    >>> from pandas import DataFrame as DF
    >>> X = DF(np.array([[0, "a", 1.6], [3.2, "b", 2], [8, "c", 3]]))
    >>> X
         0  1    2
    0    0  a  1.6
    1  3.2  b    2
    2    8  c    3
    >>> binarize(X=X, nomcols=[1])["Xbin"]
         0    2  1_a  1_b  1_c
    0    0  1.6    1    0    0
    1  3.2    2    0    1    0
    2    8    3    0    0    1
    """
    X = kwargs[input]
    cols = kwargs[idxsin]
    if X.__class__.__name__ in ["DataFrame", "Series"]:
        import pandas

        clabels = X.columns[cols]
        Xout = pandas.get_dummies(X, prefix=clabels, columns=clabels)
    else:
        import numpy
        from sklearn.preprocessing import OneHotEncoder

        encoder = OneHotEncoder()
        nom = encoder.fit_transform(X.iloc[:, cols] if hasattr(X, "iloc") else X[:, cols]).toarray()
        num = numpy.delete(X, cols, axis=1).astype(float)
        Xout = numpy.column_stack((nom, num))
    return {output: Xout, "_history": ...}


def df2list(input="df", output="list", **kwargs):
    """
    >>> from idict import idict
    >>> d = idict.fromtoy(output_format="df")
    >>> d >>= df2list
    >>> d.list
    [['attr1', 'attr2', 'class'], [5.1, 6.4, 0.0], [1.1, 2.5, 1.0], [6.1, 3.6, 0.0], [1.1, 3.5, 1.0], [3.1, 2.5, 0.0], [4.7, 4.9, 1.0], [9.1, 3.5, 0.0], [8.3, 2.9, 1.0], [9.1, 7.2, 0.0], [2.5, 4.5, 1.0], [7.1, 6.6, 0.0], [0.1, 4.3, 1.0], [2.1, 0.1, 0.0], [0.1, 4.0, 1.0], [5.1, 4.5, 0.0], [31.1, 4.7, 1.0], [1.1, 3.2, 0.0], [2.2, 8.5, 1.0], [3.1, 2.5, 0.0], [1.1, 8.5, 1.0]]
    """
    M = kwargs[input]
    lst = [list(M.columns)] + M.to_numpy().tolist()
    return {output: lst, "_history": ...}


nomcols.metadata = {
    "id": "idict----------------------------nomcols",
    "name": "nomcols",
    "description": "List column indices of nominal attributes.",
    "parameters": ...,
    "code": ...,
}
binarize.metadata = {
    "id": "sk-1.0.1--pd-1.3.4--np-1.21.4---binarize",
    "name": "binarize",
    "description": "Binarize nominal attributes so they can be handled as numeric.",
    "parameters": ...,
    "code": ...,
}
df2list.metadata = {
    "id": "idict---pandas-1.3.4--np-1.21.4--df2list",
    "name": "df2list",
    "description": "Convert DataFrame to nested lists.",
    "parameters": ...,
    "code": ...,
}
