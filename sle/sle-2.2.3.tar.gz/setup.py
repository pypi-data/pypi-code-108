import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    readme = fh.read()

setuptools.setup(
    name='sle',
    version='2.2.3',
    author_email="info@librecube.org",
    description='CCSDS Space Link Extension (SLE) Protocol',
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/librecube/lib/python-sle",
    license='MIT',
    python_requires='>=3.4',
    packages=setuptools.find_namespace_packages(where="src"),
    package_dir={"": "src"},
    install_requires=['pyasn1'],
)
