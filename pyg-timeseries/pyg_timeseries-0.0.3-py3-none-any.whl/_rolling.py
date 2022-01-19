import numpy as np
from pyg_timeseries._math import stdev_calculation, skew_calculation
from pyg_timeseries._decorators import compiled, first_, _data_state
from pyg_base import pd2np, Dict, is_num, loop_all, loop, clock

__all__ = ['ffill', 'bfill', 'fnna', 'na2v', 'v2na', 'diff', 'shift', 'ratio', 'rolling_mean', 'rolling_sum', 'rolling_rms', 'rolling_std', 'rolling_skew', 
           'diff_', 'shift_', 'ratio_', 'rolling_mean_', 'rolling_sum_', 'rolling_rms_', 'rolling_std_', 'rolling_skew_']

###############
##
## parameters
##
###############
    
@loop(list, dict)
def _vec(vec, n, value = np.nan):
    if vec is None:
        vec = np.full(abs(n), value)
    elif is_num(vec):
        vec = np.array([vec])
    return vec.copy()

@loop_all
@pd2np
@compiled
def _fnna(a, n):
    if n == 0:
        raise ValueError('n must be non-zero')
    i = 0
    _n = abs(n)
    s = (0,a.shape[0],1) if n>0 else (a.shape[0]-1,-1,-1)
    for j in range(*s):
        if not np.isnan(a[j]):
            i = i+1
            if i == _n:
                return j
            

@compiled
def _ffill1d(a, n, prev, i):
    res = a.copy()
    for j in range(a.shape[0]):
        if np.isnan(a[j]):
            if n == 0:
                res[j] = prev
            else:
                i+=1
                if i>n:
                    res[j] = np.nan
                else:
                    res[j] = prev
        else:
            i = 0
            prev = a[j]
    return res, prev, i


def _ffill2d(a, n, prev, i):
    res = a.copy()
    if n:
        for j in range(a.shape[0]):
            mask = np.isnan(res[j])
            i[mask]+=1
            i[~mask] = 0
            prev[i>n] = np.nan
            res[j][mask] = prev[mask]
            prev = res[j].copy()
    else:
        for j in range(a.shape[0]):
            mask = np.isnan(res[j])
            res[j][mask] = prev[mask]
            prev = res[j]
    return res, prev, i

@loop(dict, list)
@pd2np
def _ffill(a, n = 0, prev = None, i = None):
    if len(a.shape) == 1:
        if i is None:
            i = 0
        if prev is None:
            prev = np.nan
        return _ffill1d(a, n, prev , i)
    else:            
        if i is None:
            i = np.zeros(a[0].shape)
        if prev is None:
            prev = i + np.nan
        return _ffill2d(a, n, prev , i)


@loop_all
@pd2np
@compiled
def _na2v(a, new = 0.0):
    res = a.copy()
    for j in range(a.shape[0]):
        if np.isnan(a[j]):
            res[j] = new
    return res

@loop_all
@pd2np
@compiled
def _v2na(a, old = 0.0, new = np.nan):
    res = a.copy()
    for j in range(a.shape[0]):
        if a[j] == old:
            res[j] = new
    return res


@loop_all
@pd2np
@compiled
def _init2v(a, n = 0, new = np.nan):
    res = a.copy()
    i = 0
    while i < a.shape[0] and n > 0:
        if ~np.isnan(a[i]):
            res[i] = new
            n = n-1
        i+=1
    return res


@loop_all
@pd2np
@compiled
def _bfill(a, limit = -1):
    """
    _bfill(np.array([np.nan, 1., np.nan])) 
    """
    res = a.copy()
    prev = np.nan
    n = limit
    for j in range(a.shape[0]-1, -1, -1):
        if np.isnan(a[j]):
            if n!=0:
                n-=1
                res[j] = prev
        else:
            n = limit
            prev = res[j]
    return res


###############
##
## bottleneck
##
###############

@loop_all
@pd2np
def _rolling_window(a, window, min_count, func, vec = None):
    vec = _vec(vec,0)
    mask = ~np.isnan(a)
    na = a[mask]
    n = len(na)
    if len(vec):
        na = np.concatenate([vec,na])
    w = na.shape[0] if window == 0 else window        
    res = func(na, w, min_count)
    if len(vec):
        res = res[-n:] 
    va = a.copy()
    va[mask] = res
    return va, va[-1:] if window == 0 else na[-(window-1):]


###############
##
## diff/shift/ratio
##
###############

@loop_all
@pd2np
@compiled
def _diff(a, n, vec, i):
    vec = vec.copy()
    _n = abs(n)
    s = (0,a.shape[0],1) if n>0 else (a.shape[0]-1,-1,-1)
    res = np.empty_like(a)
    for j in range(*s):
        if np.isnan(a[j]):
            res[j] = np.nan
        else:
            res[j] = a[j] - vec[i]
            vec[i] = a[j]
            i = (i+1) % _n
    return res, vec, i

