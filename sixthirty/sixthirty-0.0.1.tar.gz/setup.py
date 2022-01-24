from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

description = 'Monorepo of 6-30 services'
long_description = (here / 'README.md').read_text(encoding='utf-8')

classifiers = [
    'Development Status :: 3 - Alpha',

    'License :: OSI Approved :: MIT License',

    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    "Programming Language :: Python :: 3.10",
]

setup(
    name='sixthirty',
    version='0.0.1',
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/dvcorreia/6-30',
    author='Diogo Correia',
    author_email='dv_correia@hotmail.com',
    classifiers=classifiers,

    keywords='beer, manage, count, metrics',
    package_dir={'': 'sixthirty'},
    packages=find_packages(where='sixthirty'),
    python_requires='>=3.8, <4',

    install_requires=[],


    extras_require={
        'dev': [],
        'test': [],
    },

    entry_points={
        'console_scripts': [
            'sixthirty=server:main',
        ],
    },

    project_urls={
        'Bug Reports': 'https://github.com/dvcorreia/6-30/issues',
        'Source': 'https://github.com/dvcorreia/6-30',
    },
)
