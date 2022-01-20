import re
from setuptools import setup
import setuptools

with open('README.md', mode='r', encoding='utf-8') as readmefile:
    long_description = readmefile.read()

with open("src/propzen/__init__.py", mode='r', encoding='utf-8') as init_file:
    version = re.search("__version__ = \"(.*?)\"", init_file.read()).group(1)


setup(
    name='propzen-common',
    version=version,
    author='Mikhail Christian Peralta',
    author_email='mikhail.peralta@gmail.com',
    maintainer='Mikhail Christian Peralta',
    maintainer_email='mikhail.peralta@gmail.com',
    description='Common package for PropZen',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='http://pypi.python.org/pypi/propzen-common',
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    python_requires='>=3.9',
    install_requires=[
        'pydantic',
        'python-dotenv',
        'sqlalchemy',
        'dataclasses-json',
        'pika',
        'tenacity',
    ],
    zip_safe=True,
    license='MIT',
)
