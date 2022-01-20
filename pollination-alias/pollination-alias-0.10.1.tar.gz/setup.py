import setuptools

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md') as fh:
    long_description = fh.read()

setuptools.setup(
    name="pollination-alias",
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    author="Pollination",
    author_email="info@pollination.cloud",
    packages=setuptools.find_namespace_packages(
        include=['pollination.*'], exclude=['tests']
    ),
    install_requires=requirements,
    description="Collection of alias inputs and outputs for Pollination recipes.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pollination/pollination-alias",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License"
    ],
    license="Apache-2.0 License",
    zip_safe=False
)
