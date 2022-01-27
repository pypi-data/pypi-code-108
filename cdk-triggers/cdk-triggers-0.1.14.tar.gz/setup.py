import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-triggers",
    "version": "0.1.14",
    "description": "Execute AWS Lambda handlers during deployments of AWS CDK stacks",
    "license": "Apache-2.0",
    "url": "https://github.com/awslabs/cdk-triggers.git",
    "long_description_content_type": "text/markdown",
    "author": "Amazon Web Services<aws-cdk-team@amazon.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/awslabs/cdk-triggers.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_triggers",
        "cdk_triggers._jsii"
    ],
    "package_data": {
        "cdk_triggers._jsii": [
            "cdk-triggers@0.1.14.jsii.tgz"
        ],
        "cdk_triggers": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk-lib>=2.0.0, <3.0.0",
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
