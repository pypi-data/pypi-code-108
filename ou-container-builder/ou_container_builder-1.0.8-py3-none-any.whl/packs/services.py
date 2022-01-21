"""Pack to setup and run system services."""
import os

from jinja2 import Environment

from ..utils import merge_settings


def apply_pack(context: str, env: Environment, settings: dict) -> dict:
    """Apply the services pack.

    Automatically generates a sudoers file that ensures that the default user can start and stop all services.

    :param context: The context path within which the generation is running
    :type context: str
    :param env: The Jinja2 environment to use for loading and rendering templates
    :type env: :class:`~jinja2.environment.Environment`
    :param settings: The settings parsed from the configuration file
    :type settings: dict
    :return: The updated settings
    :rtype: dict
    """
    settings = merge_settings(settings, {
        'content': [
            {
                'source': 'ou-builder-build/services.sudoers',
                'target': '/etc/sudoers.d/99-services',
                'overwrite': 'always'
            }
        ],
        'flags': {
            'ou_container_content': True
        }
    })
    with open(os.path.join(context, 'ou-builder-build', 'services.sudoers'), 'w') as out_f:
        tmpl = env.get_template('packs/services/sudoers')
        out_f.write(tmpl.render(**settings))
    return settings
