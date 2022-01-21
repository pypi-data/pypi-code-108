from setuptools import setup
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name='awslayer-manager',
    version='1.0.14',
    packages=['awslayer'],
    install_requires=[
          'cursor',
      ],
    url='https://www.example.com',
    include_package_data=True,
    license='MIT',
    author='Ramazan Elsunkaev',
    author_email='relsunkaev@outlook.com',
    entry_points={
        'console_scripts': [
            'awslayer = awslayer.run:main',
        ],
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    description='A simple, per-project AWS Lambda Layer manager.',
    long_description=README,
    long_description_content_type="text/markdown",
)
