"""Create tables from data-objects"""
# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from itertools import zip_longest
from operator import itemgetter
import re
from typing import Callable, Sequence, Union
from warnings import warn

import numpy as np

from . import fmtxt
from ._celltable import Celltable
from ._exceptions import KeysMissing
from ._data_obj import (
    CategorialArg, CellArg, IndexArg, VarArg,
    Categorial, Dataset, Factor, Interaction, NDVar, Scalar, UTS,
    Var, ascategorial, as_legal_dataset_key, asndvar, asvar, assub, asuv,
    cellname, combine, isuv)


def difference(
        y: Union[NDVar, VarArg],
        x: CategorialArg,
        c1: CellArg,
        c0: CellArg,
        match: CategorialArg,
        sub: IndexArg = None,
        ds: Dataset = None,
) -> Dataset:
    """Subtract data in one cell from another

    Parameters
    ----------
    y
        Dependent variable.
    x
        Model for subtraction, providing categories to compute ``c1 - c0``.
    c1
        Name of the cell in ``x`` that forms the minuend.
    c0
        Name of the cell in ``x`` that is to be subtracted from ``c1``.
    match
        Units over which measurements were repeated. ``c1 - c0`` will be
        calculated separately for each level of ``match`` (e.g. ``"subject"``,
        or ``"subject % condition"``).
    sub
        Only include a subset of the data.
    ds
        If a Dataset is specified other arguments can be str instead of
        data-objects and will be retrieved from ``ds``.

    Returns
    -------
    diff
        Dataset with the difference between ``c1`` and ``c0`` on ``y``.

    Examples
    --------
    ERP difference wave: assuming a dataset ``ds`` with EEG data
    (``ds['eeg']``), a variable named ``'condition'`` with levels ``'expected'``
    and ``'unexpected'``, and multiple subjects, the following will generate the
    ``unexpected - expected`` difference waves::

        >>> diff = table.difference('eeg', 'condition', 'unexpected', 'expected',
        ... 'subject', ds=ds)

    If ``ds`` also contains a different factor crossed with ``condition``,
    called ``'word'`` with levels ``'verb'`` abd ``'adjective'``, then separate
    difference waves for verbs and adjectives can be computed with::

        >>> diff = table.difference('eeg', 'condition', 'unexpected', 'expected',
        ... 'subject % word', ds=ds)

    Given the latter, the difference of the difference waves could be computed
    with::

        >>> diffdiff = table.difference('eeg', 'word', 'verb', 'adjective',
        ... 'subject', ds=diff)

    """
    ct = Celltable(y, x, match, sub, (c1, c0), ds=ds)
    if not ct.all_within:
        raise ValueError("Design is not fully balanced")
    out = Dataset()
    groups = ct.groups[c1]
    if isinstance(groups, Interaction):
        for x in groups.base:
            out.add(x)
    else:
        out.add(groups)
    yname = y if isinstance(y, str) else ct.y.name
    out[yname] = ct.data[c1] - ct.data[c0]
    # Transfer other variables in ds that are compatible with the rm-structure
    if ds is not None:
        out.update(ct._align_ds(ds, True, out.keys(), isuv))
    return out


