import setuptools
from setuptools import setup


setup(
    name='stdcom',
    version='1.2.3',
    license='GPL',
    license_files = ('LICENSE.txt',),
    author='ed',
    url='https://pip.pypa.io/',
    author_email='srini_durand@yahoo.com',
    description='Stec NextStep Railway Communication Module',
    long_description='Railway communication from Python 3 to Stec Multiverse ',
    long_description_content_type="text/markdown",
    classifiers = [
                  "Programming Language :: Python :: 3",
                  "Programming Language :: Python :: 3.5",
                  "Programming Language :: Python :: 3.6",
                  "Programming Language :: Python :: 3.7",
                  "Programming Language :: Python :: 3.8",
                  "Programming Language :: Python :: 3.9",
                  "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
                  "Operating System :: OS Independent",
              ],
    requires = ["setuptools", "wheel","PyQt5"],
    install_requires =["PyQt5","opcua","cryptography"],
    py_modules=["stdcomqt5widget","stdcomqt5treeewidget","ipportdialog","stdcom","stdcomqt5","frontend","frontendOPCUA" ],
    package_dir={'stdcom': './src'},
    packages=setuptools.find_packages(),
    include_package_data = True
)
