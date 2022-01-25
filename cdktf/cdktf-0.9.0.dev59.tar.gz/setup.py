import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdktf",
    "version": "0.9.0.dev59",
    "description": "Cloud Development Kit for Terraform",
    "license": "MPL-2.0",
    "url": "https://github.com/hashicorp/terraform-cdk",
    "long_description_content_type": "text/markdown",
    "author": "HashiCorp",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/hashicorp/terraform-cdk.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdktf",
        "cdktf._jsii",
        "cdktf.testing_matchers"
    ],
    "package_data": {
        "cdktf._jsii": [
            "cdktf@0.9.0-pre.59.jsii.tgz"
        ],
        "cdktf": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "constructs>=10.0.25, <11.0.0",
        "jsii>=1.52.1, <2.0.0",
        "publication>=0.0.3"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Typing :: Typed",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
