import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "pepperize.cdk-private-bucket",
    "version": "0.0.15",
    "description": "This project provides a CDK construct for creating private S3 bucket.",
    "license": "MIT",
    "url": "https://github.com/pepperize/cdk-private-bucket.git",
    "long_description_content_type": "text/markdown",
    "author": "Andreas Forster<andreas.forster@pepperize.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/pepperize/cdk-private-bucket.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "pepperize_cdk_private_bucket",
        "pepperize_cdk_private_bucket._jsii"
    ],
    "package_data": {
        "pepperize_cdk_private_bucket._jsii": [
            "cdk-private-bucket@0.0.15.jsii.tgz"
        ],
        "pepperize_cdk_private_bucket": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk-lib>=2.8.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
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
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
