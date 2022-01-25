import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-iam-floyd",
    "version": "0.310.0",
    "description": "AWS IAM policy statement generator with fluent interface for AWS CDK",
    "license": "Apache-2.0",
    "url": "https://github.com/udondan/iam-floyd",
    "long_description_content_type": "text/markdown",
    "author": "Daniel Schroeder",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/udondan/iam-floyd.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_iam_floyd",
        "cdk_iam_floyd._jsii"
    ],
    "package_data": {
        "cdk_iam_floyd._jsii": [
            "cdk-iam-floyd@0.310.0.jsii.tgz"
        ],
        "cdk_iam_floyd": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk-lib>=2.0.0, <3.0.0",
        "constructs>=10.0.0, <11.0.0",
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
