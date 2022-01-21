"""Pack to handle setting up content in the container."""
import os

from jinja2 import Environment

from ..utils import merge_settings


def apply_pack(context: str, env: Environment, settings: dict) -> dict:
    """Apply the content pack.

    This ensures that the OU Container Content application is integrated into the container and that all configured
    files are distributed in the container as configured. This also sets the ``ou_container_content`` flag to ensure
    that the OU Container Content application is run upon container startup.

    :param context: The context path within which the generation is running
    :type context: str
    :param env: The Jinja2 environment to use for loading and rendering templates
    :type env: :class:`~jinja2.environment.Environment`
    :param settings: The settings parsed from the configuration file
    :type settings: dict
    :return: The updated settings
    :rtype: dict
    """
    if 'content' in settings and settings['content']:
        settings = merge_settings(settings, {
            'flags': {
                'ou_container_content': True
            }
        })
    if settings['flags'] and settings['flags']['ou_container_content']:
        settings = merge_settings(settings, {
            'packages': {
                'pip': [
                    'ou-container-content>=1.1.0'
                ]
            },
            'scripts': {
                'build': [
                    {
                        'commands': '''ou-container-content prepare'''
                    }
                ]
            }
        })
        with open(os.path.join(context, 'ou-builder-build', 'content_config.yaml'), 'w') as out_f:
            tmpl = env.get_template('content_config.yaml')
            out_f.write(tmpl.render(**settings))
    return settings
