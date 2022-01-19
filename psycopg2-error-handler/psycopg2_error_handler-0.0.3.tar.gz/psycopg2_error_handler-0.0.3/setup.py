from setuptools import find_packages, setup

setup(
    name="psycopg2_error_handler",
    install_requires=[
        "psycopg-binary >= 3.0",
    ],
    version='0.0.3',
    description='Psycopg2 Error Handler',
    author='Alexander Lopatin',
    license='MIT',
)
