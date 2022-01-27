from setuptools import setup

# Read the contents of the README
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ocs_archive',
    use_scm_version=True,
    description='Base library for the science archive and ingester of an observatory control system',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/observatorycontrolsystem/ocs_archive',
    packages=['ocs_archive', 'ocs_archive.input', 'ocs_archive.settings', 'ocs_archive.storage'],
    python_requires='>=3.6',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Astronomy',
        'Topic :: Scientific/Engineering :: Physics'
    ],
    keywords=['archive', 'astronomy', 'astrophysics', 'cosmology', 'science', 'ocs', 'observatory'],
    setup_requires=['setuptools_scm'],
    install_requires=[
        'astropy',
        'boto3',
        'python-dateutil',
        'requests==2.26.0'
    ],
    extras_require={
        'tests': ['pytest',
                  'responses==0.16.0']
    }
)
