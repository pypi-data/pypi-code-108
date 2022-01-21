import setuptools
import os
import re

with open("README.md") as fp:
    long_description = fp.read()

# reading pymlconf version (same way sqlalchemy does)
with open(os.path.join(os.path.dirname(__file__), "aws_cdk_constructs", "__init__.py")) as v_file:
    package_version = (
        re.compile(r".*__version__ = '(.*?)'", re.S).match(v_file.read()).group(1)
    )

setuptools.setup(
    name="aws_cdk_constructs",
    version=package_version,
    description="AWS CDK constructs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="author",
    author_email="author@foa.org",
    packages=setuptools.find_packages(include=["aws_cdk_constructs", "aws_cdk_constructs.*"]),
    include_package_data=True,
    url="https://bitbucket.org/cioapps/aws-cdk-constructs",
    install_requires=[
        "aws-cdk.assets==1.139.0",
        "aws-cdk.aws-apigateway==1.139.0",
        "aws-cdk.aws-applicationautoscaling==1.139.0",
        "aws-cdk.aws-autoscaling==1.139.0",
        "aws-cdk.aws-autoscaling-common==1.139.0",
        "aws-cdk.aws-autoscaling-hooktargets==1.139.0",
        "aws-cdk.aws-certificatemanager==1.139.0",
        "aws-cdk.aws-cloudformation==1.139.0",
        "aws-cdk.aws-cloudwatch==1.139.0",
        "aws-cdk.aws-codeguruprofiler==1.139.0",
        "aws-cdk.aws-dynamodb==1.139.0",
        "aws-cdk.aws-ec2==1.139.0",
        "aws-cdk.aws-efs==1.139.0",
        "aws-cdk.aws-elasticloadbalancing==1.139.0",
        "aws-cdk.aws-elasticloadbalancingv2==1.139.0",
        "aws-cdk.aws-events==1.139.0",
        "aws-cdk.aws-iam==1.139.0",
        "aws-cdk.aws-kms==1.139.0",
        "aws-cdk.aws-lambda==1.139.0",
        "aws-cdk.aws-logs==1.139.0",
        "aws-cdk.aws-rds==1.139.0",
        "aws-cdk.aws-route53==1.139.0",
        "aws-cdk.aws-s3==1.139.0",
        "aws-cdk.aws-s3-assets==1.139.0",
        "aws-cdk.aws-sam==1.139.0",
        "aws-cdk.aws-secretsmanager==1.139.0",
        "aws-cdk.aws-sns==1.139.0",
        "aws-cdk.aws-sns-subscriptions==1.139.0",
        "aws-cdk.aws-sqs==1.139.0",
        "aws-cdk.aws-ssm==1.139.0",
        "aws-cdk.cdk-assets-schema==1.139.0",
        "aws-cdk.cloud-assembly-schema==1.139.0",
        "aws-cdk.core==1.139.0",
        "aws-cdk.custom-resources==1.139.0",
        "aws-cdk.cx-api==1.139.0",
        "aws-cdk.region-info==1.139.0",
        "aws-cdk.aws-cloudfront-origins==1.139.0",
        "boto3==1.16.16",
        "cloudcomponents.cdk-cloudfront-authorization==1.50.0",
        "cloudcomponents.cdk-lambda-at-edge-pattern==1.49.0"
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
