from setuptools import setup


requirements = []
with open("README.md", "r") as fh:
	long_description = fh.read()


setup(name='BinClassify',
      version='1.1.1',
      description='Binclassify is a library that makes it easy to classify into groups. The main idea of the library is to classify as many groups as possible using the minimum number of questions.',
      packages=['BinClassify'],
      author="Daniil Zatsev",
      author_email='yas66yelchili@gmail.com',
      install_requires=requirements,
      long_description=long_description,
      long_description_content_type="text/markdown",
      zip_safe=False)
#text/x-rst