import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-sns-notify",
    "version": "0.0.137",
    "description": "cdk-sns-notify",
    "license": "Apache-2.0",
    "url": "https://github.com/clarencetw/cdk-sns-notify.git",
    "long_description_content_type": "text/markdown",
    "author": "Clarence<mr.lin.clarence@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/clarencetw/cdk-sns-notify.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_sns_notify",
        "cdk_sns_notify._jsii"
    ],
    "package_data": {
        "cdk_sns_notify._jsii": [
            "cdk-sns-notify@0.0.137.jsii.tgz"
        ],
        "cdk_sns_notify": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-cloudwatch-actions>=1.72.0, <2.0.0",
        "aws-cdk.aws-cloudwatch>=1.72.0, <2.0.0",
        "aws-cdk.aws-ec2>=1.72.0, <2.0.0",
        "aws-cdk.aws-iam>=1.72.0, <2.0.0",
        "aws-cdk.aws-lambda-nodejs>=1.72.0, <2.0.0",
        "aws-cdk.aws-lambda>=1.72.0, <2.0.0",
        "aws-cdk.aws-sns-subscriptions>=1.72.0, <2.0.0",
        "aws-cdk.aws-sns>=1.72.0, <2.0.0",
        "aws-cdk.core>=1.72.0, <2.0.0",
        "constructs>=3.2.27, <4.0.0",
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
