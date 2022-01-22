from setuptools import setup, find_packages

import carton


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name='py3-django-enriched-carton',
    version=carton.__version__,
    description=carton.__doc__,
    packages=find_packages(),
    url='https://github.com/knyazz/py3-django-enriched-carton',
    author='smirnov.ev',
    author_email='knyazz@gmail.com',
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta'
    ],
    install_requires=[
        'Django>=3.2.0',
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    include_package_data=True,
)
