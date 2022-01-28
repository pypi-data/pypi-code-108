import versioneer
from setuptools import find_packages, setup

with open('requirements.txt') as f:
    REQUIREMENTS = f.readlines()

with open('README.md') as fh:
    long_description = fh.read()

setup(
    name='drb-impl-file',
    packages=['drb_impl_file'],
    description='DRB File implementation',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='GAEL Systems',
    author_email='drb-python@gael.fr',
    url='https://gitlab.com/drb-python/impl/file',
    install_requires=REQUIREMENTS,
    test_suite='tests',
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.8',
    entry_points={'drb.impl': 'file = drb_impl_file'},
    package_data={
        'drb_impl_file': ['cortex.yml']
    },

    version=versioneer.get_version(),
    data_files=[('.', ['requirements.txt'])],
    cmdclass=versioneer.get_cmdclass(),
)
