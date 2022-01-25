import os

import setuptools


with open(os.path.join(os.path.dirname(__file__), "README.md"), "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mposter",
    version="1.8.9",
    author="M.Postovoy",
    author_email="mihan.45rus@ya.ru",
    description="Additional tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MPostovoy/MPoster",
    packages=setuptools.find_packages(),
    license='MIT',
    install_requires=['loguru~=0.5.3', 'user_agent', 'zeep~=4.0.0', 'requests~=2.26.0', 'confluent_kafka==1.3.0',
                      'pyyml', 'pydantic~=1.8.2', 'hvac~=0.11.0', 'setuptools~=47.1.0',
                      'slackclient==1.3.1'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
# https://proglib.io/p/kak-opublikovat-svoyu-python-biblioteku-na-pypi-2020-01-28
