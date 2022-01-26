from setuptools import setup, find_packages

setup(
    name='Lateksii-invoicegen',
    version='1.3.2',
    packages = find_packages('src'),
    package_dir={'': 'src'},
    data_files = ['lateksii-white-bg.png','template.tex'],
    author='antto',)