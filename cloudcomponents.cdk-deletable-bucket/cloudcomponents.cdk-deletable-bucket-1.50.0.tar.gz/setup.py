import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cloudcomponents.cdk-deletable-bucket",
    "version": "1.50.0",
    "description": "Bucket with content cleanup to allow bucket deletion when the stack will be destroyed",
    "license": "MIT",
    "url": "https://github.com/cloudcomponents/cdk-constructs",
    "long_description_content_type": "text/markdown",
    "author": "hupe1980",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/cloudcomponents/cdk-constructs.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cloudcomponents.cdk_deletable_bucket",
        "cloudcomponents.cdk_deletable_bucket._jsii"
    ],
    "package_data": {
        "cloudcomponents.cdk_deletable_bucket._jsii": [
            "cdk-deletable-bucket@1.50.0.jsii.tgz"
        ],
        "cloudcomponents.cdk_deletable_bucket": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-lambda>=1.140.0, <2.0.0",
        "aws-cdk.aws-s3>=1.140.0, <2.0.0",
        "aws-cdk.core>=1.140.0, <2.0.0",
        "aws-cdk.custom-resources>=1.140.0, <2.0.0",
        "constructs>=3.2.0, <4.0.0",
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
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
