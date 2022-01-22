import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "renovosolutions.aws-cdk-renovo-instance-service",
    "version": "2.1.31",
    "description": "CDK Construct Library to create instance based services utilizing default configurations for Renovo Solutions.",
    "license": "Apache-2.0",
    "url": "https://github.com/RenovoSolutions/cdk-library-renovo-instance-service.git",
    "long_description_content_type": "text/markdown",
    "author": "Renovo Solutions<webmaster+cdk@renovo1.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/RenovoSolutions/cdk-library-renovo-instance-service.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "renovo-instance-service",
        "renovo-instance-service._jsii"
    ],
    "package_data": {
        "renovo-instance-service._jsii": [
            "cdk-library-renovo-instance-service@2.1.31.jsii.tgz"
        ],
        "renovo-instance-service": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk-lib>=2.8.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.52.1, <2.0.0",
        "publication>=0.0.3",
        "renovosolutions.aws-cdk-aspects-security-group>=2.0.38, <3.0.0",
        "renovosolutions.aws-cdk-managed-instance-role>=2.1.36, <3.0.0"
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
