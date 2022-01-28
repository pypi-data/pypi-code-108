def empty_schema_field_dict(schema_dict):
    """Return the schema fields as a typical dict (that you would normally interact with) with all fields empty
    NOTE: Array types will return an array with ONE instance of the the expected object type"""
    if schema_dict.get('fields'):
        return {field['name']: '' if isinstance(field['type'], str) else empty_schema_field_dict(field['type'])
                for field in schema_dict['fields']}
    return [empty_schema_field_dict(schema_dict['items'])]