from typing import Union

import numpy as np

def pretty_float(val:Union[str, float])->Union[int, float]:
    if float(val).is_integer():
        return int(float(val))
    return float(val)

def pretty_value(val:Union[int, float])->Union[int, float]:
    if isinstance(val, float) and val.is_integer():
        return int(val)
    return val

def is_integer(s:str):
    if not s:
        return False
    if len(s) == 1:
        return s.isdigit()
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()

def array_swap(arr1:np.ndarray, arr2:np.ndarray, indices):
    arr1[indices], arr2[indices] = arr2[indices], arr1[indices]

def df_array_swap(df, col1:str, col2:str, indices=None):
    if indices is None:
        df.loc[:, col1], df.loc[:, col2] = df[col2], df[col1]
    else:
        df.loc[indices, col1], df.loc[indices, col2] = df[indices][col2], df[indices][col1]
        
def reorder_arrays(*arrays, descending:bool=True):
    if descending:
        if not (arrays[0].dtype.type in [np.string_, np.str_]):
            indices = np.argsort(-arrays[0])
        else:
            indices = np.argsort(arrays[0])[::-1]
    else:
        indices = np.argsort(arrays[0])
    for arr in arrays:
        arr[:] = arr[indices]    

def reverse_arrays(*arrays):
    for arr in arrays:
        arr[:] = arr[::-1] 
        
def ceildiv(a, b):
    return -(-a // b)

def approx_n_digit(val:float, default=5):
    s = str(val)
    if not s.replace('.','',1).isdigit():
        return default
    elif '.' in s:
        return len(s.split('.')[1])
    else:
        return 0

def str_encode_value(val, n_digit=None, formatted=True):
    # account for the case where val is negative zero
    if round(float(val), 8) == 0:
        val = 0.
    if n_digit is not None:
        val_str = '{{:.{}f}}'.format(n_digit).format(val)
        #if val_str == '-{{:.{}f}}'.format(n_digit).format(0):
        #    val_str = '{{:.{}f}}'.format(n_digit).format(0)
    else:
        val_str = str(val)
    
    if formatted:
        val_str = val_str.replace('.', 'p').replace('-', 'n')
    return val_str

def str_decode_value(val_str):
    val = float(val_str.replace('p','.').replace('n','-'))
    return val