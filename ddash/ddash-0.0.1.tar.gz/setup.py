from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='ddash',
    version='0.0.1',
    author='Ron Chang',
    author_email='ron.hsien.chang@gmail.com',
    description=(
        'docker and docker-compose cli tool, to specify and automatic apply with current work directory'
    ),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Ron-Chang/ddash.git',
    packages=find_packages(),
    license='MIT',
    python_requires='>=3.6',
    exclude_package_date={'':['.gitignore', 'setup.py']},
    scripts=['bin/ddash'],
)