@loop_all
@pd2np
@compiled
def _diff1(a, vec):
    vec = vec.copy()
    v = vec[0]
    res = np.empty_like(a)
    for j in range(a.shape[0]):
        if np.isnan(a[j]):
            res[j] = np.nan
        else:
            res[j] = a[j] - v
            v = a[j]
    vec[0] = v
    return res, vec, 0


@loop_all
@pd2np
@compiled
def _ratio(a, n, vec, i):
    vec = vec.copy()
    _n = abs(n)
    s = (0,a.shape[0],1) if n>0 else (a.shape[0]-1,-1,-1)
    res = np.empty_like(a)
    for j in range(*s):
        if np.isnan(a[j]):
            res[j] = np.nan
        else:
            res[j] = np.nan if vec[i] == 0 else a[j] / vec[i] 
            vec[i] = a[j]
            i = (i+1) % _n
    return res, vec, i

@loop_all
@pd2np
@compiled
def _shift(a, n, vec, i):
    vec = vec.copy()
    res = np.empty_like(a)
    _n = abs(n)
    s = (0,a.shape[0],1) if n>0 else (a.shape[0]-1,-1,-1)
    for j in range(*s):
        if np.isnan(a[j]):
            res[j] = np.nan
        else:
            res[j] = vec[i]
            vec[i] = a[j]
            i = (i+1) % _n
    return res, vec, i


@loop_all
@pd2np
@compiled
def _shift1(a, vec):
    vec = vec.copy()
    res = np.empty_like(a)
    for j in range(a.shape[0]):
        if np.isnan(a[j]):
            res[j] = np.nan
        else:
            res[j] = vec[0]
            vec[0] = a[j]
    return res, vec, 0


###############
##
## rolling
##
###############


@pd2np
@compiled
def _rolling_mean(a, n, time, t0, t1, vec, i, denom, t = np.nan):
    vec = vec.copy()
    res = np.empty_like(a)
    _n = abs(n)
    s = (0,a.shape[0],1) if n>0 else (a.shape[0]-1,-1,-1)
    for j in range(*s):
        if np.isnan(a[j]):
            res[j] = np.nan
        else:
            if not (time[j] == t):
                i = (i+1) % _n
                t0 +=1
            t1 += a[j]-vec[i]
            vec[i] = a[j]
            res[j] = np.nan if t0<n else t1/denom
            t = time[j]
    return res, t0, t1, vec, i, t


@loop_all
def _trolling_mean(a, n, t0, t1, vec, i, denom, t = np.nan, time = None):
    time = clock(a, time, t)
    return _rolling_mean(a, n, time = time, t = t, t0 = t0, t1 = t1, vec = vec, i = i, denom = denom)


@pd2np
@compiled
def _rolling_rms(a, n, time, t0, t2, vec, i, denom, t = np.nan):
    vec = vec.copy()
    res = np.empty_like(a)
    _n = abs(n)
    s = (0,a.shape[0],1) if n>0 else (a.shape[0]-1,-1,-1)
    for j in range(*s):
        if np.isnan(a[j]):
            res[j] = np.nan
        else:
            if not (time[j] == t):
                i = (i+1) % _n
                t0 +=1
            t2 += a[j]**2-vec[i]**2
            vec[i] = a[j]
            res[j] = np.nan if t0<n else np.sqrt(t2/denom)
            t = time[j]
    return res, t0, t2, vec, i, t

@loop_all
def _trolling_rms(a, n, t0, t2, vec, i, denom, t = np.nan, time = None):
    time = clock(a, time, t)
    return _rolling_rms(a, n, time = time, t = t, t0 = t0, t2 = t2, vec = vec, i = i, denom = denom)

@pd2np
@compiled
def _rolling_std(a, n, time, t0, t1, t2, vec, i, denom, t = np.nan):
    vec = vec.copy()
    res = np.empty_like(a)
    _n = abs(n)
    s = (0,a.shape[0],1) if n>0 else (a.shape[0]-1,-1,-1)
    for j in range(*s):
        if np.isnan(a[j]):
            res[j] = np.nan
        else:
            if not (time[j] == t):
                i = (i+1) % _n
                t0 +=1
            t1 += a[j]-vec[i]
            t2 += a[j]**2-vec[i]**2
            vec[i] = a[j]
            res[j] = np.nan if t0<n else stdev_calculation(t0 = n, t1 = t1, t2 = t2)
            t = time[j]
    return res, t0, t1, t2, vec, i, t

@loop_all
def _trolling_std(a, n, t0, t1, t2, vec, i, denom, t = np.nan, time = None):
    time = clock(a, time, t)
    return _rolling_std(a, n, time = time, t = t, t0 = t0, t1 = t1, t2 = t2, vec = vec, i = i, denom = denom)


