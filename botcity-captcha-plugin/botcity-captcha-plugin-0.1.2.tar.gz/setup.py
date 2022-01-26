from setuptools import setup, find_namespace_packages
from os import path
from codecs import open
import versioneer

cur_dir = path.abspath(path.dirname(__file__))

with open(path.join(cur_dir, 'requirements.txt'), 'r') as f:
    requirements = f.read().split()

setup(
    name='botcity-captcha-plugin',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_namespace_packages(include=['botcity.plugins.*']),
    url='https://bitbucket.org/botcitydev/bot-captcha-plugin-python.git',
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    install_requires=requirements,
    include_package_data=True,
    python_requires='>=3.7'
)
