
import re
from setuptools import setup


versio = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('PandoraAPI/PandoraFMS_API.py').read(),
    re.M
    ).group(1)


with open("readme.md", "rb") as f:
    long_descr = f.read().decode("utf-8")


setup(name='PandoraFMS-API',
      version=versio,
      description='API Per extreure dades generiques dels agents de PandoraFMS',
      long_description=long_descr,
      long_description_content_type='text/markdown',
      url='https://github.com/NilPujolPorta/PandoraFMS_API-NPP',
      author='Nil Pujol Porta',
      author_email='nilpujolporta@gmail.com',
      license='GNU',
      packages=['PandoraAPI'],
      install_requires=[
          'argparse',
          "setuptools>=42",
          "wheel",
          "openpyxl",
          "pyyaml",
          "requests",
          "mysql-connector-python"
      ],
	entry_points = {
        "console_scripts": ['PandoraFMS_API-NPP = PandoraAPI.PandoraFMS_API:main']
        },
      zip_safe=False)
