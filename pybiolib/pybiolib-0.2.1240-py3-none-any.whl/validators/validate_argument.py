render_types = [
    ('dropdown', 'Dropdown'),
    ('file', 'File'),
    ('hidden', 'Hidden'),
    ('number', 'Number'),
    ('radio', 'Radio'),
    ('text', 'Text'),
    ('text-file', 'Text File'),
    ('toggle', 'Toggle'),
]


def validate_argument(argument_data):
    error_dict = {}
    key = validate_key(argument_data, error_dict)
    if key is None:
        return error_dict

    error_dict[key] = {}
    argument_error_dict = error_dict[key]

    validate_unsupported_argument_fields(key, argument_data, argument_error_dict)

    # Recursively validate sub_arguments
    sub_arguments = argument_data.get('sub_arguments', {})
    for name, sub_arguments in sub_arguments.items():
        for subargument in sub_arguments:
            errors = validate_argument(subargument)
            if errors:
                if 'sub_arguments' not in error_dict:
                    argument_error_dict['sub_arguments'] = [errors]
                else:
                    argument_error_dict['sub_arguments'].append(validate_argument(subargument))

    validate_required(key, argument_data, argument_error_dict)
    type = validate_type(key, argument_data, argument_error_dict)

    if not type:
        return error_dict

    validate_description(key, argument_data, type, argument_error_dict)

    # Just return empty dict if we have no errors
    if error_dict[key]:
        return error_dict
    else:
        return {}


def validate_key(argument_data, error_dict):
    if 'key' not in argument_data.keys():
        error_dict['required'] = [
            f'One of your arguments is missing a key. Please specify a key for each of your arguments'
        ]
        return None
    else:
        return argument_data['key']


def validate_required(key, argument_data, error_dict):
    if 'required' in argument_data.keys():

        if not isinstance(argument_data['required'], bool):
            error_dict['required'] = [
                f'Invalid value in required specified on {key} argument. required can be true or false'
            ]


def validate_type(key, argument_data, error_dict):
    # Type is optional
    if 'type' in argument_data.keys():

        render_types_choices = [type_tuple[0] for type_tuple in render_types]
        type = argument_data['type']
        if type not in render_types_choices:
            error_dict['type'] = [
                f'Invalid value {type} in type specified on {key} argument \
                type can be one of {render_types_choices}'
            ]
            return ''

        if type == 'toggle':
            if 'options' not in argument_data:
                error_dict['type'] = [
                    f'There must be exactly 2 options ("on" and "off") on arguments of type toggle'
                ]
                return ''

            number_of_options = len(argument_data['options'].keys())

            if number_of_options != 2:
                error_dict['type'] = [
                    f'There must be exactly 2 options ("on" and "off") on arguments of type toggle. Received \
                    {number_of_options} options'
                ]
                return ''

            option_names = list(argument_data['options'].keys())

            if option_names not in (['on', 'off'], ['off', 'on']):
                error_dict['type'] = [
                    f'The two options on arguments of type toggle must be named "on" and "off". Received \
                    {", ".join(option_names)}'
                ]
                return ''

        return type


def validate_description(key, argument_data, type, error_dict):
    if 'description' not in argument_data.keys() and type != 'hidden':
        error_dict['argument_description'] = [
            f'Could not find a description for argument {key}. Please provide a description for {key}'
        ]


supported_argument_fields = [
    'default_value',
    'description',
    'key',
    'key_value_separator',
    'options',
    'required',
    'sub_arguments',
    'type',
]


def validate_unsupported_argument_fields(key, argument_data, error_dict):
    for field in argument_data.keys():
        if field not in supported_argument_fields:
            error_dict['unsupported_field'] = [
                f'The argument field {field} on {key} is not valid'
            ]
