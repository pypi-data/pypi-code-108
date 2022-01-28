import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "pwrdrvr.microapps.cdk",
    "version": "0.2.6",
    "description": "MicroApps framework, by PwrDrvr LLC, delivered as an AWS CDK construct that provides the DynamoDB, Router service, Deploy service, API Gateway, and CloudFront distribution.",
    "license": "MIT",
    "url": "https://github.com/pwrdrvr/microapps-core",
    "long_description_content_type": "text/markdown",
    "author": "Harold Hunt<harold@pwrdrvr.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/pwrdrvr/microapps-core"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "pwrdrvr.microapps.cdk",
        "pwrdrvr.microapps.cdk._jsii"
    ],
    "package_data": {
        "pwrdrvr.microapps.cdk._jsii": [
            "microapps-cdk@0.2.6.jsii.tgz"
        ],
        "pwrdrvr.microapps.cdk": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk-lib>=2.8.0, <3.0.0",
        "aws-cdk.aws-apigatewayv2-alpha==2.8.0.a0",
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
