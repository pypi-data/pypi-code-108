from setuptools import setup, find_packages

setup(
    name='Lateksii-invoicegen',
    version='2.1.2',
    packages = find_packages(),
    data_files = [('res',['lateksii-white-bg.png','template.tex'])],
    author='antto',)