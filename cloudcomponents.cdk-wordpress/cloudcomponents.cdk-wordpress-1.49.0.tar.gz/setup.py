import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cloudcomponents.cdk-wordpress",
    "version": "1.49.0",
    "description": "CDK Construct to deploy wordpress",
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
        "cloudcomponents.cdk_wordpress",
        "cloudcomponents.cdk_wordpress._jsii"
    ],
    "package_data": {
        "cloudcomponents.cdk_wordpress._jsii": [
            "cdk-wordpress@1.49.0.jsii.tgz"
        ],
        "cloudcomponents.cdk_wordpress": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-backup>=1.140.0, <2.0.0",
        "aws-cdk.aws-certificatemanager>=1.140.0, <2.0.0",
        "aws-cdk.aws-cloudfront-origins>=1.140.0, <2.0.0",
        "aws-cdk.aws-cloudfront>=1.140.0, <2.0.0",
        "aws-cdk.aws-ec2>=1.140.0, <2.0.0",
        "aws-cdk.aws-ecs>=1.140.0, <2.0.0",
        "aws-cdk.aws-efs>=1.140.0, <2.0.0",
        "aws-cdk.aws-elasticloadbalancingv2-actions>=1.140.0, <2.0.0",
        "aws-cdk.aws-elasticloadbalancingv2>=1.140.0, <2.0.0",
        "aws-cdk.aws-iam>=1.140.0, <2.0.0",
        "aws-cdk.aws-logs>=1.140.0, <2.0.0",
        "aws-cdk.aws-rds>=1.140.0, <2.0.0",
        "aws-cdk.aws-route53-targets>=1.140.0, <2.0.0",
        "aws-cdk.aws-route53>=1.140.0, <2.0.0",
        "aws-cdk.aws-s3>=1.140.0, <2.0.0",
        "aws-cdk.core>=1.140.0, <2.0.0",
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
