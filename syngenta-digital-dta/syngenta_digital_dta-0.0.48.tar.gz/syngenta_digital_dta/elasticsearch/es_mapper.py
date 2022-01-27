from syngenta_digital_dta.common import schema_loader


def convert_schema_to_mapping(schema_file, schema_key, special=None):
    mapping = {}
    schema = schema_loader.load_schema(schema_file, schema_key)
    schemas = schema['allOf'] if schema.get('allOf') else [schema]
    for model in schemas:
        if model.get('type') == 'object':
            __walk_schema(schema['properties'], mapping, special)
    return {'properties': mapping}


def __walk_schema(properties, mapping, special):
    for property_key, property_value in properties.items():
        if property_value.get('type') == 'object' and property_value.get('properties'):
            mapping[property_key] = {}
            mapping[property_key]['type'] = 'object'
            mapping[property_key]['properties'] = {}
            __walk_schema(property_value['properties'], mapping[property_key]['properties'], special)
        elif property_value.get('type') == 'object' and not property_value.get('properties'):
            mapping[property_key] = {}
            mapping[property_key]['type'] = 'object'
        elif property_value.get('items', {}).get('properties'):
            mapping[property_key] = {}
            mapping[property_key]['type'] = 'nested'
        elif special and isinstance(special, dict) and special.get(property_key):
            mapping[property_key] = {'type': special[property_key]}
        else:
            simple_type = __translate_simple_type(property_value)
            if simple_type:
                mapping[property_key] = simple_type


def __translate_simple_type(property_value):
    if property_value.get('format', '') in ['email','idn-email','hostname','uri', 'uri-reference','iri', 'iri-reference']:
        mapping_type = {'type': 'text', 'analyzer': 'url_email_analyzer'}
    elif 'ip' in property_value.get('format', ''):
        mapping_type = {'type': 'ip'}
    elif 'date' in property_value.get('format', ''):
        mapping_type = {'type': 'date', 'format': "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis||strict_date_optional_time"}
    elif property_value.get('type') == 'number':
        mapping_type = {'type': 'long'}
    elif property_value.get('type') == 'string':
        mapping_type = {'type': 'text'}
    elif property_value.get('type') == 'array':
        mapping_type = None
    else:
        mapping_type = {'type': property_value.get('type')}
    return mapping_type
