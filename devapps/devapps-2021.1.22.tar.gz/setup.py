# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ax',
 'ax.utils',
 'ax.utils.ax_tree',
 'axlib',
 'axlib.ax_tree',
 'devapp',
 'devapp.app_token',
 'devapp.arch',
 'devapp.arch.gitlab',
 'devapp.arch.gitlab.solution.conf',
 'devapp.components',
 'devapp.lib',
 'devapp.operations',
 'devapp.plugins.ops_devapp',
 'devapp.plugins.ops_devapp.arch',
 'devapp.spec',
 'devapp.testing',
 'devapp.tests',
 'devapp.utils',
 'mdvl',
 'structlogging',
 'structlogging.tests',
 'theming',
 'theming.filesize',
 'theming.formatting',
 'theming.tests',
 'tree_builder',
 'tree_builder.arch']

package_data = \
{'': ['*'],
 'devapp': ['third/*'],
 'devapp.arch.gitlab': ['solution/*'],
 'devapp.spec': ['templates/*']}

install_requires = \
['PyJWT',
 'PyYAML',
 'Pygments',
 'Rx',
 'absl-py',
 'bpytop',
 'cffi>=1.15.0,<2.0.0',
 'decorator',
 'gevent',
 'httpx',
 'humanize',
 'inflection',
 'jsondiff',
 'lz4',
 'msgpack',
 'psutil',
 'pycond',
 'requests',
 'snoop',
 'structlog',
 'tabulate',
 'toml',
 'ujson']

entry_points = \
{'console_scripts': ['app = devapp.plugin_tools:main',
                     'ops = devapp.plugin_tools:main']}

setup_kwargs = {
    'name': 'devapps',
    'version': '2021.1.22',
    'description': 'Apps - End to End.',
    'long_description': '# devapps\n\n\n<!-- badges -->\n[![docs pages][docs pages_img]][docs pages] [![gh-ci][gh-ci_img]][gh-ci] [![pkg][pkg_img]][pkg] [![code_style][code_style_img]][code_style] \n\n[docs pages]: https://axgkl.github.io/devapps/\n[docs pages_img]: https://axgkl.github.io/devapps/img/badge_docs.svg\n[gh-ci]: https://github.com/AXGKl/devapps/actions/workflows/ci.yml\n[gh-ci_img]: https://github.com/AXGKl/devapps/actions/workflows/ci.yml/badge.svg\n[pkg]: https://pypi.com/artifactory/pypi-ax-sources/devapps/2021.1.22/devapps-2021.1.22.tar.gz\n[pkg_img]: https://axgkl.github.io/devapps/img/badge_pypi.svg\n[code_style]: https://pypi.org/project/axblack/\n[code_style_img]: https://axgkl.github.io/devapps/img/badge_axblack.svg\n<!-- badges -->\n\n\nEnabler repo for dev *and* ops friendly apps, in a normalized way.\n\nIncludes:\n\n- logging (structlog)\n- cli flags handling (abseil, with addons)\n- docutools (mkdocs-material)\n- project setup\n- (test) resources management, including daemons and container filesystem layers\n\nand more.\n\n\n\n\nDocumentation: https://axgkl.github.io/devapps/',
    'author': 'Gunther Klessinger',
    'author_email': 'g_kle_ss_ing_er@gmx.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://axgkl.github.io/devapps',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
