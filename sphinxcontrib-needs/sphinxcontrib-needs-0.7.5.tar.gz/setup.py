# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['sphinxcontrib',
 'sphinxcontrib.needs',
 'sphinxcontrib.needs.api',
 'sphinxcontrib.needs.directives',
 'sphinxcontrib.needs.functions',
 'sphinxcontrib.needs.nodes',
 'sphinxcontrib.needs.roles',
 'sphinxcontrib.needs.services',
 'sphinxcontrib.needs.services.config']

package_data = \
{'': ['*'],
 'sphinxcontrib.needs': ['css/*',
                         'css/blank/*',
                         'css/dark/*',
                         'css/modern/*',
                         'images/*',
                         'images/feather_png/*',
                         'images/feather_svg/*',
                         'libs/html/*',
                         'libs/html/Buttons-1.5.1/css/*',
                         'libs/html/Buttons-1.5.1/js/*',
                         'libs/html/Buttons-1.5.1/swf/*',
                         'libs/html/ColReorder-1.4.1/css/*',
                         'libs/html/ColReorder-1.4.1/js/*',
                         'libs/html/DataTables-1.10.16/css/*',
                         'libs/html/DataTables-1.10.16/images/*',
                         'libs/html/DataTables-1.10.16/js/*',
                         'libs/html/FixedColumns-3.2.4/css/*',
                         'libs/html/FixedColumns-3.2.4/js/*',
                         'libs/html/FixedHeader-3.1.3/css/*',
                         'libs/html/FixedHeader-3.1.3/js/*',
                         'libs/html/JSZip-2.5.0/*',
                         'libs/html/Responsive-2.2.1/css/*',
                         'libs/html/Responsive-2.2.1/js/*',
                         'libs/html/Scroller-1.4.4/css/*',
                         'libs/html/Scroller-1.4.4/js/*',
                         'libs/html/pdfmake-0.1.32/*']}

install_requires = \
['jsonschema==3.2.0',
 'matplotlib>3.1.0',
 'requests-file>=1.5.1,<2.0.0',
 'requests>=2.25.1,<3.0.0',
 'sphinx-data-viewer>=0.1.1,<0.2.0']

extras_require = \
{':python_version >= "3.6" and python_version < "3.7"': ['sphinx>2.2,<=3.0'],
 ':python_version >= "3.7"': ['sphinx>2.2']}

setup_kwargs = {
    'name': 'sphinxcontrib-needs',
    'version': '0.7.5',
    'description': 'Sphinx needs extension for managing needs/requirements and specifications',
    'long_description': '**Complete documentation**: http://sphinxcontrib-needs.readthedocs.io/en/latest/\n\nIntroduction\n============\n\n``Sphinx-Needs`` allows the definition, linking and filtering of class-like need-objects, which are by default:\n\n* requirements\n* specifications\n* implementations\n* test cases.\n\nThis list can be easily customized via configuration (for instance to support bugs or user stories).\n\nA default requirement need looks like:\n\n.. image:: https://raw.githubusercontent.com/useblocks/sphinxcontrib-needs/master/docs/_images/need_1.png\n   :align: center\n\nLayout and style of needs can be highly customized, so that a need can also look like:\n\n.. image:: https://raw.githubusercontent.com/useblocks/sphinxcontrib-needs/master/docs/_images/need_2.png\n   :align: center\n\nTake a look into our `Examples <https://sphinxcontrib-needs.readthedocs.io/en/latest/examples/index.html>`_ for more\npictures and ideas how to use ``Sphinx-Needs``.\n\nFor filtering and analyzing needs, ``Sphinx-Needs`` provides different, powerful possibilities:\n\n.. list-table::\n   :header-rows: 1\n   :widths: 46,14,40\n\n   - * `needtable <https://sphinxcontrib-needs.readthedocs.io/en/latest/directives/needtable.html>`_\n     * `needflow <https://sphinxcontrib-needs.readthedocs.io/en/latest/directives/needflow.html>`_\n     * `needpie <https://sphinxcontrib-needs.readthedocs.io/en/latest/directives/needpie.html>`_\n   - * .. image:: https://raw.githubusercontent.com/useblocks/sphinxcontrib-needs/master/docs/_images/needtable_1.png\n     * .. image:: https://raw.githubusercontent.com/useblocks/sphinxcontrib-needs/master/docs/_images/needflow_1.png\n     * .. image:: https://raw.githubusercontent.com/useblocks/sphinxcontrib-needs/master/docs/_images/needpie_1.png\n\nInstallation\n============\n\nUsing poetry\n------------\n::\n\n    poetry add sphinxcontrib-needs\n\n\nUsing pip\n---------\n::\n\n    pip install sphinxcontrib-needs\n\nUsing sources\n-------------\n::\n\n    git clone https://github.com/useblocks/sphinxcontrib-needs\n    cd sphinxcontrib-needs\n    pip install .\n\nActivation\n----------\n\nAdd **sphinxcontrib.needs** to your extensions::\n\n    extensions = ["sphinxcontrib.needs",]\n',
    'author': 'team useblocks',
    'author_email': 'info@useblocks.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://github.com/useblocks/sphinxcontrib-needs',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
