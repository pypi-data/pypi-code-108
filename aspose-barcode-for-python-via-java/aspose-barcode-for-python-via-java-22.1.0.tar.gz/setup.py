from setuptools import setup

NAME = "aspose-barcode-for-python-via-java"
VERSION = "22.1.0"
REQUIRES = ["JPype1==1.2.1"]

setup(
    name=NAME,
    version=VERSION,
    author="Aspose",
    description="Barcode generation and recognition component. It allows developers to quickly and easily add barcode creation and scanning functionality to their Python applications.",
    author_email="aleksander.grinin@aspose.com",
    keywords=["aspose", "barcode", "java"],
    install_requires=REQUIRES,
    packages=['asposebarcode'],
    include_package_data=True,
    long_description=open("README.md", encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'License :: Other/Proprietary License'
    ],
    python_requires='>=3.6',
)