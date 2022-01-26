from setuptools import setup, find_packages

setup(
    name='Lateksii-invoicegen',
    version='3.0.2',
    packages = find_packages(),
    data_files = [('res',['res/lateksii-white-bg.png','res/template.tex'])],
    author='antto',
    install_requires=["PySimpleGUI","pdflatex","tkinter"],)