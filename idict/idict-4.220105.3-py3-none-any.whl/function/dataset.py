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
from io import StringIO

from idict.function import isplit


def Xy2M(input=["X", "y"], output="M", **kwargs):
    """
    >>> from idict import idict
    >>> from idict.function.dataset import df2Xy
    >>> d = idict.fromtoy(output_format="df")
    >>> d = d >> df2Xy >> Xy2M
    >>> d.M
    array([[ 5.1,  6.4,  0. ],
           [ 1.1,  2.5,  1. ],
           [ 6.1,  3.6,  0. ],
           [ 1.1,  3.5,  1. ],
           [ 3.1,  2.5,  0. ],
           [ 4.7,  4.9,  1. ],
           [ 9.1,  3.5,  0. ],
           [ 8.3,  2.9,  1. ],
           [ 9.1,  7.2,  0. ],
           [ 2.5,  4.5,  1. ],
           [ 7.1,  6.6,  0. ],
           [ 0.1,  4.3,  1. ],
           [ 2.1,  0.1,  0. ],
           [ 0.1,  4. ,  1. ],
           [ 5.1,  4.5,  0. ],
           [31.1,  4.7,  1. ],
           [ 1.1,  3.2,  0. ],
           [ 2.2,  8.5,  1. ],
           [ 3.1,  2.5,  0. ],
           [ 1.1,  8.5,  1. ]])
    """
    import numpy

    return {output: numpy.column_stack((kwargs[input[0]], kwargs[input[1]])), "_history": ...}


def df2Xy(input="df", Xout="X", yout="y", **kwargs):
    """
    >>> from idict import let, idict
    >>> d = idict.fromminiarff()
    >>> d >>= df2Xy
    >>> d.show(colored=False)
    {
        "X": "→(input Xout yout df)",
        "y": "→(input Xout yout df)",
        "_history": "idict-pandas-1.3.4--sklearn-1.0.1--df2Xy",
        "df": "«{'attr1@REAL': {0: 5.1, 1: 3.1}, 'attr2@REAL': {0: 3.5, 1: 4.5}, 'class@{0,1}': {0: '0', 1: '1'}}»",
        "_id": "0GLFP05fQeW7dVFF0m50N8yVTgl-1.0.1--df2Xy",
        "_ids": {
            "X": "NeRaymrp6pcRWPAFc4t8A9.BnboEM0.1BllNL8yo",
            "y": "BLW9uncfc4h7G4e1lK66TjtG5bj6uMX2oEJxZBbm",
            "_history": "wfGnutW0WADjXhbuxxKPp5WD5po2Jk6W4srWxjdQ",
            "df": "q3_b71eb05c4be05eba7b6ae5a9245d5dd70b81b (content: 6X_dc8ccea3b2e46f1c78967fae98b692701dc99)"
        }
    }
    >>> d.y
    array([0, 1])
    """
    from sklearn.preprocessing import LabelEncoder

    le = LabelEncoder()
    df = kwargs[input]
    X_ = df.drop(df.columns[[-1]], axis=1)
    y_ = le.fit_transform(df[df.columns[-1]])
    return {Xout: X_, yout: y_, "_history": ...}


def df2arff(input="df", output="arff", **kwargs):
    """
    >>> from idict import let, idict
    >>> d = idict.fromminiarff()
    >>> d >>= let(df2arff, output="a")
    >>> d.show(colored=False)
    {
        "a": "→(input output df)",
        "_history": "idict---------arff2pandas-1.0.1--df2arff",
        "df": "«{'attr1@REAL': {0: 5.1, 1: 3.1}, 'attr2@REAL': {0: 3.5, 1: 4.5}, 'class@{0,1}': {0: '0', 1: '1'}}»",
        "_id": "Ojq9k7ZSbVjwLGlZ7uuqIyhoJPo.p36mAmav2Wul",
        "_ids": {
            "a": "pO.BtCjXeyhjKdlZ3GwdvyrYWGXEAQb9ZijWnFXj",
            "_history": "ZjxJ2WWJn82el.kX9ojvWDavSV8mReWcD3TAGgz1",
            "df": "q3_b71eb05c4be05eba7b6ae5a9245d5dd70b81b (content: 6X_dc8ccea3b2e46f1c78967fae98b692701dc99)"
        }
    }
    >>> d.a
    '@RELATION data\\n\\n@ATTRIBUTE attr1 REAL\\n@ATTRIBUTE attr2 REAL\\n@ATTRIBUTE class {0, 1}\\n\\n@DATA\\n5.1,3.5,0\\n3.1,4.5,1\\n'
    """
    from arff2pandas import a2p

    return {output: a2p.dumps(kwargs[input]), "_history": ...}


