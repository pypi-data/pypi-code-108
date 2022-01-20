def check_nan(series):

    issues = series.isna().sum()

    if issues:
        print(f'the series \'{series.name}\' contains {issues} Null value(s).')
    return issues

def check_data_types(series):

    data_types = set(series.apply(type))
    issues = int(len(data_types)>1)

    if issues:
        print(f'the series \'{series.name}\' contains {len(data_types)} data types: {data_types}')
    return issues