"""The setup script."""

from setuptools import setup

with open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()

setup(
    name='heaserver-volumes',
    version='1.0.0a7',
    description="The HEA volumes service",
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://risr.hci.utah.edu',
    author="Research Informatics Shared Resource, Huntsman Cancer Institute, Salt Lake City, UT",
    author_email='Andrew.Post@hci.utah.edu',
    python_requires='>=3.8',
    package_dir={'': 'src'},
    packages=['heaserver.volume'],
    package_data={'heaserver.volume': ['wstl/*.json']},
    install_requires=['heaserver>=1.0.0a47, <1.0.0a48'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Framework :: AsyncIO',
        'Environment :: Web Environment',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Medical Science Apps.'
    ],
    entry_points={
        'console_scripts': [
            'heaserver-volumes=heaserver.volume.service:main',
        ],
    },
    keywords=['heaserver-volumes', 'microservice', 'healthcare', 'cancer', 'research', 'informatics'],
)
