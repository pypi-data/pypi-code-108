import site
import sys
from setuptools import setup
site.ENABLE_USER_SITE = "--user" in sys.argv[1:]


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


with open("requirements.txt") as f:
    install_requires = f.read().splitlines()


setup(
    name='confluence-cli',
    version='0.6.3',
    packages=['confluence_cli.cli'],
    url='',
    license='MIT',
    author='juguerre',
    author_email='juguerre@gmail.com',
    description='Just another Atlassian Confluence API cli extension',
    entry_points='''
        [console_scripts]
        confluence_cmd=confluence_cmd:cli
    ''',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=install_requires,
    python_requires=">=3.8",
)
