
from types import FunctionType
import inspect
import pandas
import typing

def example_udf(df: pandas.DataFrame) -> pandas.DataFrame:
    # transform dataframe
    print('test')
    return df

def is_valid_udf(udf: FunctionType): 
    param_types = list(inspect.signature(udf).parameters.values())
    if len(param_types) != 1 or not param_types[0].annotation is pandas.DataFrame:
        raise TypeError(f"Valid User Defined Functions must accept exactly one parameter of explicit type<pandas.DataFrame>\n\n e.g\n\n {inspect.getsource(example_udf)}")

    if not inspect.signature(udf).return_annotation is pandas.DataFrame: 
        raise TypeError(f"Valid User Defined Functions must have a return type of exactly one <pandas.DataFrame>\n\n e.g\n\n {inspect.getsource(example_udf)}")

def stringify_udf(udf: FunctionType) -> str:
    """Creates a string representation of the given udf.  Aliases the udf as 'udf' 
    since we don't know the name of the function"""
    return f'{inspect.getsource(example_udf)}' \
        f'\nudf = {example_udf.__name__}' 
        
def _udf_text_to_function(function_text: str, dataframe: pandas.DataFrame) -> pandas.DataFrame:
    """  pass reference to global symbols so function can use pandas, builtins, etc. 
    TODO: allow users to bring their own imports, add them to passed globals 
    TODO: pass a new globals object so users can't override our symbols
    This statement executes the function text and adds the defined function to
    the locs dict. We then return that function. 
    """
    locs = {}
    exec(function_text, globals(), locs)
    return locs['udf']


