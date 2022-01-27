import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-nag",
    "version": "1.4.34",
    "description": "Check CDK applications for best practices using a combination on available rule packs.",
    "license": "Apache-2.0",
    "url": "https://github.com/cdklabs/cdk-nag.git",
    "long_description_content_type": "text/markdown",
    "author": "Arun Donti<donti@amazon.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/cdklabs/cdk-nag.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_nag",
        "cdk_nag._jsii"
    ],
    "package_data": {
        "cdk_nag._jsii": [
            "cdk-nag@1.4.34.jsii.tgz"
        ],
        "cdk_nag": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-apigateway>=1.123.0, <2.0.0",
        "aws-cdk.aws-apigatewayv2-authorizers>=1.123.0, <2.0.0",
        "aws-cdk.aws-apigatewayv2-integrations>=1.123.0, <2.0.0",
        "aws-cdk.aws-apigatewayv2>=1.123.0, <2.0.0",
        "aws-cdk.aws-applicationautoscaling>=1.123.0, <2.0.0",
        "aws-cdk.aws-appsync>=1.123.0, <2.0.0",
        "aws-cdk.aws-athena>=1.123.0, <2.0.0",
        "aws-cdk.aws-autoscaling>=1.123.0, <2.0.0",
        "aws-cdk.aws-backup>=1.123.0, <2.0.0",
        "aws-cdk.aws-certificatemanager>=1.123.0, <2.0.0",
        "aws-cdk.aws-cloud9>=1.123.0, <2.0.0",
        "aws-cdk.aws-cloudfront-origins>=1.123.0, <2.0.0",
        "aws-cdk.aws-cloudfront>=1.123.0, <2.0.0",
        "aws-cdk.aws-cloudtrail>=1.123.0, <2.0.0",
        "aws-cdk.aws-cloudwatch-actions>=1.123.0, <2.0.0",
        "aws-cdk.aws-cloudwatch>=1.123.0, <2.0.0",
        "aws-cdk.aws-codebuild>=1.123.0, <2.0.0",
        "aws-cdk.aws-cognito>=1.123.0, <2.0.0",
        "aws-cdk.aws-dax>=1.123.0, <2.0.0",
        "aws-cdk.aws-dms>=1.123.0, <2.0.0",
        "aws-cdk.aws-docdb>=1.123.0, <2.0.0",
        "aws-cdk.aws-dynamodb>=1.123.0, <2.0.0",
        "aws-cdk.aws-ec2>=1.123.0, <2.0.0",
        "aws-cdk.aws-ecr>=1.123.0, <2.0.0",
        "aws-cdk.aws-ecs>=1.123.0, <2.0.0",
        "aws-cdk.aws-efs>=1.123.0, <2.0.0",
        "aws-cdk.aws-eks>=1.123.0, <2.0.0",
        "aws-cdk.aws-elasticache>=1.123.0, <2.0.0",
        "aws-cdk.aws-elasticbeanstalk>=1.123.0, <2.0.0",
        "aws-cdk.aws-elasticloadbalancing>=1.123.0, <2.0.0",
        "aws-cdk.aws-elasticloadbalancingv2>=1.123.0, <2.0.0",
        "aws-cdk.aws-elasticsearch>=1.123.0, <2.0.0",
        "aws-cdk.aws-emr>=1.123.0, <2.0.0",
        "aws-cdk.aws-iam>=1.123.0, <2.0.0",
        "aws-cdk.aws-kinesis>=1.123.0, <2.0.0",
        "aws-cdk.aws-kinesisanalytics>=1.123.0, <2.0.0",
        "aws-cdk.aws-kinesisfirehose>=1.123.0, <2.0.0",
        "aws-cdk.aws-kms>=1.123.0, <2.0.0",
        "aws-cdk.aws-lambda>=1.123.0, <2.0.0",
        "aws-cdk.aws-logs>=1.123.0, <2.0.0",
        "aws-cdk.aws-mediastore>=1.123.0, <2.0.0",
        "aws-cdk.aws-msk>=1.123.0, <2.0.0",
        "aws-cdk.aws-neptune>=1.123.0, <2.0.0",
        "aws-cdk.aws-opensearchservice>=1.123.0, <2.0.0",
        "aws-cdk.aws-quicksight>=1.123.0, <2.0.0",
        "aws-cdk.aws-rds>=1.123.0, <2.0.0",
        "aws-cdk.aws-redshift>=1.123.0, <2.0.0",
        "aws-cdk.aws-s3>=1.123.0, <2.0.0",
        "aws-cdk.aws-sagemaker>=1.123.0, <2.0.0",
        "aws-cdk.aws-secretsmanager>=1.123.0, <2.0.0",
        "aws-cdk.aws-sns>=1.123.0, <2.0.0",
        "aws-cdk.aws-sqs>=1.123.0, <2.0.0",
        "aws-cdk.aws-stepfunctions>=1.123.0, <2.0.0",
        "aws-cdk.aws-timestream>=1.123.0, <2.0.0",
        "aws-cdk.aws-wafv2>=1.123.0, <2.0.0",
        "aws-cdk.core>=1.123.0, <2.0.0",
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
