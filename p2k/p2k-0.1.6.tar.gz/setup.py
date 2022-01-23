from setuptools import setup, find_packages

with open('README.rst', 'r') as fh:
    long_description = fh.read()

setup(
    name='p2k',  # required
    version='0.1.6',
    description='p2k: utilities for paleoclimate reconstruction',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author='Feng Zhu',
    author_email='fzhu@nuist.edu.cn',
    url='https://github.com/fzhu2e/p2k',
    packages=find_packages(),
    include_package_data=True,
    license='BSD 3-Clause',
    zip_safe=False,
    keywords='paleocliamte reconstruction',
    classifiers=[
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
    ],
    install_requires=[
        'termcolor',
        'pandas',
        'tqdm',
        'xarray',
        'netCDF4',
        'nc-time-axis',
        'dask',
        'pathos',
        'fbm',
        'statsmodels',
        'pyvsl',
    ],
)
