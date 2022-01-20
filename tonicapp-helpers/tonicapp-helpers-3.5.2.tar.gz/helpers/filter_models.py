
def filter_query(set, filters):
    """
        Apply filters to a set.
        Receive a queryset and a dictionary with the following structure:
        {"name_of_the_column_in_model": {
            "value": what_we_want,
            "search_type": search_type}
        }
        return: set filtered
    """

    has_filter = False
    for filter_name, info in filters.items():
        if info["value"] is None:
            continue

        has_filter = True
        if info['search_type']:
            v_filter = f"{filter_name}__{info['search_type']}"
        else:
            v_filter = f"{filter_name}"
        set = set.filter(**{v_filter: info["value"]})

    return set, has_filter
