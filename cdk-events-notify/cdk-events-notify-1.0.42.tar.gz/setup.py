import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-events-notify",
    "version": "1.0.42",
    "description": "The Events Notify AWS Construct lib for AWS CDK",
    "license": "Apache-2.0",
    "url": "https://github.com/neilkuan/cdk-events-notify.git",
    "long_description_content_type": "text/markdown",
    "author": "Neil Kuan<guan840912@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/neilkuan/cdk-events-notify.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_events_notify",
        "cdk_events_notify._jsii"
    ],
    "package_data": {
        "cdk_events_notify._jsii": [
            "cdk-events-notify@1.0.42.jsii.tgz"
        ],
        "cdk_events_notify": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.assertions>=1.134.0, <2.0.0",
        "aws-cdk.aws-events-targets>=1.134.0, <2.0.0",
        "aws-cdk.aws-events>=1.134.0, <2.0.0",
        "aws-cdk.aws-lambda>=1.134.0, <2.0.0",
        "aws-cdk.aws-logs>=1.134.0, <2.0.0",
        "aws-cdk.core>=1.134.0, <2.0.0",
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
