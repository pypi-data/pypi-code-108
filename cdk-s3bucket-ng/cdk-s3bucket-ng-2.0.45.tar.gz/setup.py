import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-s3bucket-ng",
    "version": "2.0.45",
    "description": "cdk-s3bucket-ng is an AWS CDK construct library that provides a drop-in replacement for the Bucket construct with the capability to remove non-empty S3 buckets.",
    "license": "Apache-2.0",
    "url": "https://github.com/neilkuan/cdk-s3bucket.git",
    "long_description_content_type": "text/markdown",
    "author": "Neil Kuan<guan840912@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/neilkuan/cdk-s3bucket.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_s3bucket_ng",
        "cdk_s3bucket_ng._jsii"
    ],
    "package_data": {
        "cdk_s3bucket_ng._jsii": [
            "cdk-s3bucket-ng@2.0.45.jsii.tgz"
        ],
        "cdk_s3bucket_ng": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk-lib>=2.1.0, <3.0.0",
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
