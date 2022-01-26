import versioneer
from setuptools import setup


with open('requirements.txt') as f:
    REQUIREMENTS = f.readlines()

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='drb-impl-xml',
    packages=['drb_impl_xml'],
    description='DRB XML implementation',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='GAEL Systems',
    author_email='drb-python@gael.fr',
    url='https://gitlab.com/drb-python/impl/xml',
    install_requires=REQUIREMENTS,
    test_suite='tests',
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",

    ],
    python_requires='>=3.8',
    entry_points={'drb.impl': 'xml = drb_impl_xml'},
    version=versioneer.get_version(),
    package_data={
        'drb_impl_xml': ['cortex.yml']
    },
    data_files=[('.', ['requirements.txt'])],
    cmdclass=versioneer.get_cmdclass(),
)
