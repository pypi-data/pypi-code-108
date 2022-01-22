import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cloudcomponents.cdk-pull-request-approval-rule",
    "version": "1.49.0",
    "description": "CodeCommit pull request approval rules to enforcing your pull request workflow",
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
        "cloudcomponents.cdk_pull_request_approval_rule",
        "cloudcomponents.cdk_pull_request_approval_rule._jsii"
    ],
    "package_data": {
        "cloudcomponents.cdk_pull_request_approval_rule._jsii": [
            "cdk-pull-request-approval-rule@1.49.0.jsii.tgz"
        ],
        "cloudcomponents.cdk_pull_request_approval_rule": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-codecommit>=1.140.0, <2.0.0",
        "aws-cdk.aws-events>=1.140.0, <2.0.0",
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
