import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cloudcomponents.cdk-blue-green-container-deployment",
    "version": "1.51.0",
    "description": "Blue green container deployment with CodeDeploy",
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
        "cloudcomponents.cdk_blue_green_container_deployment",
        "cloudcomponents.cdk_blue_green_container_deployment._jsii"
    ],
    "package_data": {
        "cloudcomponents.cdk_blue_green_container_deployment._jsii": [
            "cdk-blue-green-container-deployment@1.51.0.jsii.tgz"
        ],
        "cloudcomponents.cdk_blue_green_container_deployment": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-codebuild>=1.140.0, <2.0.0",
        "aws-cdk.aws-codedeploy>=1.140.0, <2.0.0",
        "aws-cdk.aws-ec2>=1.140.0, <2.0.0",
        "aws-cdk.aws-ecr>=1.140.0, <2.0.0",
        "aws-cdk.aws-ecs>=1.140.0, <2.0.0",
        "aws-cdk.aws-elasticloadbalancingv2>=1.140.0, <2.0.0",
        "aws-cdk.aws-iam>=1.140.0, <2.0.0",
        "aws-cdk.aws-lambda>=1.140.0, <2.0.0",
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
