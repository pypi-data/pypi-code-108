import setuptools

with open("README.md", "r") as file_obj:
    long_description = file_obj.read()

packages = setuptools.find_packages()

setuptools.setup(
    name='nubium-schemas',
    author="Edward Brennan",
    author_email="ebrennan@redhat.com",
    description="Python dictionary representations of Avro Schema for the nubium project",
    maintainer="Pramod Toraskar",
    maintainer_email="ptoraska@redhat.com",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://gitlab.corp.redhat.com/mkt-ops-de/nubium-schemas.git",
    packages=packages,
    install_requires=[
        "dataclasses-avroschema>=0.20.2",
        "pydantic"
    ],
    extras_require={
        "dev": ["black", "pip-tools", "pytest", "pytest-cov", "setuptools_scm"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
