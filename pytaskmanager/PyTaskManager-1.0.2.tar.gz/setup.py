from glob import glob
from os.path import basename, splitext
from setuptools import setup, find_packages

def _get_requires_from_file(filename):
    return open(filename).read().splitlines()


setup(
    name="PyTaskManager",
    version="1.0.2",
    license="MIT",
    author="Akagawa Daisuke",
    url="http://github.com/Akasan/PyTaskManager",
    packages=["PyTaskManager"],
    include_package_data=True,
    zip_safe=False,
)
