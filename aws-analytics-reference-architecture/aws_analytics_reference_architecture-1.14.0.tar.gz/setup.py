import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "aws_analytics_reference_architecture",
    "version": "1.14.0",
    "description": "aws-analytics-reference-architecture",
    "license": "MIT-0",
    "url": "https://aws-samples.github.io/aws-analytics-reference-architecture/",
    "long_description_content_type": "text/markdown",
    "author": "Amazon Web Services",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/aws-samples/aws-analytics-reference-architecture.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "aws_analytics_reference_architecture",
        "aws_analytics_reference_architecture._jsii"
    ],
    "package_data": {
        "aws_analytics_reference_architecture._jsii": [
            "aws-analytics-reference-architecture@1.14.0.jsii.tgz"
        ],
        "aws_analytics_reference_architecture": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.assertions==1.139.0",
        "aws-cdk.aws-athena==1.139.0",
        "aws-cdk.aws-autoscaling==1.139.0",
        "aws-cdk.aws-ec2==1.139.0",
        "aws-cdk.aws-eks==1.139.0",
        "aws-cdk.aws-emr==1.139.0",
        "aws-cdk.aws-emrcontainers==1.139.0",
        "aws-cdk.aws-events-targets==1.139.0",
        "aws-cdk.aws-events==1.139.0",
        "aws-cdk.aws-glue==1.139.0",
        "aws-cdk.aws-iam==1.139.0",
        "aws-cdk.aws-kinesis==1.139.0",
        "aws-cdk.aws-kinesisfirehose-destinations==1.139.0",
        "aws-cdk.aws-kinesisfirehose==1.139.0",
        "aws-cdk.aws-kms==1.139.0",
        "aws-cdk.aws-lambda-python==1.139.0",
        "aws-cdk.aws-lambda==1.139.0",
        "aws-cdk.aws-logs==1.139.0",
        "aws-cdk.aws-redshift==1.139.0",
        "aws-cdk.aws-s3-assets==1.139.0",
        "aws-cdk.aws-s3-deployment==1.139.0",
        "aws-cdk.aws-s3==1.139.0",
        "aws-cdk.aws-secretsmanager==1.139.0",
        "aws-cdk.aws-stepfunctions-tasks==1.139.0",
        "aws-cdk.aws-stepfunctions==1.139.0",
        "aws-cdk.core==1.139.0",
        "aws-cdk.custom-resources==1.139.0",
        "aws-cdk.lambda-layer-awscli==1.139.0",
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
