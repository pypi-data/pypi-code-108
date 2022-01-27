import re

import setuptools

with open("src/confio/__meta__.py", encoding="utf8") as f:
    version = re.search(r'version = ([\'"])(.*?)\1', f.read()).group(2)

setuptools.setup(
    name='confio',
    version=version,
    install_requires=[]
)
