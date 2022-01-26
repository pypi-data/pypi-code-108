from setuptools import setup, find_packages

setup(
    name='Lateksii-invoicegen',
    version='2.1.14',
    packages = find_packages(),
    data_files = [('res',['res/lateksii-white-bg.png','res/template.tex'])],
    author='antto',)