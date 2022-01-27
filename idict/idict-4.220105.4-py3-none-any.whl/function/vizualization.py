from itertools import repeat

from idict.macro import isnumber


def X2histogram(col=0, input="X", output="histogram", bins=8, **kwargs):
    """
    >>> import numpy as np
    >>> from idict import let
    >>> X = np.array([["a", 2.1, 1.6], ["a", 3, 2], ["b", 7, 3]])
    >>> X2histogram(X=X, col=1, bins=2)
    {'histogram': [{'x': '(2.095, 4.55]', 'count': 2}, {'x': '(4.55, 7.0]', 'count': 1}], '_history': Ellipsis}
    >>> from idict import idict
    >>> from idict.function.dataset import df2Xy
    >>> d = idict.fromtoy(output_format="df") >> df2Xy >> X2histogram
    >>> d.histogram
    [{'x': '(0.069, 3.975]', 'count': 11}, {'x': '(3.975, 7.85]', 'count': 5}, {'x': '(7.85, 11.725]', 'count': 3}, {'x': '(11.725, 15.6]', 'count': 0}, {'x': '(15.6, 19.475]', 'count': 0}, {'x': '(19.475, 23.35]', 'count': 0}, {'x': '(23.35, 27.225]', 'count': 0}, {'x': '(27.225, 31.1]', 'count': 1}]
    """
    import numpy as np
    import pandas

    X = kwargs[input]
    vals = X.iloc[:, col] if hasattr(X, "iloc") else X[:, col]
    if isnumber(vals[0]):
        cut = pandas.cut(np.array(list(map(float, vals))), bins, duplicates="drop")
        df = pandas.DataFrame(cut)
        df2 = df.groupby(cut).count()
        dic = df2.to_dict()[0]
    else:
        from pandas import Series

        dic = Series(vals).value_counts()
    result = [{"x": str(k), "count": v} for k, v in dic.items()]
    return {output: result, "_history": ...}


def tofloat(X, k, col):
    if hasattr(X, "iloc"):
        X = X.iloc
    val = X[k, col]
    try:
        return float(val)
    except ValueError:
        return float(list(X[:, col]).index(val))
    except TypeError:
        print(
            f"Warning: Wrong type {type(val)} converted to zero. Look for '?' characters if you provided an ARFF file."
        )
        return 0


def Xy2scatterplot(colx=0, coly=1, Xin="X", yin="y", output="scatterplot", **kwargs):
    """
    >>> import numpy as np
    >>> X = np.array([["c1", 2.1, 1.6], ["c2", 3.2, 2.3], ["c3", 7, 3]])
    >>> y = np.array(["a", "b", "c"])
    >>> Xy2scatterplot(X=X, y=y, colx=1, coly=2)
    {'scatterplot': [{'id': 'a', 'data': [{'x': 2.1, 'y': 1.6}]}, {'id': 'b', 'data': [{'x': 3.2, 'y': 2.3}]}, {'id': 'c', 'data': [{'x': 7.0, 'y': 3.0}]}], '_history': Ellipsis}
    >>> Xy2scatterplot(X=X, y=y, colx=1, coly=0)
    {'scatterplot': [{'id': 'a', 'data': [{'x': 2.1, 'y': 0.0}]}, {'id': 'b', 'data': [{'x': 3.2, 'y': 1.0}]}, {'id': 'c', 'data': [{'x': 7.0, 'y': 2.0}]}], '_history': Ellipsis}
    >>> from idict import idict
    >>> from idict.function.dataset import df2Xy
    >>> d = idict.fromtoy(output_format="df") >> df2Xy >> Xy2scatterplot
    >>> d.scatterplot
    [{'id': '0', 'data': [{'x': 5.1, 'y': 6.4}, {'x': 6.1, 'y': 3.6}, {'x': 3.1, 'y': 2.5}, {'x': 9.1, 'y': 3.5}, {'x': 9.1, 'y': 7.2}, {'x': 7.1, 'y': 6.6}, {'x': 2.1, 'y': 0.1}, {'x': 5.1, 'y': 4.5}, {'x': 1.1, 'y': 3.2}, {'x': 3.1, 'y': 2.5}]}, {'id': '1', 'data': [{'x': 1.1, 'y': 2.5}, {'x': 1.1, 'y': 3.5}, {'x': 4.7, 'y': 4.9}, {'x': 8.3, 'y': 2.9}, {'x': 2.5, 'y': 4.5}, {'x': 0.1, 'y': 4.3}, {'x': 0.1, 'y': 4.0}, {'x': 31.1, 'y': 4.7}, {'x': 2.2, 'y': 8.5}, {'x': 1.1, 'y': 8.5}]}]
    """
    X = kwargs[Xin]
    y = kwargs[yin]
    result = []
    for m in dict(zip(y, repeat(None))):
        inner = []
        for k in range(len(X)):
            left = m if isinstance(m, str) else str(float(m))
            if isinstance(y[k], str):
                right = y[k]
            else:
                right = str(float(y[k]))
            if left == right:
                x_ = tofloat(X, k, colx)
                y_ = tofloat(X, k, coly)
                inner.append({"x": x_, "y": y_})
        result.append({"id": str(m), "data": inner})
    return {output: result, "_history": ...}


X2histogram.metadata = {
    "id": "-----------------------------X2histogram",
    "name": "X2histogram",
    "description": "Generate a histogram for the specified column of a field.",
    "parameters": ...,
    "code": ...,
}
Xy2scatterplot.metadata = {
    "id": "--------------------------Xy2scatterplot",
    "name": "Xy2scatterplot",
    "description": "Generate a scatterplot for the specified two columns of a field.",
    "parameters": ...,
    "code": ...,
}
