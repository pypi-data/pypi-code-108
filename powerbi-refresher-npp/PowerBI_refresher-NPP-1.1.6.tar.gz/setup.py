import re
from setuptools import setup


versio = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('refresher/refresher.py').read(),
    re.M
    ).group(1)


with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")


setup(name='PowerBI_refresher-NPP',
      version=versio,
      description='Script for refreshing and publishing Power BI workbooks',
      long_description=long_descr,
      long_description_content_type='text/markdown',
      url='https://github.com/NilPujolPorta/PowerBI_refresher-NPP',
      author='Nil Pujol Porta',
      author_email='nilpujolporta@gmail.com',
      license='GNU',
      packages=['refresher'],
      install_requires=[
          'pywinauto',
          'psutil',
          'keyboard',
          'argparse',
          "setuptools>=42",
          "wheel"
      ],
	  entry_points = {
        "console_scripts": ['PowerBI_refresher-NPP = refresher.refresher:main']
        },
      zip_safe=False)