def openml(Xout="X", yout="y", name="iris", version=1):
    """
    >>> from idict import Ø
    >>> (Ø >> openml).show(colored=False)
    {
        "X": "→(Xout yout name version)",
        "y": "→(Xout yout name version)",
        "_history": "idict--------------sklearn-1.0.1--openml",
        "_id": "idict--------------sklearn-1.0.1--openml",
        "_ids": {
            "X": "KkSoAvgPmGq52PvPBqGFCEp9cSUCfb7eht9VpUdr",
            "y": "aUvIFn8094CRcfDRzrN1mjxEdkYnbBAiLiOUicIs",
            "_history": "miMBPEskz2sHRJKKHQVb1tnaOGFRtnjxZGYCxist"
        }
    }
    >>> (Ø >> openml).X.head()
       sepallength  sepalwidth  petallength  petalwidth
    0          5.1         3.5          1.4         0.2
    1          4.9         3.0          1.4         0.2
    2          4.7         3.2          1.3         0.2
    3          4.6         3.1          1.5         0.2
    4          5.0         3.6          1.4         0.2
    >>> (Ø >> openml).y.head()
    0    Iris-setosa
    1    Iris-setosa
    2    Iris-setosa
    3    Iris-setosa
    4    Iris-setosa
    Name: class, dtype: category
    Categories (3, object): ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica']
    """
    from sklearn.datasets import fetch_openml

    X, y = fetch_openml(name=name, version=version, as_frame=True, return_X_y=True)
    return {Xout: X, yout: y, "_history": ...}


def arff2df(input="arff", output="df", **kwargs):
    r"""
    >>> from idict import let, idict
    >>> d = idict.fromminiarff(output=["arff"], output_format="arff")
    >>> d.arff
    '@RELATION mini\n@ATTRIBUTE attr1\tREAL\n@ATTRIBUTE attr2 \tREAL\n@ATTRIBUTE class \t{0,1}\n@DATA\n5.1,3.5,0\n3.1,4.5,1'
    >>> d >>= arff2df
    >>> d.show(colored=False)  # doctest:+ELLIPSIS
    {
        "df": "→(input output arff)",
        "_name": "→(input output arff)",
        "_history": "idict---------arff2pandas-1.0.1--arff2df",
        "arff": "@RELATION mini\n@ATTRIBUTE attr1\tREAL\n@ATTRIBUTE attr2 \tREAL\n@ATTRIBUTE class \t{0,1}\n@DATA\n5.1,3.5,0\n3.1,4.5,1",
        "_id": "XraBH1sOCC.9ohqV3hfIRTE5FV3.0.1--arff2df",
        "_ids": {
            "df": "GCkwy4oI.s5m.pFcLGaH8kpw-djkkfftwsc5Hdj5",
            "_name": "K4gZ2YDXBHOHwPzYufHChxkfhSz7ZAr--YbuHM-o",
            "_history": ".27HRUkG1mSTh3YQOzye1BN4UoUlFhnyvdyHU3XM",
            "arff": "Z._c3e2b235b697e9734b9ec13084129dc30e45b (content: Ev_8bb973161e5ae900c5743b3c332b4a64d1955)"
        }
    }
    >>> d.name
    'mini'
    >>> d.df
       attr1@REAL  attr2@REAL class@{0,1}
    0         5.1         3.5           0
    1         3.1         4.5           1
    """
    from arff2pandas import a2p

    relation = "<Unnamed>"
    with StringIO() as f:
        f.write(kwargs[input])
        text = f.getvalue()
        df = a2p.loads(text)
        for line in isplit(text, "\n"):
            if line[:9].upper() == "@RELATION":
                relation = line[9:].strip()
                break

    return {output: df, "_name": relation, "_history": ...}


Xy2M.metadata = {
    "id": "idict--pandas-1.3.4--sklearn-1.0.1--Xy2M",
    "name": "Xy2M",
    "description": "X,y (pandas/numpy) to M (numpy) column concatenator.",
    "parameters": ...,
    "code": ...,
}
df2Xy.metadata = {
    "id": "idict-pandas-1.3.4--sklearn-1.0.1--df2Xy",
    "name": "df2Xy",
    "description": "DataFrame (pandas) to X,y (pandas) converter.",
    "parameters": ...,
    "code": ...,
}
df2arff.metadata = {
    "id": "idict---------arff2pandas-1.0.1--df2arff",
    "name": "df2arff",
    "description": "DataFrame (pandas) to ARFF converter.",
    "parameters": ...,
    "code": ...,
}
openml.metadata = {
    "id": "idict--------------sklearn-1.0.1--openml",
    "name": "openml",
    "description": "Fetch DataFrame+Series (pandas) from OpenML.",
    "parameters": ...,
    "code": ...,
}
arff2df.metadata = {
    "id": "idict---------arff2pandas-1.0.1--arff2df",
    "name": "arff2df",
    "description": "ARFF to DataFrame (pandas) converter.",
    "parameters": ...,
    "code": ...,
}
