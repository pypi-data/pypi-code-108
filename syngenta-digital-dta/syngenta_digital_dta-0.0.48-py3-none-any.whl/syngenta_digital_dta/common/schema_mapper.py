from syngenta_digital_dta.common import schema_loader


def map_to_schema(data, schema_file, schema_key):
    model_data = {}
    model_schema = schema_loader.load_schema(schema_file, schema_key)
    schemas = model_schema['allOf'] if model_schema.get('allOf') else [model_schema]
    for model in schemas:
        if model.get('type') == 'object':
            _populate_model_data(model.get('properties', {}), data, model_data)
    return model_data


def _populate_model_data(properties, data, model_data):
    if data and isinstance(data, dict):
        _populate_model_dict(properties, data, model_data)
    return model_data


def _populate_model_dict(properties, data, model_data):
    for property_key, property_value in properties.items():
        model_data[property_key] = {}
        if property_value.get('properties'):
            _populate_model_data(property_value['properties'], data.get(property_key), model_data[property_key])
        elif property_value.get('items', {}).get('properties'):
            _populate_model_list(model_data, property_key, property_value, data)
        else:
            model_data[property_key] = data.get(property_key)


def _populate_model_list(model_data, property_key, property_value, data):
    model_data[property_key] = []
    for index in range(len(data.get(property_key, []))):
        if data.get(property_key) and isinstance(data[property_key], list) and index < len(data[property_key]):
            pop = _populate_model_data(property_value['items']['properties'], data[property_key][index], {})
            model_data[property_key].append(pop)
