import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "pepperize.cdk-autoscaling-gitlab-runner",
    "version": "0.0.141",
    "description": "AWS CDK GitLab Runner autoscaling on EC2 instances using docker+machine executor.",
    "license": "MIT",
    "url": "https://github.com/pepperize/cdk-autoscaling-gitlab-runner.git",
    "long_description_content_type": "text/markdown",
    "author": "Ivan Ovdiienko<ivan.ovdiienko@pepperize.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/pepperize/cdk-autoscaling-gitlab-runner.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "pepperize_cdk_autoscaling_gitlab_runner",
        "pepperize_cdk_autoscaling_gitlab_runner._jsii"
    ],
    "package_data": {
        "pepperize_cdk_autoscaling_gitlab_runner._jsii": [
            "cdk-autoscaling-gitlab-runner@0.0.141.jsii.tgz"
        ],
        "pepperize_cdk_autoscaling_gitlab_runner": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-autoscaling>=1.134.0, <2.0.0",
        "aws-cdk.aws-ec2>=1.134.0, <2.0.0",
        "aws-cdk.aws-iam>=1.134.0, <2.0.0",
        "aws-cdk.aws-s3-deployment>=1.134.0, <2.0.0",
        "aws-cdk.aws-s3>=1.134.0, <2.0.0",
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
