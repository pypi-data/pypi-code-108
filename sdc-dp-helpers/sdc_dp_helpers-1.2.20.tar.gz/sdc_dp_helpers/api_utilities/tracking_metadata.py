def tracking_metadata(data_object: list, **kwargs) -> list:
    """
    A method to manage a more consistent tracking mechanism
    for any service that requires tracking to be sent to s3.

    Object consumed is expected to look like:
        "service",  # the name of the service i.e. google_analytics_v3
        "response_datetime",  # the datetime.now() of when the request was made
        "index",  # response index, page token etc
        "id_name",  # identifier name of the current request i.e. view_id
        "id_value",  # value of the identifier od the current request i.e 528447
        "config_datetime",  # the date scope that the config is querying
        "configuration", # dict object of the configuration file for reference
        "byte_size", # the size of the object in bytes
    """

    valid_keys = [
        "service",
        "response_datetime",
        "index",
        "id_name",
        "id_value",
        "config_datetime",
        "configuration",
        "byte_size",
    ]

    dataset = {}
    for key in valid_keys:
        try:
            dataset[key] = kwargs.get(key)
        except KeyError:
            raise KeyError(
                "The tracking_metadata only supports specific key value pairs."
            )

    data_object.append(dataset)
    return data_object
