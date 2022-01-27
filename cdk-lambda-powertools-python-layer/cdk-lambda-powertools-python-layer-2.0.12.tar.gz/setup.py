import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-lambda-powertools-python-layer",
    "version": "2.0.12",
    "description": "A lambda layer for AWS Powertools for python",
    "license": "MIT-0",
    "url": "https://github.com/aws-samples/cdk-lambda-powertools-python-layer.git",
    "long_description_content_type": "text/markdown",
    "author": "Amazon Web Services",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/aws-samples/cdk-lambda-powertools-python-layer.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_lambda_powertools_python_layer",
        "cdk_lambda_powertools_python_layer._jsii"
    ],
    "package_data": {
        "cdk_lambda_powertools_python_layer._jsii": [
            "cdk-lambda-powertools-python-layer@2.0.12.jsii.tgz"
        ],
        "cdk_lambda_powertools_python_layer": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk-lib>=2.2.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
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
