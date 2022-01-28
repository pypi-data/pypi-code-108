from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name='logged-groups',
      version='2.1.2',
      description='Per class logging tools',
      author='Rozhkov Dmitrii',
      author_email='rozhkovdmitrii@yandex.ru',
      license='GPL-3.0',
      url='http://rozhkovdmitrii.ru/',
      packages=["logged_groups"],
      install_requires=['singleton-decorator'],
      long_description=long_description,
      long_description_content_type="text/markdown",
      classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Operating System :: OS Independent",
      ],
      )
