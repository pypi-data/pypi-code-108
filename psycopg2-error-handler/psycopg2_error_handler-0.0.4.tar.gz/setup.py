from setuptools import setup

setup(
    name="psycopg2_error_handler",
    install_requires=[
        "psycopg-binary >= 3.0",
    ],
    packages=["psycopg2_error"],
    version='0.0.4',
    description='Psycopg2 Error Handler',
    author='Alexander Lopatin',
    license='MIT',
)
