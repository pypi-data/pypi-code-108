# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['htmxl', 'htmxl.compose', 'htmxl.compose.write']

package_data = \
{'': ['*']}

install_requires = \
['jinja2>=2.10', 'openpyxl>=2.5', 'pendulum>=1.0']

extras_require = \
{':python_version < "3.8"': ['typing_extensions'],
 'beautifulsoup': ['beautifulsoup4>=4.6'],
 'lxml': ['lxml>=4.6']}

setup_kwargs = {
    'name': 'htmxl',
    'version': '0.8.5',
    'description': 'Produce Excel files from HTML templates.',
    'long_description': '![CircleCI](https://img.shields.io/circleci/build/gh/schireson/htmxl/master) [![Coverage\nStatus](https://coveralls.io/repos/github/schireson/htmxl/badge.svg?branch=master)](https://coveralls.io/github/schireson/htmxl?branch=master)\n[![Documentation](https://readthedocs.org/projects/htmxl/badge/?version=latest)](https://htmxl.readthedocs.io/en/latest/?badge=latest)\n\n## Introduction\n\n``` python\nfrom htmxl.compose import Workbook\n\nworkbook = Workbook()\nworkbook.add_sheet_from_template(\n    template="""\n    <head>{{ title }}</head>\n    <body>\n      <div>\n        Hello down there, {{ name }}!\n      </div>\n      <div>\n        <table>\n          <thead>\n            <tr>\n              {% for column_name in column_names %}\n                <th>{{ column_name }}</th>\n              {% endfor %}\n            </tr>\n          </thead>\n          <tbody>\n            {% for row in rows %}\n              <tr>\n                <td>{{ row.a }}</td>\n                <td>{{ row.b }}</td>\n              </tr>\n            {% endfor %}\n          </tbody>\n        </table\n      </div>\n    </body>\n    """,\n    data=dict(\n        title="Hello World",\n        name=\'Bob\',\n        column_names=[\'A\', \'B\'],\n        rows=[{\'a\': \'a\', \'b\': 2}, {\'a\': \'b\', \'b\': 2}, {\'a\': \'c\', \'b\': 3}],\n    )\n)\n\nworkbook.compose(\'hello_world.xlsx\')\n```\n\n![example](https://github.com/schireson/htmxl/blob/main/docs/_static/readme.png)\n\n## The Pitch\n\nEssentially, HTM(x)L is an attempt to allow the declaration of Excel files in a (mostly) declarative\nmanner that separates the format that the document should take from the data being added to it.\n\nThe "normal" manner of producing Excel files essentially amounts to a series of imperitive\nstatements about what cells to modify to get the excel file you want. For any file of moderate\ncomplexity, this leads to there being very little intuition about what the resulting Excel file will\nactually look like.\n\nParticularly once you start adding cell styling, or finding yourself inserting dynamically-sized\ndata (requiring a bunch of cell offset math), the relative ease of designing and visualizing the\ntemplate using a familiar idiom, HTML, can be make it much much easier to author and maintain these\nkinds of templates.\n\n## Features\n\nGeneral features include:\n\n- HTML elements as metaphors for structures in the resulting Excel document\n\n  Due to the obviously grid-oriented structure of Excel, the metaphors **can** sometimes be\n  approximate, but should hopefully make intuitive sense!\n\n  For example:\n\n  - `<span>`: An inline-block element which pushes elements after it to the right\n  - `<div>`: An block element which push elements after it downward\n  - `<table>`: Self-explanatory!\n\n  See the documentation about\n  [elements](https://htmxl.readthedocs.io/en/latest/design/elements.html) for more details\n\n- Styling\n\n  Some commonly/obviously useful and style options like width/height (`style="width: 50px"`) or\n  rowspan/colspan `colspan="2"` have been implemented, but there\'s no reason that various different\n  options that make intuitive sense (like colors) could be implemented also\n\n  See the documentation about [styling](https://htmxl.readthedocs.io/en/latest/design/styling.html)\n  for more details\n\n- Classes\n\n  While inline color styles are not (yet) implemented, one can supply classes normally,\n  `class="class1 class2"` and supply the definitions for those classes as inputs to the Workbook\n\n  ``` python\n  styles = [\n      {"name": "odd", "pattern_fill": {"patternType": "solid", "fgColor": "FBEAFB"}},\n  ]\n  Workbook(styles=styles)\n  ```\n\n## Installation\n\nThere is no default parser (for HTML) included with a default installation of the package. We do\nthis for both backwards compatibility and future compatibility reasons.\n\nIn order to keep the base package lean when one opts to use one or the other parser, we include a\nset of bundled parser-adaptor implementations for known supported parser libraries\n\nTo opt into the installation of the dependent library for the parser you chose:\n\n``` bash\n# Slower, but more permissive\npip install htmxl[beautifulsoup]\n\n# Faster, but more strict\npip install htmxl[lxml]\n```\n\nBy default, the package will detect installed parser libraries and choose the first one we find, so\na vanilla `Workbook()` instantiation should Just Work.\n\nHowever, we encourage users to explicitly select their parser to avoid inadvertant selection of the\n"wrong" parser at runtime (given that they have [template compatibility\nissues](https://pytest-mock-resources.readthedocs.io/en/latest/compatbility.html))\n\n``` python\nfrom htmxl.compose import Workbook\n\nworkbook = Workbook(parser=\'beautifulsoup\')\nworkbook = Workbook(parser=\'lxml\')\n```\n',
    'author': 'Hunter Senft-Grupp',
    'author_email': 'hunter@janux.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/schireson/htmxl',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4',
}


setup(**setup_kwargs)
