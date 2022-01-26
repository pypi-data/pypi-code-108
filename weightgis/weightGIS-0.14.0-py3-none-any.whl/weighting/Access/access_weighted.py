from miscSupports import flatten, terminal_time


def access_weighted(data_extraction_set, data_requested):
    """
    This will use a set of keys to extract data from a weightGIS json database so that i can be written out or used in
    applications or processes.

    Note
    -----
    This requires the json dict to follow the weightGIS v0.9 or above json format of the following for each entry:

    gid__place: {attribute1: {date1:value1 ... dateN:valueN} ... attributeN: {date1:value1 ... dateN:valueN}

    :param data_extraction_set: The loaded json database
    :type data_extraction_set: dict

    :param data_requested: The attributes you would like to extract from each place
    :type data_requested: list

    """
    all_dates = []
    for place, attributes in zip(data_extraction_set.keys(), data_extraction_set.values()):
        place_dates = []

        # Isolate each elements keys, which should be the dates, as long as the data exists and is a dict
        for data in data_requested:
            if data in attributes.keys() and isinstance(attributes[data], dict):
                place_dates.append(list(attributes[data].keys()))

        all_dates.append(flatten(place_dates))

    common_dates = sorted(list(set(flatten(all_dates))))

    row_data = []
    for place, d_attr in zip(data_extraction_set.keys(), data_extraction_set.values()):

        # The place name will be a gid__place which we want to extract here
        place_names = place.split("__")
        gid, place = place_names[0], "_".join([p for i, p in enumerate(place_names) if i != 0])

        # Then for each date we setup our first two columns of place-date
        for date in common_dates:
            date_values = [gid, place, date]

            # And for each attribute requested, we extract the value if the date is valid, else NA
            for attr in data_requested:
                if (attr in d_attr.keys()) and (isinstance(d_attr[attr], dict) and (date in d_attr[attr].keys())):
                    date_values.append(d_attr[attr][date])
                else:
                    date_values.append("NA")
            row_data.append(date_values)

    print(f"Retrieved Weighted Data {terminal_time()}")
    return row_data