def frequencies(y, x=None, of=None, sub=None, ds=None):
    """Calculate frequency of occurrence of the categories in ``y``

    Parameters
    ----------
    y : univariate
        Values whose frequencies are of interest.
    x : categorial
        Optional model defining cells for which frequencies are displayed
        separately.
    of : categorial
        With ``x`` constant within ``of``, only count frequencies for each value
        in ``of`` once. (Compress y and x before calculating frequencies.)
    sub : index
        Only use a subset of the data.
    ds : Dataset
        If ds is specified, other parameters can be strings naming for
        variables in ``ds``.

    Returns
    -------
    freq : Dataset
        Dataset with frequencies.

    Examples
    --------
    A simple sample dataset::

        >>> ds = Dataset()
        >>> ds['a'] = Factor('aabbcc')
        >>> ds['x'] = Factor('xxxyyy')

    Display frequency of a single factor's cells::

        >>> print(table.frequencies('a', ds=ds))
        cell   n
        --------
        a      2
        b      2
        c      2

    Display frequency of interaction cells::

        >>> print(table.frequencies('a', 'x', ds=ds))
        x   a   b   c
        -------------
        x   2   1   0
        y   0   1   2

    """
    sub = assub(sub, ds)
    y = asuv(y, sub, ds, interaction=True)
    if x is not None:
        x = ascategorial(x, sub, ds)
    if of is not None:
        of = ascategorial(of, sub, ds)
        y = y.aggregate(of)
        if x is not None:
            x = x.aggregate(of)

    name = f"Frequencies of {y.name}" if y.name else "Frequencies"
    if isinstance(y, Var):
        cells = np.unique(y.x)
    else:
        cells = y.cells

    # special case
    if x is None:
        out = Dataset(name=name)
        if isinstance(y, Interaction):
            for i, f in enumerate(y.base):
                out[f.name] = Factor((c[i] for c in x.cells),
                                     random=getattr(f, 'random', False))
        elif isinstance(y, Factor):
            out[y.name or 'y'] = Factor(cells, random=y.random)
        elif isinstance(y, Var):
            out[y.name or 'y'] = Var(cells)
        else:
            raise RuntimeError("y=%r" % (y,))
        n = np.fromiter((np.sum(y == cell) for cell in cells), int, len(cells))
        n_underline = 0
        while (key := 'n' + '_'*n_underline) in out:
            n_underline += 1
        out[key] = Var(n)
        return out

    # header
    if getattr(x, 'name', None):
        name += f' by {x.name}'
    out = Dataset(name=name)

    if isinstance(x, Interaction):
        for i, f in enumerate(x.base):
            random = getattr(f, 'random', False)
            out[f.name] = Factor((c[i] for c in x.cells), random=random)
    else:
        out[x.name] = Factor(x.cells)

    y_idx = {cell: y == cell for cell in cells}
    x_idx = {cell: x == cell for cell in x.cells}
    for y_cell in cells:
        n = (np.sum(np.logical_and(y_idx[y_cell], x_idx[x_cell]))
             for x_cell in x.cells)
        name = as_legal_dataset_key(cellname(y_cell, '_'))
        out[name] = Var(np.fromiter(n, int, len(x.cells)))

    return out


def melt(name, cells, cell_var_name, ds, labels=None):
    """
    Restructure a Dataset such that a measured variable is in a single column

    Restructure a Dataset with a certain variable represented in several
    columns into a longer dataset in which the variable is represented in a
    single column along with an identifying variable.

    Additional variables are automatically included.

    Parameters
    ----------
    name : str
        Name of the variable in the new Dataset.
    cells : sequence of str | str
        Names of the columns representing the variable in the input Dataset.
        Names can either pe specified explicitly as a sequence of str, or
        implicitly as a str containing '%i' for an integer.
    cell_var_name : str
        Name of the variable to contain the cell identifier.
    ds : Dataset
        Input Dataset.
    labels : dict | sequence of str
        Labels for the keys in ``cells``. Can be specified either as a
        ``{key: label}`` dictionary or as a list of :class:`str` corresponding
        to ``cells``.

    Examples
    --------
    Simple example data::

        >>> ds = Dataset()
        >>> ds['y1'] = Var([1, 2, 3])
        >>> ds['y2'] = Var([4, 5, 6])
        >>> print(ds)
        y1   y2
        -------
        1    4
        2    5
        3    6
        >>> print(table.melt('y', ['y1', 'y2'], 'id', ds))
        y   id
        ------
        1   y1
        2   y1
        3   y1
        4   y2
        5   y2
        6   y2

    Additional variables are automatically included::

        >>> ds['rm'] = Factor('abc')
        >>> print(ds)
        y1   y2   rm
        ------------
        1    4    a
        2    5    b
        3    6    c
        >>> print(table.melt('y', ['y1', 'y2'], 'id', ds))
        rm   y   id
        -----------
        a    1   y1
        b    2   y1
        c    3   y1
        a    4   y2
        b    5   y2
        c    6   y2

    """
    # find source cells
    if isinstance(cells, str):
        cell_expression = cells
        cells = []
        cell_values = []
        if '%i' in cell_expression:
            pattern = cell_expression.replace('%i', r'(\d+)')
            for key in ds:
                m = re.match(pattern, key)
                if m:
                    cells.append(key)
                    cell_values.append(int(m.group(1)))
        else:
            raise ValueError(f"cells={cells!r}; If specified as string, it needs to contain '%i' as a place-holder for an integer that identifies columns")
    else:
        cell_values = cells

    if labels is None:
        cell_labels = cell_values
    elif isinstance(labels, dict):
        cell_labels = [labels[v] for v in cell_values]
    elif len(labels) != len(cells):
        raise ValueError(f"labels={labels!r}: needs as many entries as there are cells ({len(cells)})")
    else:
        cell_labels = labels

    # melt the Dataset
    keep = [k for k, v in ds.items() if isuv(v)]
    if keep:
        out = ds[tuple(keep)].tile(len(cells))
    else:
        out = Dataset(info=ds.info)
    out[name] = combine(ds[cell] for cell in cells)
    out[cell_var_name] = Factor(cell_labels, repeat=ds.n_cases)
    return out


