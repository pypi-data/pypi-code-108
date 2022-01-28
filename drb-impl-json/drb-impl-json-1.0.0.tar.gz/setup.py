import versioneer
from setuptools import setup

with open('requirements.txt') as f:
    REQUIREMENTS = f.readlines()

with open('README.md') as fh:
    long_description = fh.read()

setup(
    name='drb-impl-json',
    packages=['drb_impl_json'],
    description='DRB json implementation',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='GAEL Systems',
    author_email='drb-python@gael.fr',
    url='https://gitlab.com/drb-python/impl/json',
    install_requires=REQUIREMENTS,
    test_suite='tests',
    data_files=[('.', ['requirements.txt'])],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.8',
    entry_points={'drb.impl': 'json = drb_impl_json'},
    version=versioneer.get_version(),
    package_data={
        'drb_impl_xml': ['cortex.yml']
    },
    cmdclass=versioneer.get_cmdclass(),
    project_urls={
        'Documentation': 'http://drb-python.gitlab.io/impl/json',
        'Source': 'https://gitlab.com/drb-python/impl/json',
    }
)
