NANOSECONDS_IN_SECOND: int = 1_000_000_000


RAW_STRING_TRUE_VALUES = {'yes',
                          'y',
                          '1',
                          'true',
                          '+'}

RAW_STRING_FALSE_VALUES = {'no',
                           'n',
                           '0',
                           'false',
                           '-'}


STRING_TRUE_VALUES = {str(value).casefold() for value in RAW_STRING_TRUE_VALUES}

STRING_FALSE_VALUES = {str(value).casefold() for value in RAW_STRING_FALSE_VALUES}
