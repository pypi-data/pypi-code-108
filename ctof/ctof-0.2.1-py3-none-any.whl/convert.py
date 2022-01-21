# Imports
from typing import Union

def convert(values: Union[int, float, list, tuple, set], _from: str, _to: str) -> Union[float, list, tuple, set]:
    """
    Returns the given value(s) converted from one temperature (_from) to another (_to).
    Floating point numbers are NOT formatted or rounded by this function.
    
    :param values: The value(s) to convert. Examples of valid values: 86, 37.5, [35,36,37]
    :type values:  Union[int, float, list, tuple, set]
    :param _from:  The temperature scale the values are set to. Valid values: "C", "F", "K"
    :type _from:   str
    :param _to:    The temperature scale to convert to. Valid values: "C", "F", "K"
    :type _to:     str
    :return:       The values converted to the specified temperature scale.
    :rtype:        Union[float, list, tuple, set]
    """
    # Lambda functions that contain the conversion expressions
    ctof = lambda x: x * (9 / 5) + 32
    ftoc = lambda x: (x - 32) * (5 / 9)
    ctok = lambda x: x + 273.15
    ktoc = lambda x: x - 273.15
    
    # Check if _from or _to is not a string
    if not isinstance(_from, str) or not isinstance(_to, str):
        raise TypeError("_from and _to arguments must be a string")
    # Check if _from or _to is not "C", "F" or "K"
    _from, _to = _from.upper(), _to.upper()
    if _from not in ("C", "F", "K") or _to not in ("C", "F", "K"):
        raise ValueError("_from and _to arguments must be 'C', 'F' or 'K'")
    # Check if _from and _to are identical (e.g. "C" == "C")
    if _from == _to:
        return values
    
    # Number (int/float) conversion
    if isinstance(values, int) or isinstance(values, float):
        if _from == "C":
            if _to == "F":
                return ctof(values)
            elif _to == "K":
                return ctok(values)

        elif _from == "F":
            if _to == "C":
                return ftoc(values)
            elif _to == "K":
                return ctok(ftoc(values))
        
        elif _from == "K":
            if _to == "C":
                return ktoc(values)
            elif _to == "F":
                return ctof(ktoc(values))
    
    # List conversion
    elif isinstance(values, list):
        newvalues = []
        for i in values:
            if len(values) > 1:
                if not isinstance(i, int) and not isinstance(i, float):
                    raise TypeError("at least one iterable member is not an int/float")
                if _from == "C":
                    if _to == "F":
                        newvalues.append(ctof(i))
                    elif _to == "K":
                        newvalues.append(ctok(i))

                elif _from == "F":
                    if _to == "C":
                        newvalues.append(ftoc(i))
                    elif _to == "K":
                        newvalues.append(ctok(ftoc(i)))
                
                elif _from == "K":
                    if _to == "C":
                        newvalues.append(ktoc(i))
                    elif _to == "F":
                        newvalues.append(ctof(ktoc(i)))     
            else:
                if isinstance(i, int) or isinstance(i, float):
                    return convert(i, _from, _to)
                raise TypeError("at least one iterable member is not an int/float")
                
        return newvalues 
    
    # Tuple/set conversion
    elif isinstance(values, tuple):
        return tuple(convert(list(values), _from, _to))
    elif isinstance(values, set):
        return set(convert(list(values), _from, _to))

    # Handle passed values with invalid types
    else:
        raise TypeError("parameter 'values' not of type int/float/list/tuple/set")
