
import re
from setuptools import setup


versio = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('CatBackupAPI/CatbackupAPI_NPP.py').read(),
    re.M
    ).group(1)


with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")


setup(name='CatbackupAPI-NPP',
      version=versio,
      description="Programa per recoleccio de dades d'apis de CatBackup",
      long_description=long_descr,
      long_description_content_type='text/markdown',
      url='https://github.com/NilPujolPorta/CatbackupAPI-NPP',
      author='Nil Pujol Porta',
      author_email='nilpujolporta@gmail.com',
      license='GNU',
      packages=['catbackupAPI'],
      install_requires=[
          'argparse',
          "setuptools>=42",
          "wheel",
          "openpyxl",
          "pyyaml",
          "requests",
          "mysql-connector-python",
          "tqdm",
          "opencv-python",
          "pyotp",
          "pytesseract",
          "selenium"
      ],
	entry_points = {
        "console_scripts": ['CatbackupAPI-NPP = CatBackupAPI.CatbackupAPI_NPP:main']
        },
      zip_safe=False)
