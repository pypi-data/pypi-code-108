import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "paws.lambda-time-trigger",
    "version": "1.0.0",
    "description": "Implements sub-minute time trigger support to trigger AWS Lambda functions",
    "license": "Apache-2.0",
    "url": "https://github.com/ChristianEder/paws/packages/lambda-time-trigger",
    "long_description_content_type": "text/markdown",
    "author": "Christian Eder<christian.johann.eder@googlemail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/ChristianEder/paws.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "paws.lambda-time-trigger",
        "paws.lambda-time-trigger._jsii"
    ],
    "package_data": {
        "paws.lambda-time-trigger._jsii": [
            "paws-lambda-time-trigger@1.0.0.jsii.tgz"
        ],
        "paws.lambda-time-trigger": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk-lib==2.8.0",
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
