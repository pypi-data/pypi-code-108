import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-lambda-layer-curl",
    "version": "1.0.27",
    "description": "For lambda layer use curl",
    "license": "Apache-2.0",
    "url": "https://github.com/clarencetw/cdk-lambda-layer-curl.git",
    "long_description_content_type": "text/markdown",
    "author": "clarencetw<mr.lin.clarence@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/clarencetw/cdk-lambda-layer-curl.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_lambda_layer_curl",
        "cdk_lambda_layer_curl._jsii"
    ],
    "package_data": {
        "cdk_lambda_layer_curl._jsii": [
            "cdk-lambda-layer-curl@1.0.27.jsii.tgz"
        ],
        "cdk_lambda_layer_curl": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-lambda>=1.136.0, <2.0.0",
        "aws-cdk.core>=1.136.0, <2.0.0",
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
