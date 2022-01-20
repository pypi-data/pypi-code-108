import re

from pandas import DataFrame

__MYSQL_TO_PANDAS_PARSED_OPERATORS = [
    'all', 'any', r'between \w+ and \w+', 'and', 'exists', 'in', 'like', 'not', 'or', 'some', '==', '>=', '<=', '=', '<>', '<', '>'
]

__MYSQL_TO_PANDAS_PARSED_OPERATORS_REGEX = '|'.join([f'({op})' for op in __MYSQL_TO_PANDAS_PARSED_OPERATORS])
__MYSQL_TO_PANDAS_PARSED_OPERATORS_INCLUDE_REGEX = '|'.join([f'(\W{op})' for op in __MYSQL_TO_PANDAS_PARSED_OPERATORS])


def assert_required_columns(df: DataFrame, *required):
    _missing = [col for col in required if col not in df]

    if _missing:
        raise KeyError(*_missing)

def parse_mysql_to_pandas_query(query: str):
    _query = list(
        map(
            str.strip,
            filter(
                None, 
                re.split(
                    __MYSQL_TO_PANDAS_PARSED_OPERATORS_INCLUDE_REGEX,
                    query,
                    flags=re.IGNORECASE
                )
            )
        )
    )
    
    for index, item in enumerate(zip(_query, _query[1:])):
        first, second = item
        _first = first.lower()
        
        if re.match(__MYSQL_TO_PANDAS_PARSED_OPERATORS_REGEX, _first):
            _query[index] = _first

            if _first == '=' and _first != second:
                _query[index] = '=='

            elif _first == '<>':
                _query[index] = '!='

            elif _first == 'in':
                _numbers = re.findall(r'-?\d+', second)

                _query[index + 1] = f"({', '.join(_numbers)},)"
        
        elif re.match(r'between \w+ and \w+', second):
            _values = second.split(' ')
            _query[index] = f'{_values[1]} <= {first} <= {_values[-1]}'
            _query[index + 1] = '' 

    return ' '.join(_query)