@pd2np
@compiled
def _rolling_skew(a, n, time, bias, t0, t1, t2, t3, vec, i, denom, t = np.nan):
    vec = vec.copy()
    res = np.empty_like(a)
    _n = abs(n)
    s = (0,a.shape[0],1) if n>0 else (a.shape[0]-1,-1,-1)
    for j in range(*s):
        if np.isnan(a[j]):
            res[j] = np.nan
        else:
            if not (time[j] == t):
                i = (i+1) % _n
                t0 +=1
            t1 += a[j]-vec[i]
            t2 += a[j]**2-vec[i]**2
            t3 += a[j]**3-vec[i]**3
            vec[i] = a[j]
            res[j] = np.nan if t0<_n else skew_calculation(t0 = _n, t1 = t1, t2 = t2, t3 = t3, bias = bias, min_sample = 1)
            t = time[j]
    return res, t0, t1, t2, t3, vec, i, t


@loop_all
def _trolling_skew(a, n, t0, t1, t2, t3, vec, i, denom, bias = False, t = np.nan, time = None):
    time = clock(a, time, t)
    return _rolling_skew(a, n = n, time = time, bias = bias, t = t, t0 = t0, t1 = t1, t2 = t2, t3 = t3, vec = vec, i = i, denom = denom)


###############
##
## API
##
###############


def fnna(a, n=1, axis = 0):
    """
    returns the index in a of the nth first non-nan.
    
    :Parameters:
    ------------
    a : array/timeseries
    n: int, optional, default = 1

    :Example:
    ---------
    >>> a = np.array([np.nan,np.nan,1,np.nan,np.nan,2,np.nan,np.nan,np.nan])
    >>> fnna(a,n=-2)
    
    """
    return _fnna(a, n, axis = axis)

def bfill(a, n = -1, axis = 0):
    """
    equivalent to a.fillna('bfill'). There is no state-aware as this function is forward looking

    :Example:
    -------
    >>> from pyg import *
    >>> a = np.array([np.nan, 1., np.nan])
    >>> b = np.array([1., 1., np.nan])
    >>> assert eq(bfill(a),  b)

    :Example: pd.Series
    -------
    >>> ts = pd.Series(a, drange(-2))
    >>> assert eq(bfill(ts).values, b)
    """
    return _bfill(a, limit = n, axis = axis)


def ffill(a, n=0, axis = 0, data = None, state = None):
    """
    returns a forward filled array, up to n values forward. 
    supports state manegement which is needed if we want only nth

    
    :Parameters:
    ------------
    a : array/timeseries
        array/timeseries
    n: int, optional, default = 1
        window size
    data: None.
        unused at the moment. Allow code such as func(live, **func_(history)) to work
    state: dict, optional
        state parameters used to instantiate the internal calculations, based on history prior to 'a' provided. 

    :Example:
    ---------
    >>> a = np.array([np.nan,np.nan,1,np.nan,np.nan,2,np.nan,np.nan,np.nan])
    >>> fnna(a, n=-2)
    """
    state = state or Dict(prev = None, i = None)
    return first_(_ffill(a, n=n, axis = axis, **state))

def ffill_(a, n=0, axis = 0, instate = None):
    """
    returns a forward filled array, up to n values forward. 
    supports state manegement
    
    """
    state = instate or dict(prev = None, i = None)
    return _data_state(['data', 'prev', 'i'],_ffill(a, n=n, axis = axis, **state))

ffill_.output = ['data', 'state']


def v2na(a, old = 0.0, new = np.nan):
    """
    replaces an old value with a new value (default is nan)

    :Examples:
    --------------
    >>> from pyg import *
    >>> a = np.array([1., np.nan, 1., 0.])
    >>> assert eq(v2na(a), np.array([1., np.nan, 1., np.nan]))
    >>> assert eq(v2na(a,1), np.array([np.nan, np.nan, np.nan, 0]))
    >>> assert eq(v2na(a,1,0), np.array([0., np.nan, 0., 0.]))
    
    :Parameters:
    ----------------
    a : array/timeseries
    old: float
        value to be replaced
    new : float, optional
        new value to be used, The default is np.nan.

    :Returns:
    -------
    array/timeseries

    """
    return _v2na(a, old = old, new = new)

def na2v(a, new = 0.0):
    """
    replaces a nan with a new value
    
    :Example:
    -------
    >>> from pyg import *
    >>> a = np.array([1., np.nan, 1.])
    >>> assert eq(na2v(a), np.array([1., 0.0, 1.]))
    >>> assert eq(na2v(a,1), np.array([1., 1., 1.]))
    
    :Parameters:
    ----------------
    a : array/timeseries
    new : float, optional
        DESCRIPTION. The default is 0.0.

    :Returns:
    -------
    array/timeseries

    """
    return _na2v(a, new)
    

def init2v(a, n = 0, new = np.nan):
    """
    replaces initial non-nan values with a new value. This is primarily to remove initial results of a volatile fit etc.
    
    :Example:
    -------
    >>> from pyg import *
    >>> a = np.arange(100) * 1.
    >>> assert np.sum(a[np.isnan(init2v(a,10))]) == 0+1+2+3+4+5+6+7+8+9
    
    :Parameters:
    ----------------
    a : array/timeseries
        data to be nanned
    new : float, optional
        DESCRIPTION. The default is np.nan.
    n: int
        number of entries to go to new value

    :Returns:
    -------
    array/timeseries

    """
    if n == 0:
        return a
    return _init2v(a, n, new)


