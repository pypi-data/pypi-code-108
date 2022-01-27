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


def fit(algorithm=None, config={}, Xin="X", yin="y", output="model", version=0, **kwargs):
    """
    >>> from sklearn.ensemble import RandomForestClassifier as RF
    >>> from idict import idict, let
    >>> d = idict.fromtoy() >> let(fit, algorithm=RF)
    >>> d.model
    RandomForestClassifier()
    >>> d >>= predict
    >>> d.z
    array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1])
    """
    obj = algorithm(**config)
    obj.fit(kwargs[Xin], kwargs[yin])
    return {output: obj, "_history": ...}


def predict(input="model", Xin="X", yout="z", version=0, **kwargs):
    return {yout: kwargs[input].predict(kwargs[Xin]), "_history": ...}


# TODO these functions are just drafts
def transform(input="model", Xin="X", yin="y", Xout="X", yout="y", version=0, **kwargs):
    return {yout: kwargs[input].transform(kwargs[Xin]), "_history": ...}


def use(input="model", Xin="X", yin="y", Xout="X", yout="y", version=0, **kwargs):
    if hasattr(kwargs[input], "predict"):
        r = kwargs[Xin], kwargs[input].predict(kwargs[Xin])
    elif hasattr(kwargs[input], "transform"):
        r = kwargs[input].transform(kwargs[Xin])
    elif hasattr(kwargs[input], "sample"):
        r = kwargs[input].sample(kwargs[Xin])
    elif hasattr(kwargs[input], "resample"):
        r = kwargs[input].resample(kwargs[Xin])
    else:
        raise Exception("Cannot detect how to use this model.")
    if len(r) == 1:
        X, y = r, None
    else:
        X, y = r
    return {Xout: X, yout: y, "_history": ...}


fit.metadata = {
    "id": "idict-----------------------wrapper--fit",
    "name": "fit",
    "description": "Induce a model.",
    "parameters": ...,
    "code": ...,
}
predict.metadata = {
    "id": "idict-------------------wrapper--predict",
    "name": "predict",
    "description": "Predict values according to a model.",
    "parameters": ...,
    "code": ...,
}
transform.metadata = {
    "id": "idict-----------------wrapper--transform",
    "name": "transform",
    "description": "Transform values according to a model.",
    "parameters": ...,
    "code": ...,
}
use.metadata = {
    "id": "idict-----------------------wrapper--use",
    "name": "use",
    "description": "Use (predict, transform, [re]sample) values according to a model.",
    "parameters": ...,
    "code": ...,
}
