import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "aws-solutions-constructs.aws-s3-stepfunctions",
    "version": "2.2.0",
    "description": "CDK Constructs for AWS S3 to AWS Step Functions integration",
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
        "aws_solutions_constructs.aws_s3_stepfunctions",
        "aws_solutions_constructs.aws_s3_stepfunctions._jsii"
    ],
    "package_data": {
        "aws_solutions_constructs.aws_s3_stepfunctions._jsii": [
            "aws-s3-stepfunctions@2.2.0.jsii.tgz"
        ],
        "aws_solutions_constructs.aws_s3_stepfunctions": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk-lib>=2.4.0, <3.0.0",
        "aws-solutions-constructs.aws-eventbridge-stepfunctions==2.2.0",
        "aws-solutions-constructs.core==2.2.0",
        "constructs>=10.0.0, <11.0.0",
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