def diff(a, n=1, axis = 0, data = None, state = None):
    """
    equivalent to a.diff(n) in pandas if there are no nans. If there are, we SKIP nans rather than propagate them.

    :Parameters:
    ------------
    a : array/timeseries
        array/timeseries
    n: int, optional, default = 1
        window size
    data: None.
        unused at the moment. Allow code such as func(live, **func_(history)) to work
    state: dict, optional
        state parameters used to instantiate the internal calculations, based on history prior to 'a' provided. 


    :Example: : matching pandas no nan's
    ----------------------------------------------------------
    >>> from pyg import *; import pandas as pd; import numpy as np
    >>> a = pd.Series(np.random.normal(0,1,10000), drange(-9999))
    >>> assert eq(timer(diff, 1000)(a), timer(lambda a, n=1: a.diff(n), 1000)(a))

    :Example: : nan skipping
    ----------------------------------
    >>> a = np.array([1., np.nan, 3., 9.])
    >>> assert eq(diff(a),                      np.array([np.nan, np.nan, 2.0,   6.0]))
    >>> assert eq(pd.Series(a).diff().values,   np.array([np.nan, np.nan, np.nan,6.0]))
    
    """
    if n == 0:
        return a - a
    state = state or Dict(vec = None, i = 0)
    state.vec = _vec(state.vec, n)
    return first_(_diff1(a, vec = state.vec, axis = axis) if n == 1 else _diff(a, n, axis = axis, **state))

def diff_(a, n=1, axis = 0, data = None, instate = None):
    """
    returns a forward filled array, up to n values forward. 
    Equivalent to diff(a,n) but returns the full state. See diff for full details
  
    """
    if n == 0:
        return Dict(data = a - a, state = instate)
    state = instate or Dict(vec = None, i = 0) 
    state.vec = _vec(state['vec'], n)
    return _data_state(['data', 'vec', 'i'], _diff1(a, state.vec, axis = axis) if n == 1 else _diff(a, n, axis = axis, **state))

diff_.output = ['data', 'state']
        
def shift(a, n=1, axis = 0, data = None, state = None):
    """
    Equivalent to a.shift() with support to arra
    
    :Parameters:
    ------------
    a : array, pd.Series, pd.DataFrame or list/dict of these
        timeseries
    n: int
        size of rolling window
    data: None.
        unused at the moment. Allow code such as func(live, **func_(history)) to work
    state: dict, optional
        state parameters used to instantiate the internal calculations, based on history prior to 'a' provided. 
        
    :Example:
    ---------
    >>> from pyg import *; import pandas as pd; import numpy as np
    >>> a = pd.Series([1.,2,3,4,5], drange(-4))
    >>> assert eq(shift(a), pd.Series([np.nan,1,2,3,4], drange(-4)))
    >>> assert eq(shift(a,2), pd.Series([np.nan,np.nan,1,2,3], drange(-4)))
    >>> assert eq(shift(a,-1), pd.Series([2,3,4,5,np.nan], drange(-4)))

    :Example: np.ndarrays
    ---------------------
    >>> assert eq(shift(a.values), shift(a).values)

    :Example: nan skipping
    ---------------------
    >>> a = pd.Series([1.,2,np.nan,3,4], drange(-4))
    >>> assert eq(shift(a), pd.Series([np.nan,1,np.nan, 2,3], drange(-4)))
    >>> assert eq(a.shift(), pd.Series([np.nan,1,2,np.nan,3], drange(-4))) # the location of the nan changes

    :Example: state management
    --------------------------
    >>> old = a.iloc[:3]
    >>> new = a.iloc[3:]
    >>> old_ts = shift_(old)
    >>> new_ts = shift(new, **old_ts)
    >>> assert eq(new_ts, shift(a).iloc[3:])
    """
    if n == 0:
        return a
    state = state or Dict(vec = None, i = 0,)
    state.vec = _vec(state.vec, n)
    return first_(_shift1(a, state.vec, axis = axis) if n == 1 else _shift(a, n, axis = axis, **state))

def shift_(a, n=1, axis = 0, instate = None):
    """
    Equivalent to shift(a,n) but returns the full state. See shift for full details
  
    """
    if n == 0:
        return Dict(data = a, state = instate)
    state = instate or Dict(vec = None, i = 0,)
    state.vec = _vec(state.vec, n)
    return _data_state(['data', 'vec', 'i'], _shift1(a, vec = state.vec, axis = axis) if n == 1 else _shift(a, n, axis = axis, **state))

shift_.output = ['data', 'state']
        
