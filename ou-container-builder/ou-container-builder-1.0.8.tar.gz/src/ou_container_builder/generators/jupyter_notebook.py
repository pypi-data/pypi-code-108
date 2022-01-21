"""Build containers based on a Jupyter Notebook."""
import os

from jinja2 import Environment

from ou_container_builder.utils import merge_settings


def setup(context: str, env: Environment, settings: dict) -> dict:
    """Run the setup for the Jupyter Notebook generator.

    Merges the required settings for Jupyter Notebooks into the settings.

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
        'packages': {
            'pip': [
                'jupyterhub==1.3.0',
                'notebook>=6.0.0,<7'
            ]
        },
        'content': [
            {
                'source': 'ou-builder-build/start-notebook.sh',
                'target': '/usr/bin/start.sh',
                'overwrite': 'always'
            },
            {
                'source': 'ou-builder-build/jupyter_notebook_config.py',
                'target': '/etc/jupyter/jupyter_notebook_config.py',
                'overwrite': 'always'
            }
        ],
        'scripts': {
            'build': [
                {
                    'commands': [
                        'chmod a+x /usr/bin/start.sh'
                    ]
                }
            ]
        }
    })
    return settings


def generate(context: str, env: Environment, settings: dict):
    """Generate the Dockerfile for a Jupyter Notebook container.

    This generates the ``Dockerfile``, ``jupyter_notebook_config.py``, and ``start-notebook.sh`` files.

    :param context: The context path within which the generation is running
    :type context: str
    :param env: The Jinja2 environment to use for loading and rendering templates
    :type env: :class:`~jinja2.environment.Environment`
    :param settings: The settings parsed from the configuration file
    :type settings: dict
    """
    with open(os.path.join(context, 'ou-builder-build', 'jupyter_notebook_config.py'), 'w') as out_f:
        tmpl = env.get_template('generators/jupyter_notebook/jupyter_notebook_config.py')
        out_f.write(tmpl.render(**settings))

    with open(os.path.join(context, 'ou-builder-build', 'start-notebook.sh'), 'w') as out_f:
        tmpl = env.get_template('generators/jupyter_notebook/start.sh')
        out_f.write(tmpl.render(**settings))

    with open(os.path.join(context, 'Dockerfile'), 'w') as out_f:
        tmpl = env.get_template('Dockerfile.jinja2')
        out_f.write(tmpl.render(**settings))
