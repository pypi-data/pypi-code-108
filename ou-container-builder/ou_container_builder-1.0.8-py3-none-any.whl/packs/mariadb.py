"""Pack to install the MariaDB database."""
import os

from jinja2 import Environment

from ..utils import merge_settings


def apply_pack(context: str, env: Environment, settings: dict) -> dict:
    """Apply the mariadb pack.

    This ensures that the the mariadb service is activated and that the configured database is set up in the user's
    home-directory.

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
            'apt': ['mariadb-server', 'sudo']
        },
        'scripts': {
            'build': [
                {
                    'commands': [
                        'mkdir -p /run/mysqld',
                        'sed -e "s#datadir.*=.*#datadir = $HOME/mariadb#" -e "s#user.*=.*#user = ou#" -i /etc/mysql/mariadb.conf.d/50-server.cnf',  # noqa: E501
                        'chown ou: /var/log/mysql/error.log /run/mysqld',
                        'chmod a+x /usr/bin/mariadb-setup.sh',
                        'printf "ou ALL=NOPASSWD: /usr/bin/mariadb-setup.sh\\n" > /etc/sudoers.d/99-mariadb'  # noqa: E501
                    ]
                },
            ],
            'startup': [
                {
                    'commands': [
                        'sudo /usr/bin/mariadb-setup.sh'
                    ]
                }
            ]
        },
        'services': [
            'mysql'
        ],
        'content': [
            {
                'source': '/var/lib/mysql',
                'target': 'mariadb',
                'overwrite': 'never'
            },
            {
                'source': 'ou-builder-build/mariadb-setup.sh',
                'target': '/usr/bin/mariadb-setup.sh',
                'overwrite': 'always'
            }
        ]
    })
    with open(os.path.join(context, 'ou-builder-build', 'mariadb-setup.sh'), 'w') as out_f:
        tmpl = env.get_template('packs/mariadb/setup.sh')
        out_f.write(tmpl.render(**settings))
    return settings