def ratio(a, n=1, data = None, state = None):
    """
    Equivalent to a.diff() but in log-space..
    
    :Parameters:
    ------------
    a : array, pd.Series, pd.DataFrame or list/dict of these
        timeseries
    n: int
        size of rolling window

    data: None.
        unused at the moment. Allow code such as func(live, **func_(history)) to work
    state: dict, optional
        state parameters used to instantiate the internal calculations, based on history prior to 'a' provided. 
            
    :Example:
    ---------
    >>> from pyg import *; import pandas as pd; import numpy as np
    >>> a = pd.Series([1.,2,3,4,5], drange(-4))
    >>> assert eq(ratio(a), pd.Series([np.nan, 2, 1.5, 4/3,1.25], drange(-4)))
    >>> assert eq(ratio(a,2), pd.Series([np.nan, np.nan, 3, 2, 5/3], drange(-4)))
    """
    state = state or Dict(vec = None, i = 0)
    state.vec = _vec(state.vec, n)
    return first_(_ratio(a, n, **state))

def ratio_(a, n=1, data = None, instate = None):
    state = instate or Dict(vec = None, i = 0) 
    state.vec = _vec(state.vec, n)
    return _data_state(['data', 'vec', 'i'], _ratio(a, n, **state))

ratio_.output = ['data', 'state']


def rolling_mean(a, n, time = None, axis = 0, data = None, state = None):
    """
    equivalent to pandas a.rolling(n).mean().
    
    - works with np.arrays
    - handles nan without forward filling.
    - supports state parameters
    
    :Parameters:
    ------------
    a : array, pd.Series, pd.DataFrame or list/dict of these
        timeseries
    n: int
        size of rolling window
    time: a sequence of rising values of time
        passage of time
    axis : int, optional
        0/1/-1. The default is 0.    
    data: None.
        unused at the moment. Allow code such as func(live, **func_(history)) to work
    state: dict, optional
        state parameters used to instantiate the internal calculations, based on history prior to 'a' provided. 
        
    :Example: agreement with pandas
    --------------------------------
    >>> from pyg import *; import pandas as pd; import numpy as np
    >>> a = pd.Series(np.random.normal(0,1,10000), drange(-9999))
    >>> panda = a.rolling(10).mean(); ts = rolling_mean(a,10)
    >>> assert abs(ts-panda).max()<1e-10   

    :Example: nan handling
    ----------------------
    Unlike pandas, timeseries does not include the nans in the rolling calculation: it skips them.
    Since pandas rolling engine does not skip nans, they propagate. 
    In fact, having removed half the data points, rolling(10) will return 99% of nans

    >>> a[a<0.1] = np.nan
    >>> panda = a.rolling(10).mean(); ts = rolling_mean(a,10)
    >>> print('#original:', len(nona(a)), 'timeseries:', len(nona(ts)), 'panda:', len(nona(panda)), 'data points')
    >>> #original: 4534 timeseries: 4525 panda: 6 data points

    :Example: state management
    --------------------------
    One can split the calculation and run old and new data separately.

    >>> old = a.iloc[:5000]        
    >>> new = a.iloc[5000:]    
    >>> ts = rolling_mean(a,10)
    >>> old_ts = rolling_mean_(old,10)
    >>> new_ts = rolling_mean(new, 10, **old_ts)    
    >>> assert eq(new_ts, ts.iloc[5000:])

    :Example: dict/list inputs
    ---------------------------
    >>> assert eq(rolling_mean(dict(x = a, y = a**2),10), dict(x = rolling_mean(a,10), y = rolling_mean(a**2,10)))
    >>> assert eq(rolling_mean([a,a**2],10), [rolling_mean(a,10), rolling_mean(a**2,10)])

    :Example: passage of time
    --------------------------
    >>> a = np.array([1.,2.,3.,4.])
    >>> time = np.array([0,0,1,1]) ## i.e. the first two observations are from day 0 and the next two are from day 1
    >>> rolling_mean(a,2,time)
    >>> array([nan, nan, 2.5, 3. ])  
    
    ## The first two observations are from day 0 so cannot have a mean until we get a second point
    ## The mean is then calculated from last observation in day 0 (i.e. 2) and then 3. and then with 4. since these are again, from same day
            

    """
    state = state or Dict(t0 = 0, t1 = 0., vec = None, i = 0, t = np.nan)
    state.vec = _vec(state.vec, n, 0.)
    return first_(_trolling_mean(a, n, time = time, denom = n, axis = axis, **state))

