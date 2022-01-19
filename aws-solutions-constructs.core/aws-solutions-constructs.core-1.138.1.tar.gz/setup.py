import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "aws-solutions-constructs.core",
    "version": "1.138.1",
    "description": "Core CDK Construct for patterns library",
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
        "aws_solutions_constructs.core",
        "aws_solutions_constructs.core._jsii"
    ],
    "package_data": {
        "aws_solutions_constructs.core._jsii": [
            "core@1.138.1.jsii.tgz"
        ],
        "aws_solutions_constructs.core": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-apigateway==1.138.1",
        "aws-cdk.aws-certificatemanager==1.138.1",
        "aws-cdk.aws-cloudfront-origins==1.138.1",
        "aws-cdk.aws-cloudfront==1.138.1",
        "aws-cdk.aws-cloudwatch==1.138.1",
        "aws-cdk.aws-cognito==1.138.1",
        "aws-cdk.aws-dynamodb==1.138.1",
        "aws-cdk.aws-ec2==1.138.1",
        "aws-cdk.aws-ecr==1.138.1",
        "aws-cdk.aws-ecs==1.138.1",
        "aws-cdk.aws-elasticloadbalancingv2-targets==1.138.1",
        "aws-cdk.aws-elasticloadbalancingv2==1.138.1",
        "aws-cdk.aws-elasticsearch==1.138.1",
        "aws-cdk.aws-events==1.138.1",
        "aws-cdk.aws-glue==1.138.1",
        "aws-cdk.aws-iam==1.138.1",
        "aws-cdk.aws-iot==1.138.1",
        "aws-cdk.aws-kinesis==1.138.1",
        "aws-cdk.aws-kinesisanalytics==1.138.1",
        "aws-cdk.aws-kinesisfirehose==1.138.1",
        "aws-cdk.aws-kms==1.138.1",
        "aws-cdk.aws-lambda-event-sources==1.138.1",
        "aws-cdk.aws-lambda==1.138.1",
        "aws-cdk.aws-logs==1.138.1",
        "aws-cdk.aws-mediastore==1.138.1",
        "aws-cdk.aws-s3-assets==1.138.1",
        "aws-cdk.aws-s3-notifications==1.138.1",
        "aws-cdk.aws-s3==1.138.1",
        "aws-cdk.aws-sagemaker==1.138.1",
        "aws-cdk.aws-secretsmanager==1.138.1",
        "aws-cdk.aws-sns==1.138.1",
        "aws-cdk.aws-sqs==1.138.1",
        "aws-cdk.aws-ssm==1.138.1",
        "aws-cdk.aws-stepfunctions==1.138.1",
        "aws-cdk.aws-wafv2==1.138.1",
        "aws-cdk.core==1.138.1",
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
