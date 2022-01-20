from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'A package that parses configuration values.'
LONG_DESCRIPTION = 'A package that makes it easy to parse env values.'

setup(
    name="pyenvparser",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author="jspenc72",
    author_email="jspenc72@gmail.com",
    license='MIT',
    packages=find_packages(),
    install_requires=[],
    keywords='env',
    classifiers= [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python :: 3",
    ]
)
