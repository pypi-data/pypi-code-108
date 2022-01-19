__version__ = "0.1.8"

from setuptools import setup, find_packages
import os

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    long_description = f.read()


if __name__ == '__main__':
    setup(
        name='logboss',
        packages=find_packages(where='.', exclude=['examples']),
        package_dir={
            'logboss': 'logboss'
        },
        include_package_data=True,
        long_description=long_description,
        long_description_content_type='text/markdown',
        version=__version__,
        author='Tyler Spens',
        author_email='mrtspens@gmail.com',
        keywords=['logging', 'persistent', 'database', 'db', 'sqlite', 'log', 'persist', 'data'],
        install_requires=[
            'jsonpickle',
            'Pygments',
            'htmlmin',
            'simplejson'
        ],
        url='https://gitlab.com/tspens/log-boss',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Build Tools',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.8',
        ]
    )
