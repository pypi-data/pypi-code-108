import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "renovosolutions.aws-cdk-aws-ipam",
    "version": "0.0.1",
    "description": "AWS CDK Construct Library to manage AWS VPC IP Address Manager resources",
    "license": "Apache-2.0",
    "url": "https://github.com/RenovoSolutions/cdk-library-aws-ipam.git",
    "long_description_content_type": "text/markdown",
    "author": "Renovo Solutions<webmaster+cdk@renovo1.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/RenovoSolutions/cdk-library-aws-ipam.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "ipam",
        "ipam._jsii"
    ],
    "package_data": {
        "ipam._jsii": [
            "cdk-library-aws-ipam@0.0.1.jsii.tgz"
        ],
        "ipam": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk-lib>=2.5.0, <3.0.0",
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
