import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-prowler",
    "version": "2.9.0",
    "description": "An AWS CDK custom construct for deploying Prowler to you AWS Account. The following description about Prowler is taken from https://github.com/toniblyx/prowler: Prowler is a security tool to perform AWS security best practices assessments, audits, incident response, continuous monitoring, hardening and forensics readiness. It contains all CIS controls listed here https://d0.awsstatic.com/whitepapers/compliance/AWS_CIS_Foundations_Benchmark.pdf and more than 100 additional checks that help on GDPR, HIPAA …",
    "license": "Apache-2.0",
    "url": "https://github.com/mmuller88/cdk-prowler",
    "long_description_content_type": "text/markdown",
    "author": "Martin Mueller<damadden88@googlemail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/mmuller88/cdk-prowler"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_prowler",
        "cdk_prowler._jsii"
    ],
    "package_data": {
        "cdk_prowler._jsii": [
            "cdk-prowler@2.9.0.jsii.tgz"
        ],
        "cdk_prowler": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk-lib>=2.9.0, <3.0.0",
        "cdk-iam-floyd>=0.301.0, <0.302.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.47.0, <2.0.0",
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
