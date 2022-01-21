import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='bigquery_utils',
    version='0.0.2',
    author='Alex Parthemer',
    author_email='alexparthemer@gmail.com',
    description='Utilities for creating, loading and querying bigquery tables.',
    long_description_content_type="text/markdown",
    url='https://github.com/aParthemer/bigquery_utils',
    download_url='https://github.com/aParthemer/bigquery_utils/archive/refs/tags/v0.0.2.tar.gz',
    project_urls={
        "Bug Tracker": "https://github.com/aParthemer/bigquery_utils/issues"
    },
    license='MIT',
    packages=['bigquery_utils'],
    install_requires=['google-cloud-bigquery',
                      'pandas',
                      'pyyaml'],
    classifiers=[
        'Development Status :: 3 - Alpha'
    ]
)
