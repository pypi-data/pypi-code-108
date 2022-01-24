import re

from biolib.validators.validator_utils import AllowedYAMLEnvironments, custom_executors, old_to_new_executors_map  # type: ignore


def validate_module(name, module_data, yaml_version):
    error_dict = {}
    name = validate_name(name, error_dict)
    if not name:
        return error_dict
    error_dict[name] = {}
    task_error_dict = error_dict[name]

    validate_unsupported_task_fields(name, module_data, task_error_dict, yaml_version)
    validate_mappings(name, module_data, task_error_dict, mapping_type='input_files')
    validate_mappings(name, module_data, task_error_dict, mapping_type='output_files')
    validate_mappings(name, module_data, task_error_dict, mapping_type='source_files')
    validate_image(name, module_data, task_error_dict, yaml_version)

    validate_working_directory(name, module_data, task_error_dict)

    # Just return empty dict if we have no errors
    if error_dict[name]:
        return error_dict
    else:
        return {}


def validate_working_directory(name, task_data, error_dict):
    if 'working_directory' in task_data:
        if not task_data['working_directory'].startswith('/'):
            error_dict['working_directory'] = [
                f'Wrong path format on working_directory for {name}. Directory path must be an absolute path'
            ]
            return

        if not task_data['working_directory'].endswith('/'):
            error_dict['working_directory'] = [
                f'Wrong path format on working_directory for {name}. Directories must end in a slash: "/dir/sub_dir/"'
            ]
            return

        if '//' in task_data['working_directory']:
            error_dict['working_directory'] = [
                f'Wrong path format on working_directory for {name}. Directories can not have consecutive slashes"'
            ]


def validate_external_app_format(name, app_version_string, error_dict, yaml_version):
    try:
        split_on_slash = app_version_string.split('/')
        if not len(split_on_slash) == 2:
            if yaml_version == 1:
                error_dict['external_app'] = [
                    f'Wrong format. Tried to interpret {name} as an external-app; \
                    The format should be owner/app:version i.e. "some_user/example_app:2.0.1.'
                ]
            else:
                error_dict['image'] = [
                    f'Wrong format. Tried to interpret {name} as a biolib app; \
                    The format should be owner/app:version i.e. "some_user/example_app:2.0.1.'
                ]
            return None, None, None

        account_handle, app_name_and_version = split_on_slash

        split_on_colon = app_name_and_version.split(':')
        if not len(split_on_slash) == 2:
            if yaml_version == 1:
                error_dict['task'] = [
                    f'Wrong format. Tried to interpret {name} as an external-app; \
                    The format should be owner/app:version i.e. "some_user/example_app:2.0.1.'
                ]
            else:
                error_dict['image'] = [
                    f'Wrong format. Tried to interpret {name} as a biolib app; \
                    The format should be owner/app:version i.e. "some_user/example_app:2.0.1.'
                ]
            return None, None, None

        app_name, version = split_on_colon
        return account_handle, app_name, version

    except:
        if yaml_version == 1:
            error_dict['external_app'] = [
                f'Wrong format. Tried to interpret {name} as an external-app; \
                The format should be owner/app:version i.e. "some_user/example_app:2.0.1.'
            ]
        else:
            error_dict['image'] = [
                f'Wrong format. Tried to interpret {name} as an external-app; \
                The format should be owner/app:version i.e. "some_user/example_app:2.0.1.'
            ]

        return None, None, None


def validate_name(name, error_dict):
    # TODO: Refactor this to use a version of is_alphanumeric that allows control of the error message.
    if not re.match("^[A-Za-z0-9_-]+$", name):
        error_dict[name] = [f'The module name {name} is invalid, it can only contain alphanumeric characters.']
        return

    if re.search("(--)|(__)|(-_)|(_-)", name):
        error_dict[name] = [f'The module name {name} is invalid, it can not contain consecutive dashes or underscores']
        return

    if re.match("^(-|_)[A-Za-z0-9_-]+$", name):
        error_dict[name] = [f'The module name {name} is invalid, it can not start with dashes or underscores']
        return

    if re.match("^[A-Za-z0-9_-]+(-|_)$", name):
        error_dict[name] = [f'The module name {name} is invalid, it can not end with dashes or underscores']
        return

    return name


