import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "aws-solutions-constructs.aws-dynamodbstreams-lambda-elasticsearch-kibana",
    "version": "1.138.1",
    "description": "CDK Constructs for Amazon Dynamodb streams to AWS Lambda to AWS Elasticsearch with Kibana integration",
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
        "aws_solutions_constructs.aws_dynamodbstreams_lambda_elasticsearch_kibana",
        "aws_solutions_constructs.aws_dynamodbstreams_lambda_elasticsearch_kibana._jsii"
    ],
    "package_data": {
        "aws_solutions_constructs.aws_dynamodbstreams_lambda_elasticsearch_kibana._jsii": [
            "aws-dynamodbstreams-lambda-elasticsearch-kibana@1.138.1.jsii.tgz"
        ],
        "aws_solutions_constructs.aws_dynamodbstreams_lambda_elasticsearch_kibana": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-cloudwatch==1.138.1",
        "aws-cdk.aws-cognito==1.138.1",
        "aws-cdk.aws-dynamodb==1.138.1",
        "aws-cdk.aws-elasticsearch==1.138.1",
        "aws-cdk.aws-iam==1.138.1",
        "aws-cdk.aws-lambda-event-sources==1.138.1",
        "aws-cdk.aws-lambda==1.138.1",
        "aws-cdk.aws-sqs==1.138.1",
        "aws-cdk.core==1.138.1",
        "aws-solutions-constructs.aws-dynamodbstreams-lambda==1.138.1",
        "aws-solutions-constructs.aws-lambda-elasticsearch-kibana==1.138.1",
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
