import versioneer
from setuptools import find_packages, setup

with open('requirements.txt') as f:
    REQUIREMENTS = f.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='drb',
    packages=find_packages(exclude=['tests']),
    description='Data Request Broker',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='GAEL Systems',
    author_email='drb-python@gael.fr',
    url='https://gitlab.com/drb-python/drb',
    install_requires=REQUIREMENTS,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    use_scm_version=True,
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    package_data={
        'drb.factory': ['it_schema.yml']
    },
    data_files=[('.', ['requirements.txt'])],
    entry_points={
        'console_scripts': [
            'cortex-validator=drb.factory.cortex_validator:main'
        ]
    },
    project_urls={
        'Documentation': 'https://drb-python.gitlab.io/drb',
        'Source': 'https://github.com/drb-python/drb',
    }
)
