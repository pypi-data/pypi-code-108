import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-codepipeline-badge-notification",
    "version": "1.0.26",
    "description": "cdk-codepipeline-badge-notification",
    "license": "Apache-2.0",
    "url": "https://github.com/kimisme9386/cdk-codepipeline-badge-notification",
    "long_description_content_type": "text/markdown",
    "author": "Chris Yang",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/kimisme9386/cdk-codepipeline-badge-notification"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_codepipeline_badge_notification",
        "cdk_codepipeline_badge_notification._jsii"
    ],
    "package_data": {
        "cdk_codepipeline_badge_notification._jsii": [
            "cdk-codepipeline-badge-notification@1.0.26.jsii.tgz"
        ],
        "cdk_codepipeline_badge_notification": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-codebuild>=1.100.0, <2.0.0",
        "aws-cdk.aws-codepipeline-actions>=1.100.0, <2.0.0",
        "aws-cdk.aws-codepipeline>=1.100.0, <2.0.0",
        "aws-cdk.aws-events-targets>=1.100.0, <2.0.0",
        "aws-cdk.aws-iam>=1.100.0, <2.0.0",
        "aws-cdk.aws-lambda>=1.100.0, <2.0.0",
        "aws-cdk.aws-s3>=1.100.0, <2.0.0",
        "aws-cdk.aws-secretsmanager>=1.100.0, <2.0.0",
        "aws-cdk.aws-ssm>=1.100.0, <2.0.0",
        "aws-cdk.core>=1.100.0, <2.0.0",
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
