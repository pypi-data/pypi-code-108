"""
This module defines how the netapp_ontap library gets built/installed. Build the
package by running "python3 setup.py sdist bdist_wheel"
"""

import os
import setuptools

import netapp_ontap

setuptools.setup(
    name=os.getenv("PACKAGE_NAME", "netapp-ontap"),
    version=netapp_ontap.__version__,
    author="NetApp",
    author_email="ng-ontap-rest-python-lib@netapp.com",
    description="A library for working with ONTAP's REST APIs simply in Python",
    long_description=netapp_ontap.__doc__,
    long_description_content_type="text/markdown",
    url="https://devnet.netapp.com/restapi.php",
    project_urls={
        "Documentation": "https://library.netapp.com/ecmdocs/ECMLP2879970/html/index.html",
    },
    keywords='NetApp ONTAP REST API development',
    packages=setuptools.find_packages(),
    package_data={
        "netapp_ontap": ["py.typed"],
    },
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    install_requires=["marshmallow>=3.2.1", "requests>=2.26.0", "requests-toolbelt>=0.9.1", "urllib3>=1.26.7"],
    extras_require={"cli": ["recline>=2020.5"]},
    python_requires=">=3.6",
    include_package_data=True,
    entry_points={
        "console_scripts": ["ontap-cli = netapp_ontap.__main__:main [cli]"],
    },
)
