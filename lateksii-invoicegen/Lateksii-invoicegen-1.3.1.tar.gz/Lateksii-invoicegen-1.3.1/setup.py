from setuptools import setup, find_packages

setup(
    name='Lateksii-invoicegen',
    version='1.3.1',
    packages = find_packages('src'),
    data_files = ['lateksii-white-bg.png','template.tex'],
    author='antto',)