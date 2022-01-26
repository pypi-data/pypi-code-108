from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='boonnano',
    version='3.1.5',
    author="BoonLogic",
    author_email="elise@boonlogic.com",
    packages=['boonnano'],
    install_requires=['urllib3','numpy'],
    description="A SDK package for utilizing the BoonLogic nano API",
    long_description=long_description,
    license='MIT',
    long_description_content_type="text/markdown",
    url="https://github.com/boonlogic/Python_API",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ]
)
