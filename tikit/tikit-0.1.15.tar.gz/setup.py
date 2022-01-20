from setuptools import setup, find_packages
import io


def requirements():
    with open('requirements.txt', 'r') as fileobj:
        requirements = [line.strip() for line in fileobj]
        return requirements


def long_description():
    with io.open('README.md', 'r', encoding='utf8') as fileobj:
        return fileobj.read()


setup(
    name='tikit',
    version='0.1.15',
    url='https://cloud.tencent.com/',
    license='MIT',
    author='TI PLATFORM TEAM',
    author_email='TI_Platform@tencent.com',
    description='Kit for TI PLATFORM',
    long_description=long_description(),
    packages=find_packages(),
    package_data={'requirements': ['requirements.txt']},
    install_requires=requirements()
)
