from pathlib import Path
import yaml

from biolib import cli_utils
from biolib.typing_utils import Optional
from biolib.biolib_api_client import BiolibApiClient
from biolib.biolib_docker_client import BiolibDockerClient
from biolib.biolib_api_client.biolib_app_api import BiolibAppApi
from biolib.biolib_errors import BioLibError
from biolib.biolib_logging import logger
from biolib.utils import get_absolute_container_image_uri


def push_application(app_uri: str, app_path: str, app_version_to_copy_images_from: Optional[str]):
    api_client = BiolibApiClient.get()
    if not api_client.is_signed_in:
        # TODO: Create an exception class for expected errors like this that does not print stacktrace
        raise Exception(
            'You must be authenticated to push an application.\n'
            'Please set the environment variable "BIOLIB_TOKEN=[your_api_token]"\n'
            'You can get an API token at: https://biolib.com/settings/api-tokens/'
        ) from None

    # prepare zip file
    if not Path(f'{app_path}/.biolib/config.yml').is_file():
        raise BioLibError('The file .biolib/config.yml was not found in the application directory')

    tmp_directory, source_files_zip_path = cli_utils.create_temporary_directory_with_source_files_zip(app_path)

    try:
        with open(source_files_zip_path, mode='rb') as zip_file:
            source_files_zip_bytes = zip_file.read()
    except IOError:
        raise Exception('Failed to read temporary source files zip') from None

    try:
        tmp_directory.cleanup()
    except IOError:
        raise Exception('Failed to clean up temporary source files zip directory') from None

    # TODO: Raise exception if app_uri contains version

    if app_version_to_copy_images_from and app_version_to_copy_images_from != 'active':
        # Get app with `app_version_to_copy_images_from` in app_uri to get the app version public id.
        app_uri += f':{app_version_to_copy_images_from}'

    app_response = BiolibAppApi.get_by_uri(app_uri)
    app = app_response['app']
    # push new app version
    new_app_version_json = BiolibAppApi.push_app_version(
        app_id=app['public_id'],
        app_name=app['name'],
        author=app['account_handle'],
        set_as_active=False,
        zip_binary=source_files_zip_bytes,
        app_version_id_to_copy_images_from=app_response['app_version']['public_id'] if app_version_to_copy_images_from
        else None
    )

    #  Don't push docker images if copying from another app version
    docker_tags = new_app_version_json.get('docker_tags', {})
    if not app_version_to_copy_images_from and docker_tags:
        logger.info('Found docker images to push.')

        try:
            yaml_file = open(f'{app_path}/.biolib/config.yml', 'r', encoding='utf-8')

        except Exception as error:  # pylint: disable=broad-except
            raise BioLibError('Could not open the config file .biolib/config.yml') from error

        try:
            config_data = yaml.safe_load(yaml_file)

        except Exception as error:  # pylint: disable=broad-except
            raise BioLibError('Could not parse .biolib/config.yml. Please make sure it is valid YAML') from error

        # Auth to be sent to proxy
        # The tokens are sent as "{access_token},{job_id}". We leave job_id blank on push.
        tokens = f'{BiolibApiClient.get().access_token},'
        auth_config = {'username': 'biolib', 'password': tokens}

        docker_client = BiolibDockerClient.get_docker_client()

        for module_name, repo_and_tag in docker_tags.items():
            docker_image_definition = config_data['modules'][module_name]['image']
            repo, tag = repo_and_tag.split(':')

            if docker_image_definition.startswith('dockerhub://'):
                docker_image_name = docker_image_definition.replace('dockerhub://', 'docker.io/', 1)
                logger.info(
                    f'Pulling image {docker_image_name} defined on module {module_name} from Dockerhub.')
                dockerhub_repo, dockerhub_tag = docker_image_name.split(':')
                docker_client.images.pull(dockerhub_repo, tag=dockerhub_tag, platform='linux/amd64')

            elif docker_image_definition.startswith('local-docker://'):
                docker_image_name = docker_image_definition.replace('local-docker://', '', 1)

            try:
                logger.info(f'Trying to push image {docker_image_name} defined on module {module_name}.')
                image = docker_client.images.get(docker_image_name)
                image_uri = get_absolute_container_image_uri(
                    base_url=api_client.base_url,
                    relative_image_uri=repo
                )
                image.tag(image_uri, tag)
                for line in docker_client.images.push(image_uri, tag=tag, stream=True,
                                                      decode=True, auth_config=auth_config):
                    logger.info(line)

            except Exception as exception:  # pylint: disable=broad-except
                raise BioLibError(f'Failed to tag and push image {docker_image_name}.') from exception

            logger.info(f'Successfully pushed {docker_image_name}')

        logger.info('Successfully pushed all docker images')

    # Set new app version as active
    BiolibAppApi.update_app_version(
        app_version_id=new_app_version_json['public_id'],
        data={
            'set_as_active': True
        }
    )
