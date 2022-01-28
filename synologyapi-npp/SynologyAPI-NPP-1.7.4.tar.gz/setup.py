
import re
from setuptools import setup


versio = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('SynologyAPI/synology_API.py').read(),
    re.M
    ).group(1)


with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")


setup(name='SynologyAPI-NPP',
      version=versio,
      description='API Basica per a synologys Active Backup For Buissiness',
      long_description=long_descr,
      long_description_content_type='text/markdown',
      url='https://github.com/NilPujolPorta/Synology_API-NPP',
      author='Nil Pujol Porta',
      author_email='nilpujolporta@gmail.com',
      license='GNU',
      packages=['SynologyAPI'],
      install_requires=[
          'argparse',
          "setuptools>=42",
          "wheel",
          "openpyxl",
          "pyyaml",
          "requests",
          "mysql-connector-python",
          "tqdm"
      ],
	entry_points = {
        "console_scripts": ['SynologyAPI-NPP = SynologyAPI.synology_API:main']
        },
      zip_safe=False)