def melt_ndvar(ndvar, dim=None, cells=None, ds=None, varname=None, labels=None):
    """
    Transform data to long format by converting an NDVar dimension into a variable

    Parameters
    ----------
    ndvar : NDVar | str
        The NDVar (or name of the NDVar in ``ds``).
    dim : str
        The name of the dimension that should be unwrapped (optional if
        ``ndvar`` has only one non-case dimension).
    cells : sequence
        The values on ``dim`` that should be included in the output Dataset
        (default is to include all values).
    ds : Dataset
        Dataset with additional variables that should be included in the long
        table.
    varname : str
        Name for the transformed ``ndvar`` (default is ``ndvar.name``).
    labels: dict | callable
        Mapping or function to create labels for ``dim`` levels.

    Returns
    -------
    long_table : Dataset
        Dataset in long format.

    See Also
    --------
    cast_to_ndvar

    Examples
    --------
    See :ref:`exa-compare-topographies`.
    """
    ndvar = asndvar(ndvar, ds=ds)
    if dim is None:
        if ndvar.ndim == ndvar.has_case + 1:
            dim = ndvar.dims[-1]
            dimname = dim.name
        else:
            raise ValueError(f"The ndvar has more than one possible dimensions, the dim parameter must be one of {ndvar.dimnames[ndvar.has_case:]}")
    else:
        dimname = dim
        dim = ndvar.get_dim(dimname)

    dim_vars = dim._melt_vars()
    if cells is None:
        cells = dim._as_uv()
    elif dim_vars:
        index = dim._array_index(cells)
        dim_vars = {k: v[index] for k, v in dim_vars.items()}

    if callable(labels):
        label = labels
    elif isinstance(labels, dict):
        missing = set(cells).difference(labels)
        if missing:
            raise KeysMissing(missing, 'labels', labels)
        label = itemgetter(labels)
    elif labels is None:
        label = lambda x: x
    else:
        raise TypeError(f"labels={labels!r}")

    if varname is None:
        if ndvar.name is None:
            raise TypeError("Need to provide a name")
        varname = ndvar.name

    if ds is None:
        base_ds = Dataset()
    else:
        uv_keys = tuple(k for k, v in ds.items() if isuv(v))
        base_ds = ds[uv_keys]

    if not ndvar.has_case:
        ndvar = ndvar[np.newaxis]
    dss = []
    for cell in cells:
        ds_ = base_ds.copy()
        ds_[varname] = ndvar.sub(**{dimname: cell})
        ds_[dimname, :] = label(cell)
        dss.append(ds_)
    out = combine(dss)
    for k, v in dim_vars.items():
        if k not in out:
            out[k] = v.repeat(len(ndvar))
    return out