def validate_executor(name, task_data, error_dict):
    if 'executor' not in task_data.keys():
        error_dict['executor'] = [
            'You must define an executor in your module definition; \
            Make sure you follow the format executor_name:version'
        ]
        return

    if task_data['executor'].count(':') != 1:
        error_dict['executor'] = [
            f'Executor {task_data["executor"]} on module {name} is invalid. Please only use ":" to separate to and from paths i.e. "from:to".'
        ]
        return

    executor, version = task_data['executor'].split(':')
    if executor not in old_to_new_executors_map.keys():
        error_dict['executor'] = [
            f'You provided an invalid executor in module {name}; \
            Make sure you follow the format executor_name:version'
        ]

    new_executor_name = old_to_new_executors_map[executor]
    supported_versions = custom_executors[new_executor_name]['versions'] + ['*']
    if version not in supported_versions:
        error_dict['image'] = [
            f'Invalid version for executor {executor} on module {name}. The supported versions for {executor} are {supported_versions}'
        ]
        return


def validate_mappings(name, task_data, error_dict, mapping_type):
    """
    Shared validation function for input and output mappings.
    """
    if mapping_type not in task_data:
        error_dict[mapping_type] = [
            f'{mapping_type} field on module {name} is required. Please specify your {mapping_type}.'
        ]
        return

    if not isinstance(task_data[mapping_type], list):
        error_dict[mapping_type] = [
            f'{mapping_type} field on module {name} is invalid. Please format the field as a yaml array.'
        ]
        return

    for mapping in task_data.get(mapping_type):
        mapping_parts = mapping.split(' ')
        if len(mapping_parts) != 3:
            error_dict[mapping_type] = [
                f'{mapping_type} item {mapping} on module {name} is invalid. Please use the format "COPY from_path to_path" i.e. "COPY / /home/biolib/"'
            ]
            return

        if mapping_parts[0] != 'COPY':
            error_dict[mapping_type] = [
                f'{mapping_type} item {mapping} on module {name} is missing the COPY command. Please use the format "COPY from_path to_path" i.e. "COPY / /home/biolib/"'
            ]
            return

        from_path = mapping_parts[1]
        to_path = mapping_parts[2]

        if '$' in re.sub(r"\$[1-9][0-9]*", "", from_path):
            error_dict[mapping_type] = [
                f'{mapping_type} item {mapping} on module {name} in path "{from_path}" is using an invalid variable. \
Please only use variables referring to an argument number, where "$1" refers to the first argument \
i.e. "COPY $1 /home/biolib/$1"'
            ]
            return

        if '$' in re.sub(r"\$[1-9][0-9]*", "", to_path):
            error_dict[mapping_type] = [
                f'{mapping_type} item {mapping} on module {name} in path "{to_path}" is using an invalid variable. \
Please only use variables referring to an argument number, where "$1" refers to the first argument \
i.e. "COPY $1 /home/biolib/$1"'
            ]
            return

        # Check that we don't map a directory to a file
        to_path_with_vars_replaced_with_dollar = re.sub("\$[0-9]+", "$", to_path)
        if from_path.endswith('/') and (not to_path.endswith('/') and
                                        not to_path_with_vars_replaced_with_dollar.endswith('$')):
            error_dict[mapping_type] = [
                f'{mapping_type} item {mapping} on module {name} is invalid. Directories can only map to other directories'
            ]
            return

        if not to_path.startswith('/') and not to_path.startswith('$'):
            error_dict[mapping_type] = [
                f'{mapping_type} item {mapping} on module {name} on path "{to_path}" is invalid. Only absolute paths allowed'
            ]
            return

        if not from_path.startswith('/') and not from_path.startswith('$'):
            error_dict[mapping_type] = [
                f'{mapping_type} item {mapping} on module {name} on path "{from_path}" is invalid. Only absolute paths allowed'
            ]
            return

        if '//' in from_path or '//' in to_path:
            error_dict[mapping_type] = [
                f'{mapping_type} item {mapping} on module {name} is invalid. Directories can not have consecutive slashes'
            ]


