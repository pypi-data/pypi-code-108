import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-aurora-globaldatabase",
    "version": "1.0.46",
    "description": "cdk-aurora-globaldatabase is an AWS CDK construct library that provides Cross Region Create Global Aurora RDS Databases.",
    "license": "Apache-2.0",
    "url": "https://github.com/neilkuan/cdk-aurora-globaldatabase.git",
    "long_description_content_type": "text/markdown",
    "author": "Neil Kuan<guan840912@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/neilkuan/cdk-aurora-globaldatabase.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_aurora_globaldatabase",
        "cdk_aurora_globaldatabase._jsii"
    ],
    "package_data": {
        "cdk_aurora_globaldatabase._jsii": [
            "cdk-aurora-globaldatabase@1.0.46.jsii.tgz"
        ],
        "cdk_aurora_globaldatabase": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-ec2>=1.134.0, <2.0.0",
        "aws-cdk.aws-events-targets>=1.134.0, <2.0.0",
        "aws-cdk.aws-events>=1.134.0, <2.0.0",
        "aws-cdk.aws-iam>=1.134.0, <2.0.0",
        "aws-cdk.aws-lambda>=1.134.0, <2.0.0",
        "aws-cdk.aws-logs>=1.134.0, <2.0.0",
        "aws-cdk.aws-rds>=1.134.0, <2.0.0",
        "aws-cdk.core>=1.134.0, <2.0.0",
        "aws-cdk.custom-resources>=1.134.0, <2.0.0",
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