def cast_to_ndvar(
        data: Union[VarArg, Sequence[VarArg]],
        dim_values: Union[VarArg, Factor],
        match: CategorialArg,
        sub: IndexArg = None,
        ds: Dataset = None,
        dim: str = None,
        unit: str = 's',
        name: str = None,
) -> Dataset:
    """Create an NDVar by converting a data column to a dimension
    
    Parameters
    ----------
    data
        Data to be cast.
    dim_values
        Location on the new dimension.
    match
        Indicating rows which belong the the same case in the NDvar.
    sub
        Use a subset of the data.
    ds
        Dataset with data for operation.
    dim
        Name for the new dimension. Use ``dim='uts'`` to create :class:`UTS` 
        time dimension from scalar ``dim_values``.
    unit
        Unit for :class:`UTS` dimension (ignored otherwise).
    name
        Name for the new :class:`NDVar` (the default is the name of ``data``).
        
    Returns
    -------
    short_ds
        Copy of ``ds``, aggregated over ``dim_values``, and with an 
        :class:`NDVar` containing the values form ``data`` and a new dimension
        reflecting ``dim_values``. If ``dim_values`` is a Factor, the new 
        dimension is :class:`Categorial`; if ``dim_values`` is a :class:`Var`, 
        it is :class:`Scalar`. The new dimension's name is ``dim``. The only
        exception to this is that when ``dim='uts'``, the new dimension is 
        :class:`UTS` named ``'time'``.

    See Also
    --------
    melt_ndvar
    """
    sub, n = assub(sub, ds, return_n=True)
    if isinstance(data, (str, Var)):
        data, n = asvar(data, sub, ds, n, return_n=True)
        data_vars = [data]
        names = [name]
    else:
        data_vars = []
        for data_i in data:
            data_var, n = asvar(data_i, sub, ds, n, return_n=True)
            data_vars.append(data_var)
        if name is None:
            names = [None for _ in range(len(data_vars))]
        elif isinstance(name, str):
            raise TypeError(f"name={name!r}: single name for multiple variables")
        else:
            names = name
    dim_values, n = asuv(dim_values, sub, ds, n, return_n=True)
    match, n = ascategorial(match, sub, ds, n, return_n=True)

    # determine NDVar dimension
    if isinstance(dim_values, Factor):
        unique_dim_values = dim_values.cells
        dim = Categorial(dim or dim_values.name, unique_dim_values)
    else:
        unique_dim_values = np.unique(dim_values.x)
        if dim == 'uts':
            diff = np.diff(unique_dim_values)
            unique_diff = np.unique(diff)
            if len(unique_diff) > 1:
                if np.diff(unique_diff).max() > 1e-15:
                    raise NotImplementedError(f"Can't create UTS dimension from data with irregular sampling (detected time-steps of {', '.join(map(str, unique_diff))}")
                tstep = round(unique_diff.mean(), 17)
            else:
                tstep = unique_diff[0]
            dim = UTS(unique_dim_values[0], tstep, len(unique_dim_values), unit)
        else:
            dim = Scalar(dim or dim_values.name, unique_dim_values)

    # find NDVar data
    n_samples = len(dim)
    n_cases = len(match.cells)
    case_indexes = [match == case for case in match.cells]
    samples_indexes = [dim_values == v for v in unique_dim_values]
    xs = [np.empty((n_cases, n_samples)) for _ in data_vars]
    index = None
    for i, case_index in enumerate(case_indexes):
        try:
            for j, sample_index in enumerate(samples_indexes):
                index = np.logical_and(case_index, sample_index, out=index)
                for x, data_var in zip(xs, data_vars):
                    x[i, j] = data_var.x[index]
        except ValueError:
            if not np.any(index):
                raise ValueError(f"Case {match.cells[i]!r} is missing some values")

    # package output dataset
    if ds is None:
        out = Dataset()
    else:
        out = ds if sub is None else ds.sub(sub)
        out = out.aggregate(match, drop_bad=True, count=False)
    for x, data_var, name in zip_longest(xs, data_vars, names):
        out[name or data_var.name] = NDVar(x, ('case', dim))
    return out


