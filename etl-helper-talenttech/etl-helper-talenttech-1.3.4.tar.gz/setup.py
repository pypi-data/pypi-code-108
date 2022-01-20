import os

from setuptools import setup, Command, find_packages


class CleanCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info ./.pytest_cache ./.eggs')


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='etl-helper-talenttech',
    packages=find_packages(),
    version='1.3.4',
    license='MIT',
    description='TopMind ETL helper',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Dmitry Utiralov',
    author_email='d.utiralov@talenttech.ru',
    url='https://github.com/severgroup-tt/topmind-commons/tree/master/py/etl-helper',
    install_requires=[
        'sqlalchemy',
        'python-dateutil',
        'clickhouse-sqlalchemy==0.1.4',
        'sqlalchemy-vertica-python',
        'psycopg2-binary', 'requests'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.6',
    cmdclass={
        'clean': CleanCommand
    }
)
