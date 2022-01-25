def create_arn(service='', region='', account_id='', resource_type='', resource_id=''):
    if resource_type == 'db' or resource_type == 'cluster':
        separator = ':'
    else:
        separator = '/'
    _resource_arn = 'arn:aws:' + service + ':' + region + ':' + account_id + ':' + resource_type + separator + resource_id
    return _resource_arn


# Return stack name
def get_stack_name(customer_id, environment_type, stack_identifier):
    return stack_identifier + '-' + environment_type + '-' + customer_id
