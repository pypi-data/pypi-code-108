# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['oshino_admin']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'click>=8.0.3,<9.0.0',
 'daemonize>=2.5.0,<3.0.0',
 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'oshino-admin',
    'version': '0.2.0',
    'description': '',
    'long_description': 'oshino-admin\n=============\nAdministration module for Oshino.\nShould come bundled together with Oshino itself.\n\nManaging Plugins\n=================\n`oshino-admin plugin list` - lists all available plugins\n\n`oshino-admin plugin install <plugin_name>` - installs requested plugin\n\n`oshino-admin plugin uninstall <plugin_name>` - uninstalls requested plugin\n\nManaging Oshino\n===============\n\n`oshino-admin start --config=config.yaml --pid=oshino.pid` \n\n`oshino-admin status --pid=oshino.pid` \n\n`oshino-admin stop --pid=oshino.pid` \n\nBe aware, that default PID path `/var/run/oshino.pid` might be unaccessible by oshino-admin (Lacking of root permissions).\nCustom pid path can be defined (as show in example above). Main problem is that you need to direct into correct PID for each service command.\n\nGenerating Config\n==================\n`oshino-admin config init <config_name>.yml`\n\nQuerying metrics\n=================\n`oshino-admin query \'tagged "hw"\' --config=config.yaml`\n\nYou can run any query against Riemann using it\'s query DSL language. Short examples:\n`tagged "<tag>"` - retrieves metrics by tag\n`service = "<something>"` - gives metrics by service name. Same can be done for `host` or other keys\n`service =~ "%<something>%"` - `=~` marks that we\'re going to search by wildcard, `%` marks that there can be anything (similar to SQLs `LIKE %something%`)\n',
    'author': 'Šarūnas Navickas',
    'author_email': 'zaibacu@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/CodersOfTheNight/oshino-admin',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