def rolling_rms(a, n, time = None, axis = 0, data = None, state = None):
    """
    equivalent to pandas (a**2).rolling(n).mean()**0.5.
    
    - works with np.arrays
    - handles nan without forward filling.
    - supports state parameters
    
    :Parameters:
    ------------
    a : array, pd.Series, pd.DataFrame or list/dict of these
        timeseries
    n: int
        size of rolling window
    time: a sequence of rising values of time
        passage of time
    axis : int, optional
        0/1/-1. The default is 0.    
    data: None.
        unused at the moment. Allow code such as func(live, **func_(history)) to work
    state: dict, optional
        state parameters used to instantiate the internal calculations, based on history prior to 'a' provided. 
        
    :Example: agreement with pandas
    --------------------------------
    >>> from pyg import *; import pandas as pd; import numpy as np
    >>> a = pd.Series(np.random.normal(0,1,10000), drange(-9999))
    >>> panda = (a**2).rolling(10).mean()**0.5; ts = rolling_rms(a,10)
    >>> assert abs(ts-panda).max()<1e-10   

    :Example: nan handling
    ----------------------
    Unlike pandas, timeseries does not include the nans in the rolling calculation: it skips them.
    Since pandas rolling engine does not skip nans, they propagate. 
    In fact, having removed half the data points, rolling(10) will return 99% of nans

    >>> a[a<0.1] = np.nan
    >>> panda = (a**2).rolling(10).mean()**0.5; ts = rolling_rms(a,10)
    >>> print('#original:', len(nona(a)), 'timeseries:', len(nona(ts)), 'panda:', len(nona(panda)), 'data points')
    >>> #original: 4534 timeseries: 4525 panda: 6 data points

    :Example: state management
    --------------------------
    One can split the calculation and run old and new data separately.

    >>> old = a.iloc[:5000]        
    >>> new = a.iloc[5000:]    
    >>> ts = rolling_rms(a,10)
    >>> old_ts = rolling_rms_(old,10)
    >>> new_ts = rolling_rms(new, 10, **old_ts)    
    >>> assert eq(new_ts, ts.iloc[5000:])

    :Example: dict/list inputs
    ---------------------------
    >>> assert eq(rolling_rms(dict(x = a, y = a**2),10), dict(x = rolling_rms(a,10), y = rolling_rms(a**2,10)))
    >>> assert eq(rolling_rms([a,a**2],10), [rolling_rms(a,10), rolling_rms(a**2,10)])

    :Example: passage of time
    --------------------------
    >>> a = np.array([1.,2.,3.,4.])
    >>> time = np.array([0,0,1,1]) ## i.e. the first two observations are from day 0 and the next two are from day 1
    >>> (rolling_rms(a,2,time) ** 2) * 2
    >>> array([nan, nan, 13., 20.])   == array([nan, nan, 4 + 9, 4 + 16])
    
    ## The first two observations are from day 0 so cannot have a mean until we get a second point
    ## The rms is then calculated from last observation in day 0 (i.e. 2) and then 3. and then with 4. since these are again, from same day
            

    """
    state = state or Dict(t0 = 0, t2 = 0., vec = None, i = 0, t = np.nan)
    state.vec = _vec(state.vec, n, 0.)
    return first_(_trolling_rms(a, n, time = time, denom = n, axis = axis, **state))

def rolling_sum(a, n, time = None, axis = 0, data = None, state = None):
    """
    equivalent to pandas a.rolling(n).sum().
    
    - works with np.arrays
    - handles nan without forward filling.
    - supports state parameters
    
    :Parameters:
    ------------
    a : array, pd.Series, pd.DataFrame or list/dict of these
        timeseries
    n: int
        size of rolling window
    time: a sequence of rising values of time
        passage of time
    axis : int, optional
        0/1/-1. The default is 0.    
    data: None.
        unused at the moment. Allow code such as func(live, **func_(history)) to work
    state: dict, optional
        state parameters used to instantiate the internal calculations, based on history prior to 'a' provided. 
        
    :Example: agreement with pandas
    --------------------------------
    >>> from pyg import *; import pandas as pd; import numpy as np
    >>> a = pd.Series(np.random.normal(0,1,10000), drange(-9999))
    >>> panda = a.rolling(10).sum(); ts = rolling_sum(a,10)
    >>> assert abs(ts-panda).max()<1e-10   

    :Example: nan handling
    ----------------------
    Unlike pandas, timeseries does not include the nans in the rolling calculation: it skips them.
    Since pandas rolling engine does not skip nans, they propagate. 
    In fact, having removed half the data points, rolling(10) will return 99.9% nans

    >>> a[a<0.1] = np.nan
    >>> panda = a.rolling(10).sum(); ts = rolling_sum(a,10)
    >>> print('#original:', len(nona(a)), 'timeseries:', len(nona(ts)), 'panda:', len(nona(panda)), 'data points')
    >>> #original: 4534 timeseries: 4525 panda: 2 data points

    :Example: state management
    --------------------------
    One can split the calculation and run old and new data separately.

    >>> old = a.iloc[:5000]        
    >>> new = a.iloc[5000:]    
    >>> ts = rolling_sum(a,10)
    >>> old_ts = rolling_sum_(old,10)
    >>> new_ts = rolling_sum(new, 10, **old_ts)    
    >>> assert eq(new_ts, ts.iloc[5000:])

    :Example: dict/list inputs
    ---------------------------
    >>> assert eq(rolling_sum(dict(x = a, y = a**2),10), dict(x = rolling_sum(a,10), y = rolling_sum(a**2,10)))
    >>> assert eq(rolling_sum([a,a**2],10), [rolling_sum(a,10), rolling_sum(a**2,10)])

    :Example: passage of time
    --------------------------
    >>> a = np.array([1.,2.,3.,4.])
    >>> time = np.array([0,0,1,1]) ## i.e. the first two observations are from day 0 and the next two are from day 1
    >>> rolling_sum(a,2,time) 
    >>> array([nan, nan, 5., 6.])   == array([nan, nan, 2+3, 2+4])
    
    ## The first two observations are from day 0 so cannot have a mean until we get a second point
    ## The sum is then calculated from last observation in day 0 (i.e. 2) and then 3. and then with 4. since these are again, from same day
    """
    state = state or Dict(t0 = 0, t1 = 0., vec = None, i = 0, t = np.nan)
    state.vec = _vec(state.vec, n, 0.)
    return first_(_trolling_mean(a, n, time = time, denom = 1, axis = axis, **state))

