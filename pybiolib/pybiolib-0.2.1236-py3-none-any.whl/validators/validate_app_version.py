import io
import re
from zipfile import ZipFile

from biolib.validators import validator_utils  # type: ignore


def validate_app_version(yaml_data, yaml_version, zip_file):
    files = [filename.strip('/') for filename in zip_file.namelist()]

    error_dict = {}
    validate_unsupported_root_level_fields(yaml_data, error_dict, yaml_version)
    validate_output_type(yaml_data, error_dict)
    validate_consumes_stdin(yaml_data, error_dict)
    validate_remote_hosts(yaml_data, error_dict)
    validate_description_file(yaml_data, files, zip_file, error_dict)
    validate_license_file(yaml_data, files, zip_file, error_dict)
    return error_dict


def validate_output_type(yaml_data, error_dict):
    # output_type is not required
    if 'output_type' in yaml_data.keys():
        output_type = yaml_data['output_type']
        stdout_render_types_choices = [type_tuple[0] for type_tuple in validator_utils.stdout_render_types]
        if output_type not in stdout_render_types_choices:
            error_dict['output_type'] = [
                f'Invalid output_type specified for your app. output_type can be one of {stdout_render_types_choices}'
            ]


def validate_consumes_stdin(yaml_data, error_dict):
    if 'consumes_stdin' in yaml_data.keys():
        consumes_stdin = yaml_data['consumes_stdin']
        if not isinstance(consumes_stdin, bool):
            error_dict['consumes_stdin'] = [
                f'Invalid consumes_stdin specified for your app. consumes_stdin can be true or false'
            ]


def validate_remote_hosts(yaml_data, error_dict):
    if 'remote_hosts' in yaml_data.keys():
        for hostname in yaml_data['remote_hosts']:
            # No error message is returned if the hostname is valid
            hostname_error_message = validator_utils.validate_hostname_and_return_error_message(hostname)
            if hostname_error_message:
                error_dict['remote_hosts'] = hostname_error_message


def validate_description_file(yaml_data, files, zip_file: ZipFile, error_dict):
    # Only check existence of description file if user specified it
    if 'description_file' in yaml_data.keys():
        description_path = yaml_data['description_file']

        if description_path not in files:
            error_dict['description_file'] = [
                f'Could not find description file at {description_path}. \
Please provide a path pointing to a markdown (.md) file'
            ]
        return

    else:
        description_path = 'README.md'

    if description_path in files:
        # TODO: Discuss this limit, seems very high :sweat:
        # Check if description file is bigger than 100MB, written as 100000000 bytes
        if zip_file.getinfo(description_path).file_size > 100000000:
            error_dict['description_file'] = [f'The description file {description_path} must be less than 100MB']

        validate_description_images(zip_file.open(description_path), files, zip_file, error_dict)


def validate_license_file(yaml_data, files, zip_file, error_dict):
    if 'license_file' in yaml_data.keys():
        license_path = yaml_data['license_file']

        if license_path not in files:
            error_dict['license_file'] = [
                f'Could not find license file at {license_path}. Please provide a path pointing to a license file'
            ]
            return

    else:
        license_path = 'LICENSE'

    if license_path in files:
        # Check if license file is bigger than 100MB, written as 100000000 bytes
        if zip_file.getinfo(license_path).file_size > 100000000:
            error_dict['license_file'] = [f'The license file {license_path} must be less than 100MB']


def validate_is_open_source(yaml_data, error_dict):
    if 'is_open_source' in yaml_data.keys():
        if not isinstance(yaml_data['is_open_source'], bool):
            error_dict['is_open_source'] = [
                f'Invalid is_open_source specified for your app. is_open_source can be true or false'
            ]


supported_root_level_fields_base = [
    'arguments',
    'biolib_version',
    'citation',
    'consumes_stdin',
    'description_file',
    'license_file',
    'modules',
    'output_type',
    'remote_hosts',
]

supported_root_level_fields_v1 = [
    'client_side_include',
]

supported_root_level_fields_v2 = [
    'source_files_ignore',
]


def validate_unsupported_root_level_fields(yaml_data, error_dict, yaml_version):
    if yaml_version == 1:
        supported_fields = supported_root_level_fields_base + supported_root_level_fields_v1
    else:
        supported_fields = supported_root_level_fields_base + supported_root_level_fields_v2

    errors = []
    for field in yaml_data.keys():
        if field not in supported_fields:
            errors.append(
                f'The field {field} is not valid'
            )

    if errors:
        error_dict['unsupported_fields'] = errors


def validate_description_images(description_path, files, zip_file, error_dict):
    REGEX_MARKDOWN_INLINE_IMAGE = re.compile(r'!\[(?P<alt>.*)\]\((?P<src>.*)\)')
    image_filesize_limit_in_bytes = 5000000
    supported_image_file_types = ('png', 'gif', 'jpg', 'jpeg')

    description_images = {}
    description_markdown = io.TextIOWrapper(description_path).read()

    for img_alt, img_src_path in re.findall(REGEX_MARKDOWN_INLINE_IMAGE, description_markdown):

        if img_src_path in description_images:
            continue

        if re.match(r'data:.*;base64,', img_src_path):
            error_dict['description_file'] = [
                'The Markdown description does not support base64 images. '
                'Please specify images using their path in the application files: '
                '![Example Alt Text](path/to/image.png)'
            ]
            return error_dict

        if img_src_path not in files:
            if len(img_src_path) > 200:
                img_src_path = img_src_path[:200] + '...'
            error_dict['description_file'] = [
                f'In the Markdown description the image path {img_src_path} does not exist in application files'
            ]
            return error_dict

        extension = img_src_path.split('.')[-1] if '.' in img_src_path else 'png'
        if extension not in supported_image_file_types:
            error_dict['description_file'] = [
                f'In the Markdown description, the image {img_src_path} '
                f'must point to an image of the following types {supported_image_file_types}.'
            ]
            return error_dict

        # Limit image size
        if zip_file.getinfo(img_src_path).file_size > image_filesize_limit_in_bytes:
            error_dict['description_file'] = [
                f'In the Markdown description, the image {img_src_path} is over '
                f'{image_filesize_limit_in_bytes / 1000000} MB which is too large.'
            ]

        return error_dict
