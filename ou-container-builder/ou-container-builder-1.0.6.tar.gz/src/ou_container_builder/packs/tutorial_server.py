"""Pack to install the tutorial_sever."""
import os

from jinja2 import Environment

from ..utils import merge_settings


def apply_pack(context: str, env: Environment, settings: dict) -> dict:
    """Apply the tutorial-server pack.

    Ensures that the Tutorial Server is installed and set up via the ``web_apps`` setting.

    :param context: The context path within which the generation is running
    :type context: str
    :param env: The Jinja2 environment to use for loading and rendering templates
    :type env: :class:`~jinja2.environment.Environment`
    :param settings: The settings parsed from the configuration file
    :type settings: dict
    :return: The updated settings
    :rtype: dict
    """
    additional_settings = {
        'packages': {
            'pip': [
                'tutorial-server>=1.0.2',
                'jupyter-server-proxy'
            ]
        },
        'content': [
            {
                'source': 'ou-builder-build/tutorial-server.ini',
                'target': '/etc/tutorial-server/production.ini',
                'overwrite': 'always'
            }
        ],
        'web_apps': [
            {
                'path': 'tutorial-server',
                'cmdline': [
                    'python',
                    '-m',
                    'tutorial_server',
                    '--config=/etc/tutorial-server/production.ini',
                    '--port={port}',
                    '--basepath={base_url}tutorial-server/'
                ],
                'absolute_url': True,
                'default': True
            }
        ]
    }
    if 'tutorial_server' in settings and settings['tutorial_server']['php-cgi']:
        additional_settings['packages']['apt'] = ['php-cgi']
    settings = merge_settings(settings, additional_settings)

    with open(os.path.join(context, 'ou-builder-build', 'tutorial-server.ini'), 'w') as out_f:
        tmpl = env.get_template('packs/tutorial-server/production.ini')
        out_f.write(tmpl.render(**settings))
    return settings
