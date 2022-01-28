from datetime import timedelta, datetime

from sdc_dp_helpers.api_utilities.date_managers import date_handler


def date_range(start_date, end_date, delta=timedelta(days=1)):
    """
    The range is inclusive, so both start_date and end_date will be returned.
    :start_date: The datetime object representing the first day in the range.
    :end_date: The datetime object representing the second day in the range.
    :delta: A datetime.timedelta instance, specifying the step interval. Defaults to one day.
    Yields:
        Each datetime object in the range.
    """

    start_date = date_handler(date_string=start_date)
    end_date = date_handler(date_string=end_date)

    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    current_date = start_date
    while current_date <= end_date:
        yield current_date.strftime('%Y-%m-%d')
        current_date += delta


def un_nest_keys(data, col, key_list, value_list):
    """
    A simple method that takes a set of keys and values
    from a dataset with dimensions and replaces them
    with key value pairs.

    :data: The dataset that needs to be un_nested.
    :col: The key name of the dimensions.
    :key_list: List of keys.
    :value_list: List of Values.

    returns:
        So dataset A:
            {'keys': [1, 2, 3]}
        Can become:
            {'key1': 1, 'key2': 2, 'key3': 3}
    """
    data.update(
        dict(zip(key_list, value_list))
    )
    del data[col]
    return data
