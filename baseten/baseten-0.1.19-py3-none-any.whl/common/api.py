import configparser
import functools
import json
import logging
import os
import tarfile
import tempfile
from typing import IO, Dict, List

import requests
from colorama import Fore, Style
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
from tqdm import tqdm

from baseten.common import settings
from baseten.common.core import ARTIFACT_FILENAME, ApiError, AuthorizationError
from baseten.common.util import base64_encoded_json_str

logger = logging.getLogger(__name__)


def with_api_key(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        config = settings.read_config()
        try:
            api_key = config.get('api', 'api_key')
        except configparser.NoOptionError:
            raise AuthorizationError('You must first run the `baseten login` cli command.')
        result = func(api_key, *args, **kwargs)
        return result
    return wrapper


@with_api_key
def models(api_key):
    query_string = '''
    {
      models {
        id,
        name
      }
    }
    '''

    resp = _post_graphql_query(api_key, query_string)
    return resp['data']


@with_api_key
def create_model_from_scaffold(
    api_key,
    model_name,
    s3_key,
    model_framework,
    model_type,
    model_framework_req,
    dockerfile,
    build_args,
    semver_bump
):
    encoded_model_framework_req = base64_encoded_json_str(model_framework_req)
    encoded_build_args = base64_encoded_json_str(build_args)
    query_string = f'''
    mutation {{
      create_model_from_scaffold(name: "{model_name}"
                   s3_key: "{s3_key}",
                   model_framework: "{model_framework}",
                   model_type: "{model_type}",
                   semver_bump: "{semver_bump}",
                   encoded_model_framework_req: "{encoded_model_framework_req}",
                   dockerfile: "{dockerfile}"
                   encoded_build_args: "{encoded_build_args}"
      ) {{
        id,
        name,
        version_id
      }}
    }}
    '''

    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['create_model_from_scaffold']


@with_api_key
def create_model_version_from_scaffold(
    api_key,
    model_id,
    s3_key,
    model_framework,
    model_type,
    model_framework_req,
    dockerfile,
    build_args,
    semver_bump
):
    encoded_model_framework_req = base64_encoded_json_str(model_framework_req)
    encoded_build_args = base64_encoded_json_str(build_args)
    query_string = f'''
    mutation {{
      create_model_version_from_scaffold(
                   model_id: "{model_id}"
                   s3_key: "{s3_key}",
                   model_framework: "{model_framework}",
                   model_type: "{model_type}",
                   semver_bump: "{semver_bump}",
                   encoded_model_framework_req: "{encoded_model_framework_req}",
                   dockerfile: "{dockerfile}"
                   encoded_build_args: "{encoded_build_args}"
      ) {{
        id,
        name,
        version_id
      }}
    }}
    '''

    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['create_model_version_from_scaffold']


@with_api_key
def create_model(api_key,
                 model_name,
                 s3_key,
                 model_framework,
                 model_type,
                 input_shape,
                 feature_names,
                 feature_summary,
                 class_labels,
                 model_framework_req,
                 semver_bump,
                 model_files_dict):
    encoded_input_shape = base64_encoded_json_str(input_shape)
    encoded_feature_names = base64_encoded_json_str(feature_names)
    encoded_feature_summary = base64_encoded_json_str(feature_summary)
    encoded_class_labels = base64_encoded_json_str(class_labels)
    encoded_model_framework_req = base64_encoded_json_str(model_framework_req)
    encoded_model_files_dict = base64_encoded_json_str(model_files_dict)
    if not model_name:
        import coolname
        model_name = coolname.generate_slug(2)
    query_string = f'''
    mutation {{
      create_model(name: "{model_name}"
                   s3_key: "{s3_key}",
                   model_framework: "{model_framework}",
                   model_type: "{model_type}",
                   semver_bump: "{semver_bump}",
                   encoded_input_shape: "{encoded_input_shape}",
                   encoded_feature_names: "{encoded_feature_names}",
                   encoded_feature_summary: "{encoded_feature_summary}",
                   encoded_class_labels: "{encoded_class_labels}",
                   encoded_model_framework_req: "{encoded_model_framework_req}"
                   encoded_model_files_dict: "{encoded_model_files_dict}"
      ) {{
        id,
        name,
        version_id
      }}
    }}
    '''

    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['create_model']


@with_api_key
def models_versions(api_key, model_id):
    query_string = f'''
    {{
      model(id: "{model_id}") {{
        versions {{
          id,
          s3_key,
          feature_names,
          feature_summary
        }}
      }}
    }}
    '''

    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['model']


@with_api_key
def model_version_input_shape(api_key, model_version_id):
    query_string = f'''
    {{
      model_version(id: "{model_version_id}") {{
        input_shape
      }}
    }}
    '''

    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['model_version']['input_shape']


@with_api_key
def create_model_version(api_key,
                         model_id,
                         s3_key,
                         model_framework,
                         model_type,
                         input_shape,
                         feature_names,
                         feature_summary,
                         class_labels,
                         model_framework_req,
                         semver_bump,
                         model_files_dict):
    encoded_input_shape = base64_encoded_json_str(input_shape)
    encoded_feature_names = base64_encoded_json_str(feature_names)
    encoded_feature_summary = base64_encoded_json_str(feature_summary)
    encoded_class_labels = base64_encoded_json_str(class_labels)
    encoded_model_framework_req = base64_encoded_json_str(model_framework_req)
    encoded_model_files_dict = base64_encoded_json_str(model_files_dict)
    query_string = f'''
    mutation {{
      create_model_version(model_id: "{model_id}",
                           s3_key: "{s3_key}",
                           model_framework: "{model_framework}",
                           model_type: "{model_type}",
                           semver_bump: "{semver_bump}",
                           encoded_input_shape: "{encoded_input_shape}",
                           encoded_feature_names: "{encoded_feature_names}",
                           encoded_feature_summary: "{encoded_feature_summary}",
                           encoded_class_labels: "{encoded_class_labels}",
                           encoded_model_framework_req: "{encoded_model_framework_req}"
                           encoded_model_files_dict: "{encoded_model_files_dict}") {{
        id,
        s3_key,
        feature_names,
        feature_summary
      }}
    }}
    '''

    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['create_model_version']


@with_api_key
def create_model_configuration(
    api_key: str,
    configuration: dict,
    model_id: str = None,
    model_version_id: str = None,
):
    # encode for None/null
    encoded_configuration = base64_encoded_json_str(configuration)

    model_identifier_field = None
    if model_id:
        model_identifier_field = f'model_id: "{model_id}"'
    elif model_version_id:
        model_identifier_field = f'model_version_id: "{model_version_id}"'
    else:
        raise ValueError('Either model_version_id or model_id must be specified.')

    query_string = f'''
    mutation {{
        create_model_configuration(
            encoded_configuration: "{encoded_configuration}",
            {model_identifier_field}
        )
        {{
            configuration_id: id,
        }}
    }}
    '''
    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['create_model_configuration']


@with_api_key
def model_version_configuration(api_key, model_version_id):
    query_string = f'''
    {{
      model_version(id: "{model_version_id}") {{
        configuration
      }}
    }}
    '''

    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['model_version']['configuration']


@with_api_key
def model_configuration(api_key, model_id):
    query_string = f'''
    {{
      model(id: "{model_id}") {{
        configuration
      }}
    }}
    '''

    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['model']['configuration']


@with_api_key
def create_model_metrics(
    api_key: str,
    metric_data: dict,
    model_id: str = None,
    model_version_id: str = None,
):
    # encode for None/null
    encoded_metric_data = base64_encoded_json_str(metric_data)

    model_identifier_field = None
    if model_id:
        model_identifier_field = f'model_id: "{model_id}"'
    elif model_version_id:
        model_identifier_field = f'model_version_id: "{model_version_id}"'
    else:
        raise ValueError('Either model_version_id or model_id must be specified.')

    query_string = f'''
    mutation {{
        create_model_metrics(
            encoded_metric_data: "{encoded_metric_data}",
            {model_identifier_field}
        )
        {{
            metrics_id: id,
        }}
    }}
    '''
    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['create_model_metrics']


@with_api_key
def model_version_metrics(api_key, model_version_id):
    query_string = f'''
    {{
      model_version(id: "{model_version_id}") {{
        metrics
      }}
    }}
    '''

    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['model_version']['metrics']


@with_api_key
def model_metrics(api_key, model_id):
    query_string = f'''
    {{
      model(id: "{model_id}") {{
        metrics
      }}
    }}
    '''

    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['model']['metrics']


@with_api_key
def signed_s3_upload_post(api_key, model_file_name):
    query_string = f'''
    {{
      signed_s3_upload_url(model_file_name: "{model_file_name}") {{
        url,
        form_fields {{
          key,
          aws_access_key_id,
          policy,
          signature,
        }}
      }}
    }}
    '''

    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['signed_s3_upload_url']


@with_api_key
def artifact_signed_s3_upload_post(api_key, file_name, file_size):
    query_string = f'''
    {{
      artifact_signed_s3_upload_url(file_name: "{file_name}", file_size: {file_size}) {{
        url,
        form_fields {{
          key,
          aws_access_key_id,
          policy,
          signature,
        }}
      }}
    }}
    '''

    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['artifact_signed_s3_upload_url']


@with_api_key
def register_data_for_model(api_key, s3_key, model_version_id, data_name):
    query_string = f'''
    mutation {{
        create_sample_data_file(model_version_id: "{model_version_id}",
                                name: "{data_name}",
                                s3_key: "{s3_key}") {{
          id
        }}
    }}
    '''
    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['create_sample_data_file']


@with_api_key
def create_artifact(
    api_key: str,
    s3_key: str,
    name: str,
    description: str = None,
    model_id: str = None,
    model_version_id: str = None,
):
    # encode for None/null
    description = base64_encoded_json_str(description)
    model_id = base64_encoded_json_str(model_id)
    model_version_id = base64_encoded_json_str(model_version_id)

    query_string = f'''
    mutation {{
        create_artifact(
            name: "{name}",
            s3_key: "{s3_key}",
            encoded_description: "{description}",
            encoded_model_id: "{model_id}",
            encoded_model_version_id: "{model_version_id}"
        )
        {{
            artifact_id: id,
            name,
            description
        }}
    }}
    '''
    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['create_artifact']


@with_api_key
def create_artifact_link(
    api_key: str,
    artifact_id: str,
    model_id: str = None,
    model_version_id: str = None,
):
    # encode for None/null
    model_id = base64_encoded_json_str(model_id)
    model_version_id = base64_encoded_json_str(model_version_id)

    query_string = f'''
    mutation {{
        link_artifact(
            id: "{artifact_id}",
            encoded_model_id: "{model_id}",
            encoded_model_version_id: "{model_version_id}"
        )
        {{
            id
        }}
    }}
    '''
    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['link_artifact']


@with_api_key
def delete_artifact(
    api_key: str,
    artifact_id: str,
):
    query_string = f'''
    mutation {{
        delete_artifact(
            artifact_id: "{artifact_id}",
        )
        {{
            ok
        }}
    }}
    '''
    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['delete_artifact']


@with_api_key
def update_artifact(
    api_key: str,
    artifact_id: str,
    name: str = None,
    description: str = None,
    s3_key: str = None,
):
    update_str = ''
    if name:
        update_str += f'name: "{name}",\n'
    if description:
        update_str += f'description: "{description}",\n'
    if s3_key:
        update_str += f's3_key: "{s3_key}",\n'

    query_string = f'''
    mutation {{
        update_artifact(
            artifact_id: "{artifact_id}",
            {update_str}
        )
        {{
            id
            name
            description
        }}
    }}
    '''
    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['update_artifact']


@with_api_key
def artifact_url(
    api_key: str,
    artifact_id: str,
):
    query_string = f'''{{
        artifact(
            id: "{artifact_id}",
        )
        {{
            id, url
        }}
    }}
    '''
    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['artifact']['url']


@with_api_key
def artifact_links(
    api_key: str,
    artifact_id: str,
):
    query_string = f'''{{
        artifact(
            id: "{artifact_id}",
        )
        {{
            model_ids: oracle_ids
            model_version_ids: oracle_version_ids
        }}
    }}
    '''
    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['artifact']


@with_api_key
def model_linked_artifacts(
    api_key: str,
    model_id: str,
):
    query_string = f'''{{
        model(
            id: "{model_id}",
        )
        {{
            artifacts {{
                artifact_id: id,
                name,
                description
            }}
        }}
    }}
    '''
    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['model']['artifacts']


@with_api_key
def model_version_linked_artifacts(
    api_key: str,
    model_version_id: str,
):
    query_string = f'''{{
        model_version(
            id: "{model_version_id}",
        )
        {{
            artifacts {{
                artifact_id: id,
                name,
                description
            }}
        }}
    }}
    '''
    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['model_version']['artifacts']


@with_api_key
def predict_for_model(api_key, model_id: str, inputs: list, metadata: List[Dict] = None) -> List[List]:
    """Call the model's predict given the input json.

    Args:
        api_key (str)
        model_id (str)
        inputs (list)
        metadata (List[Dict]): Metadata key/value pairs (e.g. name, url), one for each input.

    Raises:
        RequestException: If there was an error communicating with the server.
    """
    predict_url = f'{settings.API_URL_BASE}/models/{model_id}/predict'
    return _predict(api_key, predict_url, inputs, metadata)


@with_api_key
def predict_for_model_version(api_key, model_version_id: str, inputs: list, metadata: List[Dict] = None) -> List[List]:
    """Call the model version's predict given the input json.

    Args:
        api_key (str)
        model_version_id (str)
        inputs (list)
        metadata (List[Dict]): Metadata key/value pairs (e.g. name, url), one for each input.

    Raises:
        RequestException: If there was an error communicating with the server.
    """
    predict_url = f'{settings.API_URL_BASE}/model_versions/{model_version_id}/predict'
    return _predict(api_key, predict_url, inputs, metadata)


@with_api_key
def set_primary(api_key, model_version_id: str):
    """Promote this version of the model as the primary version.

    Args:
        api_key (str)
        model_version_id (str)
    """
    query_string = f'''
    mutation {{
      update_model_version(model_version_id: "{model_version_id}", is_primary: true) {{
        id,
        is_primary,
      }}
    }}
    '''
    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['update_model_version']


@with_api_key
def update_model_features(api_key, model_version_id: str, feature_names: list, class_labels: list = None):
    """Update the feature names for the model.

    Args:
        api_key (str)
        model_version_id (str)
        feature_names (list)
        class_labels (Optional[list]): applies only to classifiers.
    """
    encoded_feature_names = base64_encoded_json_str(feature_names)
    encoded_class_labels = base64_encoded_json_str(class_labels)
    query_string = f'''
    mutation {{
      update_model_version(model_version_id: "{model_version_id}",
                           encoded_feature_names: "{encoded_feature_names}",
                           encoded_class_labels: "{encoded_class_labels}") {{
        id,
        feature_names,
      }}
    }}
    '''
    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['update_model_version']


@with_api_key
def install_requirements(api_key, requirements_txt):
    escaped_requirements_txt = requirements_txt.replace('\n', '\\n')  # Otherwise the mutation becomes invalid graphql.
    query_string = f'''
    mutation {{
      create_pynode_requirement(requirements_txt: "{escaped_requirements_txt}") {{
        id
        status
        error_message
      }}
    }}
    '''
    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['create_pynode_requirement']


@with_api_key
def requirement_status(api_key, requirement_id):
    query_string = f'''
    {{
      pynode_requirement(id: "{requirement_id}") {{
        id
        status
        error_message
      }}
    }}
    '''

    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['pynode_requirement']


def _predict(api_key, predict_url: str, inputs: list, metadata: List[Dict] = None) -> List[List]:
    resp = _post_rest_query(api_key, predict_url, {'inputs': inputs, 'metadata': metadata})
    resp_json = json.loads(resp.content)
    return resp_json['predictions']


def _headers(api_key):
    return {'Authorization': f'Api-Key {api_key}'}


def _post_graphql_query(api_key, query_string) -> dict:
    resp = requests.post(f'{settings.API_URL_BASE}/graphql/', data={'query': query_string}, headers=_headers(api_key))
    if not resp.ok:
        logger.error(f'GraphQL endpoint failed with error: {resp.content}')
        resp.raise_for_status()
    resp_dict = resp.json()
    errors = resp_dict.get('errors')
    if errors:
        raise ApiError(errors[0]['message'], resp)
    return resp_dict


def _post_rest_query(api_key, url, post_body_dict):
    resp = requests.post(url, json=post_body_dict, headers=_headers(api_key))
    resp.raise_for_status()
    return resp


def upload_model(serialize_file: IO, file_ext: str, file_name: str) -> str:
    """Uploads the serialized model to the appropriate environment

    Args:
        serialize_file (file): A file-like object that is the serialized representation of the model object.
        file_ext (str): The file extension for the saved model

    Returns:
        str: The key for the uploaded model

    Raises:
        RequestException: If there was an error communicating with the server.
    """

    model_file_name = f'{file_name}.{file_ext}'
    this_signed_s3_upload_post = signed_s3_upload_post(model_file_name)
    logger.debug(f'Signed s3 upload post:\n{json.dumps(this_signed_s3_upload_post, indent=4)}')

    form_fields = this_signed_s3_upload_post['form_fields']
    form_fields['AWSAccessKeyId'] = form_fields.pop('aws_access_key_id')  # S3 expects key name AWSAccessKeyId
    form_fields['file'] = (file_name, serialize_file)
    logger.info('🚀 Uploading model to BaseTen 🚀')

    return _upload_file(this_signed_s3_upload_post, form_fields)


def upload_artifact(serialize_file: IO, file_ext: str, file_name: str, file_size: int) -> str:
    """Uploads the serialized artifact to the appropriate environment

    Args:
        serialize_file (file): A file-like object that is the serialized representation of the artifact object.
        file_ext (str): The file extension for the saved artifact

    Returns:
        str: The key for the uploaded artifact

    Raises:
        RequestException: If there was an error communicating with the server.
    """
    artifact_file_name = f'{file_name}.{file_ext}'
    this_signed_s3_upload_post = artifact_signed_s3_upload_post(artifact_file_name, file_size)
    logger.debug(f'Signed s3 upload post:\n{json.dumps(this_signed_s3_upload_post, indent=4)}')

    form_fields = this_signed_s3_upload_post['form_fields']
    form_fields['AWSAccessKeyId'] = form_fields.pop('aws_access_key_id')  # S3 expects key name AWSAccessKeyId
    form_fields['file'] = (file_name, serialize_file)
    logger.info('🚀 Uploading artifact to BaseTen 🚀')

    return _upload_file(this_signed_s3_upload_post, form_fields)


def _upload_file(this_signed_s3_upload_post: dict, form_fields: dict) -> str:
    encoder = MultipartEncoder(fields=form_fields)
    encoder_len = encoder.len
    pbar = tqdm(total=encoder_len, unit_scale=True,
                bar_format="Upload Progress: {percentage:3.0f}%% |%s{bar:100}%s| {n_fmt}/{total_fmt}"
                % (Fore.BLUE, Fore.RESET))

    def callback(monitor):
        progress = monitor.bytes_read - pbar.n
        pbar.update(progress)

    monitor = MultipartEncoderMonitor(encoder, callback)
    resp = requests.post(
        this_signed_s3_upload_post['url'], data=monitor, headers={'Content-Type': monitor.content_type}
    )
    resp.raise_for_status()
    pbar.close()
    logger.info('🔮 Upload successful!🔮')

    logger.debug(f'File upload HTTP status code: {resp.status_code} and content:\n{resp.content}')

    return this_signed_s3_upload_post['form_fields']['key']


def _tar_a_list_of_files(list_of_files: List[str]) -> tempfile.NamedTemporaryFile:
    temp_file = tempfile.NamedTemporaryFile(suffix='.tgz')
    with tarfile.open(temp_file.name, 'w:gz') as tar:
        for file in list_of_files:
            tar.add(file)
    temp_file.file.seek(0)
    return temp_file


def serialize_artifact_to_s3(name, list_of_files):
    logger.info(f'Serializing {Fore.BLUE}{name}{Style.RESET_ALL} artifact.')
    artifact_tgz = _tar_a_list_of_files(list_of_files)
    logger.info('Making contact with BaseTen 👋 👽')
    s3_key = upload_artifact(artifact_tgz, 'tgz', ARTIFACT_FILENAME, os.path.getsize(artifact_tgz.name))
    return s3_key
