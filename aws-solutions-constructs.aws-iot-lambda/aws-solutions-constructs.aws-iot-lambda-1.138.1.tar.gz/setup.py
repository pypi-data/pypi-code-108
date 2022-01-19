import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "aws-solutions-constructs.aws-iot-lambda",
    "version": "1.138.1",
    "description": "CDK Constructs for AWS IoT to AWS Lambda integration",
    "license": "Apache-2.0",
    "url": "https://github.com/awslabs/aws-solutions-constructs.git",
    "long_description_content_type": "text/markdown",
    "author": "Amazon Web Services",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/awslabs/aws-solutions-constructs.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "aws_solutions_constructs.aws_iot_lambda",
        "aws_solutions_constructs.aws_iot_lambda._jsii"
    ],
    "package_data": {
        "aws_solutions_constructs.aws_iot_lambda._jsii": [
            "aws-iot-lambda@1.138.1.jsii.tgz"
        ],
        "aws_solutions_constructs.aws_iot_lambda": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-iam==1.138.1",
        "aws-cdk.aws-iot==1.138.1",
        "aws-cdk.aws-lambda==1.138.1",
        "aws-cdk.core==1.138.1",
        "aws-solutions-constructs.core==1.138.1",
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