def rolling_std(a, n, time = None, axis = 0, data = None, state = None):
    """
    equivalent to pandas a.rolling(n).std().
    
    - works with np.arrays
    - handles nan without forward filling.
    - supports state parameters
    
    :Parameters:
    ------------
    a : array, pd.Series, pd.DataFrame or list/dict of these
        timeseries
    n: int
        size of rolling window
    time: a sequence of rising values of time
        passage of time
    axis : int, optional
        0/1/-1. The default is 0.    
    data: None.
        unused at the moment. Allow code such as func(live, **func_(history)) to work
    state: dict, optional
        state parameters used to instantiate the internal calculations, based on history prior to 'a' provided. 
        
    :Example: agreement with pandas
    --------------------------------
    >>> from pyg import *; import pandas as pd; import numpy as np
    >>> a = pd.Series(np.random.normal(0,1,10000), drange(-9999))
    >>> panda = a.rolling(10).std(); ts = rolling_std(a,10)
    >>> assert abs(ts-panda).max()<1e-10   

    :Example: nan handling
    ----------------------
    Unlike pandas, timeseries does not include the nans in the rolling calculation: it skips them.
    Since pandas rolling engine does not skip nans, they propagate. 
    In fact, having removed half the data points, rolling(10) will return 99.9% nans

    >>> a[a<0.1] = np.nan
    >>> panda = a.rolling(10).std(); ts = rolling_std(a,10)
    >>> print('#original:', len(nona(a)), 'timeseries:', len(nona(ts)), 'panda:', len(nona(panda)), 'data points')
    >>> #original: 4534 timeseries: 4525 panda: 2 data points

    :Example: state management
    --------------------------
    One can split the calculation and run old and new data separately.

    >>> old = a.iloc[:5000]        
    >>> new = a.iloc[5000:]    
    >>> ts = rolling_std(a,10)
    >>> old_ts = rolling_std_(old,10)
    >>> new_ts = rolling_std(new, 10, **old_ts)    
    >>> assert eq(new_ts, ts.iloc[5000:])

    :Example: dict/list inputs
    ---------------------------
    >>> assert eq(rolling_std(dict(x = a, y = a**2),10), dict(x = rolling_std(a,10), y = rolling_std(a**2,10)))
    >>> assert eq(rolling_std([a,a**2],10), [rolling_std(a,10), rolling_std(a**2,10)])

    :Example: passage of time
    --------------------------
    >>> a = np.array([1.,2.,3.,4.])
    >>> time = np.array([0,0,1,1]) ## i.e. the first two observations are from day 0 and the next two are from day 1
    >>> 2*(rolling_std(a,2,time) ** 2)
    >>> array([nan, nan, 1., 4.])
    
    ## The first two observations are from day 0 so cannot have a mean until we get a second point
    ## The sum is then calculated from last observation in day 0 (i.e. 2) and then 3. and then with 4. since these are again, from same day
    """    
    state = state or Dict(t0 = 0, t1 = 0, t2 = 0., vec = None, i = 0, t = np.nan)
    state.vec = _vec(state.vec, n, 0.)
    return first_(_trolling_std(a, n, time = time, denom = n, axis = axis, **state))

