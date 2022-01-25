import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-demo-construct",
    "version": "0.0.42",
    "description": "A sample L3 CDK project",
    "license": "Apache-2.0",
    "url": "https://github.com/neilkuan/cdk-demo-construct.git",
    "long_description_content_type": "text/markdown",
    "author": "Neil Kuan<guan840912@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/neilkuan/cdk-demo-construct.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_demo_construct",
        "cdk_demo_construct._jsii"
    ],
    "package_data": {
        "cdk_demo_construct._jsii": [
            "cdk-demo-construct@0.0.42.jsii.tgz"
        ],
        "cdk_demo_construct": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-cloudwatch-actions>=1.139.0, <2.0.0",
        "aws-cdk.aws-cloudwatch>=1.139.0, <2.0.0",
        "aws-cdk.aws-ec2>=1.139.0, <2.0.0",
        "aws-cdk.aws-sns>=1.139.0, <2.0.0",
        "aws-cdk.core>=1.139.0, <2.0.0",
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
