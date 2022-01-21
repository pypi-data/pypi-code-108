import setuptools

REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines()]

setuptools.setup(
    name='pyspark-utilities',
    version='0.0.14',
    description='Spark utilities to be used by the Analytics BDA',
    author='ENG ALIDA TEAM',
    author_email='engineering-alida-lab@eng.it',
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    install_requires=REQUIREMENTS
)