def stats(
        y: Var,
        row: CategorialArg,
        col: CategorialArg = None,
        match: CategorialArg = None,
        sub: IndexArg = None,
        fmt: str = '%.4g',
        funcs: Sequence[Union[str, Callable]] = ('mean',),
        ds: Dataset = None,
        title: fmtxt.FMTextArg = None,
        caption: fmtxt.FMTextArg = None,
        format: bool = True,
) -> Union[Dataset, fmtxt.Table]:
    """Make a table with statistics

    Parameters
    ----------
    y
        Dependent variable.
    row
        Model specifying rows
    col
        Model specifying columns.
    match
        Identifier for repeated measures data; aggregate within subject before
        computing statistics.
    sub
        Only use part of the data.
    fmt
        How to format values.
    funcs
        A list of statistics functions to show (all functions must take an
        array argument and return a scalar; strings are interpreted as
        :mod:`numpy` functions).
    ds
        If a Dataset is provided, ``y``, ``row``, and ``col`` can be strings
        specifying members.
    title
        Table title.
    caption
        Table caption.
    format
        Return a formatted table (instead of a :class:`Dataset`)


    Returns
    -------
    table
        Table with statistics.

    Examples
    --------
    >>> ds = datasets.get_uts()
    >>> table.stats('Y', 'A', 'B', ds=ds)
                B
         -----------------
         b0        b1
    ----------------------
    a0   0.1668    -0.3646
    a1   -0.4897   0.8746

    >>> table.stats('Y', 'A', ds=ds, funcs=['mean', 'std'])
    Condition   Mean     Std
    --------------------------
    a0          0.6691   1.37
    a1          0.8596   1.192

    """
    sub = assub(sub, ds)
    y = asvar(y, sub, ds)
    row = ascategorial(row, sub, ds)
    if match is not None:
        match = ascategorial(match, sub, ds)

    if isinstance(funcs, str):
        funcs = [funcs]
    funcs = [getattr(np, f) if isinstance(f, str) else f for f in funcs]

    if col is None:
        ct = Celltable(y, row, match=match)
        if not format:
            out = Dataset()
            if isinstance(ct.x, Factor):
                out[ct.x.name or 'cell'] = Factor(ct.x.cells)
            elif isinstance(ct.x, Interaction):
                for i, base in enumerate(ct.x.base):
                    out[base.name or f'cell_{i}'] = Factor([cell[i] for cell in ct.x.cells])
            else:
                raise RuntimeError(f"{ct.x=}")

            for func in funcs:
                out[func.__name__] = ct.get_statistic(func)
            return out

        # table header
        n_disp = len(funcs)
        table = fmtxt.Table('l' * (n_disp + 1), title=title, caption=caption)
        table.cell('Condition', 'bf')
        for func in funcs:
            table.cell(func.__name__.capitalize(), 'bf')
        table.midrule()

        # table entries
        for cell in ct.cells:
            data = ct.data[cell]
            table.cell(cell)
            for func in funcs:
                table.cell(fmt % func(data.x))
    else:
        col = ascategorial(col, sub, ds)
        ct = Celltable(y, row % col, match=match)

        N = len(col.cells)
        if not format:
            raise NotImplementedError(f"{format=} with col specified")

        table = fmtxt.Table('l' * (N + 1), title=title, caption=caption)

        # table header
        table.cell()
        table.cell(col.name, width=N, just='c')
        table.midrule(span=(2, N + 1))
        table.cell()

        table.cells(*col.cells)
        table.midrule()

        # table body
        fmt_n = fmt.count('%')
        if fmt_n == 1:
            fmt_once = False
        elif len(funcs) == fmt_n:
            fmt_once = True
        else:
            raise ValueError("fmt does not match funcs")

        for Ycell in row.cells:
            table.cell(Ycell)
            for Xcell in col.cells:
                # construct address
                a = ()
                if isinstance(Ycell, tuple):
                    a += Ycell
                else:
                    a += (Ycell,)
                if isinstance(Xcell, tuple):
                    a += Xcell
                else:
                    a += (Xcell,)

                # cell
                data = ct.data[a]
                values = (f(data.x) for f in funcs)
                if fmt_once:
                    txt = fmt % values
                else:
                    txt = ', '.join((fmt % v for v in values))

                table.cell(txt)

    return table


def repmeas(y, x, match, sub=None, ds=None):
    """Create a repeated-measures table

    Parameters
    ----------
    y :
        Dependent variable (can be model with several dependents).
    x : categorial
        Model defining the cells that should be restructured into variables.
    match : categorial
        Model identifying the source of the measurement across repetitions,
        i.e. the model that should be retained.
    sub :
        boolean array specifying which values to include (generate e.g.
        with 'sub=T==[1,2]')
    ds : Dataset
        If a Dataset is specified other arguments can be str instead of
        data-objects and will be retrieved from ds.

    Returns
    -------
    rm_table : Dataset
        Repeated measures table. Entries for cells of ``x`` correspond to the
        data in ``y`` on these levels of ``x`` (if cell names are not valid
        Dataset keys they are modified).

    Examples
    --------
    Generate test data in long format::

        >>> ds = Dataset()
        >>> ds['y'] = Var([1,2,3,5,6,4])
        >>> ds['x'] = Factor('aaabbb')
        >>> ds['rm'] = Factor('123231', random=True)
        >>> print(ds)
        y   x   rm
        ----------
        1   a   1
        2   a   2
        3   a   3
        5   b   2
        6   b   3
        4   b   1

    Compute difference between two conditions::

        >>> ds_rm = table.repmeas('y', 'x', 'rm', ds=ds)
        >>> print(ds_rm)
        rm   a   b
        ----------
        1    1   4
        2    2   5
        3    3   6
        >>> ds_rm['difference'] = ds_rm.eval("b - a")
        >>> print(ds_rm)
        rm   a   b   difference
        -----------------------
        1    1   4   3
        2    2   5   3
        3    3   6   3

    """
    ct = Celltable(y, x, match, sub, ds=ds)
    if not ct.all_within:
        raise ValueError("Incomplete data")

    out = Dataset()
    x_ = ct.groups[ct.x.cells[0]]
    if isinstance(x_, Interaction):
        for f in x_.base:
            out.add(f)
    else:
        out[ct.match.name] = x_

    for cell in ct.x.cells:
        if len(ct.data[cell]):  # for models with empty cells
            key = as_legal_dataset_key(cellname(cell, '_'))
            out[key] = ct.data[cell]

    # Transfer other variables in ds that are compatible with the rm-structure
    if ds is not None:
        out.update(ct._align_ds(ds, True, out.keys(), isuv))

    return out