def validate_image(name, task_data, error_dict, yaml_version):
    if 'image' not in task_data:
        error_dict['image'] = [
            f'You must define an image to use for module {name}.'
        ]
        return

    image = task_data['image']
    if '://' not in image:
        error_dict['image'] = [
            f'Wrong image format on module {name}. You must define an image using the following format "environment://image_name:version"'
        ]
        return

    environment = image.split('://')[0]
    if environment not in AllowedYAMLEnvironments.values():
        error_dict['image'] = [
            f'Wrong environment on image of module {name}. The environment should be specified before "://" and can be only be one of {AllowedYAMLEnvironments.values()}'
        ]

    if image.startswith(f'{AllowedYAMLEnvironments.BIOLIB_APP.value}://biolib/'):
        # Image is a biolib custom executor
        uri = image.replace(f'{AllowedYAMLEnvironments.BIOLIB_APP.value}://biolib/', '', 1)
        if uri.count(':') != 1:
            error_dict['image'] = [
                f'Missing version on the image of module {name}. A version must be specified at the end of the image like so: "environment://image_name:version"'
            ]
            return

        executor, version = uri.split(':')
        # Check if the executor is supported
        if executor not in custom_executors.keys():
            error_dict['image'] = [
                f'Invalid image name biolib/{executor} for biolib executor on module {name}. The supported biolib executors are {["biolib/" + executor for executor in custom_executors.keys()]}'
            ]
            return

        # Check if the supplied version for the executor is supported
        supported_versions = custom_executors[executor]['versions'] + ['*']
        if version not in supported_versions:
            error_dict['image'] = [
                f'Invalid version for biolib executor {executor} on module {name}. The supported versions for {executor} are {supported_versions}'
            ]
            return

    elif environment == AllowedYAMLEnvironments.BIOLIB_APP.value:
        app_version_string = image.split('://')[1]
        # validate_external_app(name, app_version_string, user, error_dict, yaml_version)

    elif environment in (AllowedYAMLEnvironments.DOCKERHUB.value, AllowedYAMLEnvironments.LOCAL_DOCKER.value):
        repo_and_tag = image.split('://')[1]
        if not repo_and_tag.count(':', 1):
            error_dict['image'] = [
                f'Invalid docker image on module {name}. A tag must be included in your image with format repo:tag i.e. alpine:latest'
            ]
            return


# Task fields shared between all versions
supported_task_fields_base = [
    'working_directory',
]

supported_task_fields_v1 = [
    'executor',
    'path'
]

supported_task_fields_v2 = [
    'image',
    'input_files',
    'output_files',
    'source_files',
    'command',
]


def validate_unsupported_task_fields(name, task_data, error_dict, yaml_version):
    # If we need to validate module fields, i.e. the module is not a string in v1, then it has to be a dict
    if not isinstance(task_data, dict):
        error_dict['unsupported_fields'] = [
            f'Module {name} is the wrong type. Modules can only be a YAML dict in version {yaml_version}']
        return

    if yaml_version == 1:
        supported_fields = supported_task_fields_base + supported_task_fields_v1
    else:
        supported_fields = supported_task_fields_base + supported_task_fields_v2

    errors = []
    for field in task_data.keys():
        if field not in supported_fields:
            errors.append(
                f'The module field {field} on {name} is not valid for biolib yaml version {yaml_version}'
            )

    if errors:
        error_dict['unsupported_fields'] = errors
