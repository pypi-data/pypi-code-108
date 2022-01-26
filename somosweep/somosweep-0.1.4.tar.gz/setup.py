from setuptools import setup, find_packages

# a dummy setup.py used to reserve the name somo on pypi following
# https://stackoverflow.com/questions/47676721/register-an-internal-package-on-pypi

setup(
    name="somosweep",
    version=open("somosweep/_version.py").readlines()[-1].split()[-1].strip("\"'"),
    description="A utility for running parameter sweeps in SoMo or SoMoGym.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/cbteeple/somosweep",
    author="Clark B. Teeple",
    author_email="cbteeple@gmail.com",
    license='MIT',
    # remember to add all additional submodules to this list
    packages=find_packages(exclude=['tests*']),
    install_requires=['python-dateutil',
                      'six',
                      'natsort',
                      'pathos',
                      ],
    classifiers=["Development Status :: 1 - Planning"],
)
