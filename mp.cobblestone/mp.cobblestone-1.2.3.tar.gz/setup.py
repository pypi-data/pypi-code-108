from setuptools import setup, find_packages

long_desc = open('README.md').read()

setup(
    packages=find_packages(include=['cobblestone*']),
    package_data={
        'cobblestone': [
            'Dockerfile',
            'scripts/gitignore',
            'scripts/*.txt',
            'scripts/*.sh',
        ],
    },
    long_description=long_desc,
    long_description_content_type='text/markdown')
