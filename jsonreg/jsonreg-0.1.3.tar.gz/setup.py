import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='jsonreg',
    url='https://github.com/awesomelewis2007/jsonreg/',
    author='Lewis Evans',
    packages=['jsonreg'],
    install_requires=[''],
    version="0.1.3",
    license='GNU',
    long_description=long_description,
    long_description_content_type="text/markdown",
    description='Quickly create json keys to store data'
)
