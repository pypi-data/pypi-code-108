from .filter_models import filter_query


# This functions are used to handle the data of url body to be easier to implement them on the django orm
def filter_queryset_according_parameters(object, queryset):
    """
    Get request meth from request (example of structure: "GET http://127.0.0.1:9000/?price[gte]=10&price[lte]=100&limit=20&offset=100&sort_by=desc[name],asc[email]&locale=pt-PT")
    Return a queryset according to the parameters.
    """

    request_meth = object.request.query_params

    has_status = True if request_meth.get('status', None) else None
    if not has_status:
        queryset = queryset.filter(status=1).order_by('-id')

    # Get the filters and sort
    filters, sort = get_filters_and_sort_from_request(request_meth)

    # Apply the filters
    queryset, has_filter = filter_query(queryset, filters)

    # Apply the sort
    queryset = queryset.order_by(*sort) if sort else queryset

    return queryset


def get_filters_and_sort_from_request(request_meth):
    """
    Get request meth from request (example of structure: "GET http://127.0.0.1:9000/?price[gte]=10&price[lte]=100&limit=20&offset=100&sort_by=desc[name],asc[email]&locale=pt-PT")
    Return a dictionary for filter and a string for sort.
    (This dictionary is used with filter_query to apply the filters)
    """

    filters = {}
    sort = []
    for parameter, value in request_meth.items():

        if not value or (parameter in ['offset', 'limit', 'page', 'page_size']):
            continue

        if parameter == 'sort_by':
            # sort_by=desc[last_modified],asc[email]
            if ',' in value:
                values = value.split(",")
                for value in values:
                    sort.append(get_sort_in_django_format(value))
                continue

            # sort_by=desc[last_modified]
            sort.append(get_sort_in_django_format(value))
            continue

        search_type = None
        field_name = parameter

        if '[' in parameter:
            parameter_info = parameter.split("[")
            search_type = parameter_info[1][:-1]
            field_name = parameter_info[0]

        if search_type == 'in' and ',' in value:
            value = value.split(',')

        filters[field_name] = {
            "value": value,
            "search_type": search_type
        }

    return filters, sort


def get_sort_in_django_format(parameter):
    """
    Get a parameter of the type sort: sort_by=desc[last_modified]
    return: '-last_modified'
    """

    parameter_info = parameter.split("[")
    order_type = parameter_info[0]
    field_name = parameter_info[1][:-1]
    if order_type == 'desc':
        return f'-{field_name}'
    return field_name
