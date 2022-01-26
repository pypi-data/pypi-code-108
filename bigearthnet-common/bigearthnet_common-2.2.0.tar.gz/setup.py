# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bigearthnet_common']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4,<2.0',
 'fastcore>=1.3,<2.0',
 'natsort>=8,<9',
 'pydantic>=1.8,<2.0',
 'rich>=10,<12',
 'typer>=0.4,<0.5']

entry_points = \
{'console_scripts': ['ben_constant_prompt = '
                     'bigearthnet_common.constants:constants_prompt']}

setup_kwargs = {
    'name': 'bigearthnet-common',
    'version': '2.2.0',
    'description': 'A collection of common tools to interact with the BigEarthNet dataset.',
    'long_description': '# Common BigEarthNet Tools\n> A personal collection of common tools to interact with the BigEarthNet dataset.\n\n\n[![Tests](https://img.shields.io/github/workflow/status/kai-tub/bigearthnet_common/CI?color=dark-green&label=%20Tests)](https://github.com/kai-tub/bigearthnet_common/actions/workflows/main.yml)\n[![License](https://img.shields.io/pypi/l/bigearthnet_common?color=dark-green)](https://github.com/kai-tub/bigearthnet_common/blob/main/LICENSE)\n[![PyPI version](https://badge.fury.io/py/bigearthnet-common.svg)](https://pypi.org/project/bigearthnet-common/)\n[![Conda Version](https://img.shields.io/conda/vn/conda-forge/bigearthnet-common?color=dark-green)](https://anaconda.org/conda-forge/bigearthnet-common)\n[![Auto Release](https://img.shields.io/badge/release-auto.svg?colorA=888888&colorB=9B065A&label=auto&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAACzElEQVR4AYXBW2iVBQAA4O+/nLlLO9NM7JSXasko2ASZMaKyhRKEDH2ohxHVWy6EiIiiLOgiZG9CtdgG0VNQoJEXRogVgZYylI1skiKVITPTTtnv3M7+v8UvnG3M+r7APLIRxStn69qzqeBBrMYyBDiL4SD0VeFmRwtrkrI5IjP0F7rjzrSjvbTqwubiLZffySrhRrSghBJa8EBYY0NyLJt8bDBOtzbEY72TldQ1kRm6otana8JK3/kzN/3V/NBPU6HsNnNlZAz/ukOalb0RBJKeQnykd7LiX5Fp/YXuQlfUuhXbg8Di5GL9jbXFq/tLa86PpxPhAPrwCYaiorS8L/uuPJh1hZFbcR8mewrx0d7JShr3F7pNW4vX0GRakKWVk7taDq7uPvFWw8YkMcPVb+vfvfRZ1i7zqFwjtmFouL72y6C/0L0Ie3GvaQXRyYVB3YZNE32/+A/D9bVLcRB3yw3hkRCdaDUtFl6Ykr20aaLvKoqIXUdbMj6GFzAmdxfWx9iIRrkDr1f27cFONGMUo/gRI/jNbIMYxJOoR1cY0OGaVPb5z9mlKbyJP/EsdmIXvsFmM7Ql42nEblX3xI1BbYbTkXCqRnxUbgzPo4T7sQBNeBG7zbAiDI8nWfZDhQWYCG4PFr+HMBQ6l5VPJybeRyJXwsdYJ/cRnlJV0yB4ZlUYtFQIkMZnst8fRrPcKezHCblz2IInMIkPzbbyb9mW42nWInc2xmE0y61AJ06oGsXL5rcOK1UdCbEXiVwNXsEy/6+EbaiVG8eeEAfxvaoSBnCH61uOD7BS1Ul8ESHBKWxCrdyd6EYNKihgEVrwOAbQruoytuBYIFfAc3gVN6iawhjKyNCEpYhVJXgbOzARyaU4hCtYizq5EI1YgiUoIlT1B7ZjByqmRWYbwtdYjoWoN7+LOIQefIqKawLzK6ID69GGpQgwhhEcwGGUzfEPAiPqsCXadFsAAAAASUVORK5CYII=)](https://github.com/intuit/auto)\n\nThis library provides a collection of high-level tools to better work with the [BigEarthNet](bigearth.net) dataset.\n\n`bigearthnet_common` tries to:\n\n1. Collect the most relevant _constants_ into a single place to reduce the time spent looking for these, like:\n   - The 19 or 43 class nomenclature strings\n   - URL\n   - Band statistics (mean/variance) as integer and float\n   - Channel names\n   - etc.\n2. Provide common metadata related functions\n   - Safe JSON parser for S1/S2\n   - Get the original split\n   - Get a list of snowy/cloudy patches\n   - Convert the _old_ labels to thew _new_ label nomenclature\n   - Generate multi-hot encoded label views\n\n## Installation\nThe package is available via PyPI and can be installed with:\n- `pip install bigearthnet_common`\n\nThe package has _Python-only_ dependencies and should cause no issues in more complex Conda environments with various binaries.\n\n## Review constants\nTo quickly search for BigEarthNet constants of interest, call:\n- `ben_constants_prompt` or\n- `python -m bigearthnet_common.constants`\n\n## Contributing\n\nContributions are always welcome!\n\nPlease look at the corresponding `ipynb` notebook from the `nbs` folder to review the source code.\nThese notebooks include extensive documentation, visualizations, and tests.\nThe automatically generated Python files are available in the `bigearthnet_common` module.\n\nMore information is available in the [contributing guidelines](https://github.com/kai-tub/bigearthnet_common/blob/main/.github/CONTRIBUTING.md) document.\n',
    'author': 'Kai Norman Clasen',
    'author_email': 'snakemap_navigation@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kai-tub/bigearthnet_common',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
