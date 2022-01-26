# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['streamlit_url_fragment']

package_data = \
{'': ['*'],
 'streamlit_url_fragment': ['build/*',
                            'build/static/js/*',
                            'public/*',
                            'src/*']}

install_requires = \
['importlib-resources>=5.4.0,<6.0.0', 'streamlit>0.63']

setup_kwargs = {
    'name': 'streamlit-url-fragment',
    'version': '0.2.1',
    'description': 'Get the URL fragment (part after #) from Streamlit',
    'long_description': '# Streamlit URL fragment\n\nGet the URL fragment (the part of URL after #) in your Streamlit script:\n```python\nimport streamlit as st\nfrom streamlit_url_fragment import get_fragment\n\ncurrent_value = get_fragment()\nst.write("Current value: {!r}".format(get_fragment()))\n```\n\nWarning: the first value you\'ll get will be a `None` - that means the component is still loading.\nYou can wait for the correct value with `if current_value is None: st.stop()`.',
    'author': 'Tomasz Kontusz',
    'author_email': 'tomasz.kontusz@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