def rolling_skew(a, n, bias = False, time = None, axis = 0, data = None, state = None):
    """
    equivalent to pandas a.rolling(n).skew().
    
    - works with np.arrays
    - handles nan without forward filling.
    - supports state parameters
    
    :Parameters:
    ------------
    a : array, pd.Series, pd.DataFrame or list/dict of these
        timeseries
    n: int
        size of rolling window
    time: a sequence of rising values of time
        passage of time
    bias: 
        affects the skew calculation definition, see scipy documentation for details.
    axis : int, optional
        0/1/-1. The default is 0.    
    data: None.
        unused at the moment. Allow code such as func(live, **func_(history)) to work
    state: dict, optional
        state parameters used to instantiate the internal calculations, based on history prior to 'a' provided. 
        
    :Example: agreement with pandas
    --------------------------------
    >>> from pyg import *; import pandas as pd; import numpy as np
    >>> a = pd.Series(np.random.normal(0,1,10000), drange(-9999))
    >>> panda = a.rolling(10).skew(); ts = rolling_skew(a,10)
    >>> assert abs(ts-panda).max()<1e-10   

    :Example: nan handling
    ----------------------
    Unlike pandas, timeseries does not include the nans in the rolling calculation: it skips them.
    Since pandas rolling engine does not skip nans, they propagate. 
    In fact, having removed half the data points, rolling(10) will return 99.9% nans

    >>> a[a<0.1] = np.nan
    >>> panda = a.rolling(10).skew(); ts = rolling_skew(a,10)
    >>> print('#original:', len(nona(a)), 'timeseries:', len(nona(ts)), 'panda:', len(nona(panda)), 'data points')
    >>> #original: 4534 timeseries: 4525 panda: 2 data points

    :Example: state management
    --------------------------
    One can split the calculation and run old and new data separately.

    >>> old = a.iloc[:5000]        
    >>> new = a.iloc[5000:]    
    >>> ts = rolling_skew(a,10)
    >>> old_ts = rolling_skew_(old,10)
    >>> new_ts = rolling_skew(new, 10, **old_ts)    
    >>> assert eq(new_ts, ts.iloc[5000:])

    :Example: dict/list inputs
    ---------------------------
    >>> assert eq(rolling_skew(dict(x = a, y = a**2),10), dict(x = rolling_skew(a,10), y = rolling_skew(a**2,10)))
    >>> assert eq(rolling_skew([a,a**2],10), [rolling_skew(a,10), rolling_skew(a**2,10)])
    """
    state = state or Dict(t0 = 0, t1 = 0, t2 = 0., t3 = 0, vec = None, i = 0, t = np.nan)
    state.vec = _vec(state.vec, n, 0.)
    return first_(_trolling_skew(a, n, time = time, bias = bias, denom = n, axis = axis, **state))


def rolling_mean_(a, n, time = None, axis = 0, data = None, instate = None):
    """
    Equivalent to rolling_mean(a) but returns also the state variables t0,t1 etc. 
    For full documentation, look at rolling_mean.__doc__
    """
    state = instate or Dict(t0 = 0, t1 = 0., vec = None, i = 0, t = np.nan)
    state.vec = _vec(state.vec, n, 0.)
    return _data_state(['data','t0','t1', 'vec','i', 't'],_trolling_mean(a, n, time = time, denom = n, axis = axis, **state))

rolling_mean_.output = ['data','state']

def rolling_rms_(a, n, time = None, axis = 0, data = None, instate = None):
    """
    Equivalent to rolling_rms(a) but returns also the state variables t0,t1 etc. 
    For full documentation, look at rolling_rms.__doc__
    """
    state = instate or Dict(t0 = 0, t2 = 0., vec = None, i = 0, t = np.nan)
    state.vec = _vec(state.vec, n, 0.)
    return _data_state(['data','t0','t2', 'vec','i', 't'],_trolling_rms(a, n, time = time, denom = n, axis = axis, **state))

rolling_rms_.output = ['data','state']

def rolling_sum_(a, n, time = None, axis = 0, data = None, instate = None):
    """
    Equivalent to rolling_sum(a) but returns also the state variables t0,t1 etc. 
    For full documentation, look at rolling_sum.__doc__
    """
    state = instate or Dict(t0 = 0, t1 = 0., vec = None, i = 0, t = np.nan)
    state.vec = _vec(state.vec, n, 0.)
    return _data_state(['data','t0','t1', 'vec','i', 't'], _trolling_mean(a, n, denom = 1, axis = axis, **state))

rolling_sum_.output = ['data','state']

def rolling_std_(a, n, time = None, axis = 0, data = None, instate = None):
    """
    Equivalent to rolling_std(a) but returns also the state variables t0,t1 etc. 
    For full documentation, look at rolling_std.__doc__
    """
    state = instate or Dict(t0 = 0, t1 = 0, t2 = 0., vec = None, i = 0, t = np.nan)
    state.vec = _vec(state.vec, n, 0.)
    return _data_state(['data','t0', 't1', 't2', 'vec', 'i', 't'],_trolling_std(a, n, time = time, denom = n, axis = axis, **state))


rolling_std_.output = ['data','state']

def rolling_skew_(a, n, time = None, bias = False, axis = 0, data = None, instate = None):
    """
    Equivalent to rolling_skew(a) but returns also the state variables t0,t1 etc. 
    For full documentation, look at rolling_skew.__doc__
    """
    state = instate or Dict(t0 = 0, t1 = 0, t2 = 0., t3 = 0, vec = None, i = 0, t = np.nan)
    state.vec = _vec(state.vec, n, 0.)
    return _data_state(['data','t0', 't1', 't2', 't3', 'vec','i', 't'], _trolling_skew(a, n, time = time, bias = bias, denom = n, axis = axis, **state))

rolling_skew_.output = ['data','state']
