from typing import List
import setuptools


def slurp(filename: str) -> List[str]:
    return open(filename, 'r').read().splitlines()


setuptools.setup(
    name='daacla',
    version='0.0.6',
    author='anekos',
    author_email='pypi@snca.net',
    description='Python module to management `dataclass` objects using SQLite',
    long_description='\n'.join(slurp('README.md')),
    long_description_content_type='text/markdown',
    url='https://github.com/anekos/daacla',
    packages=setuptools.find_packages(),
    install_requires=slurp('requirements.txt'),
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
