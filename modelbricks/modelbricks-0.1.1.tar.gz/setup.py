# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
import setuptools

with open('README.md', 'r', encoding="utf-8") as readme:
    long_description = readme.read()

setuptools.setup(
    name = 'modelbricks',
    version='0.1.1',
    author='Jimmy Su',
    author_email = 'jim83531@gmail.com',
    description = 'ML model brick',
    long_description = long_description,
    long_description_content__type='markdown',
    url = 'https://github.com/nextfortune/modelbricks.git',
    packages = setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        'tensorflow>=2.6.0'
    ]
)
