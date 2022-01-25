from setuptools import setup

with open("README.md", 'r') as fh:
    long_description = fh.read()

setup(
    name='afori-utils',
    version='1.0.2',
    description='Some utils by Dor Miron',
    package_dir={'afori_utils': 'afori_utils'},
    packages=['afori_utils'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)"
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",

    install_requires=[
        "numpy>=1.20",
        "matplotlib>=3.4"
    ],
    license='LICENSE.txt',

    url="https://github.com/dor-miron/afori_utils",
    author="Dor Miron",
    author_email="dor00012@gmail.com"
)
