import io

from setuptools import setup, find_packages

with io.open('README.md', 'rt', encoding='utf8') as f:
    readme = f.read()

with io.open('VERSION') as version_file:
    version = version_file.read().strip().lower()
    if version.startswith("v"):
        version = version[1:]

setup(
    name='graphql_http_server',
    version=version,
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    author='Robert Parker',
    author_email='rob@parob.com',
    url='https://gitlab.com/parob/graphql-http-server',
    download_url=f'https://gitlab.com/parob/graphql-http-server/-/archive/master/graphql-http-server-v{version}.zip',
    keywords=['GraphQL', 'HTTPServer', 'werkzeug'],
    description='HTTPServer for GraphQL.',
    long_description=readme,
    long_description_content_type='text/markdown',
    install_requires=[
        "graphql-core>=3.0.0",
        "werkzeug>=0.13"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
