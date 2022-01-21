import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "renovosolutions.aws-cdk-aspects-security-group",
    "version": "1.0.38",
    "description": "A library of CDK aspects applying to security groups.",
    "license": "Apache-2.0",
    "url": "https://github.com/RenovoSolutions/cdk-aspects-library-security-group.git",
    "long_description_content_type": "text/markdown",
    "author": "Renovo Solutions<webmaster+cdk@renovo1.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/RenovoSolutions/cdk-aspects-library-security-group.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "aspects-security-group",
        "aspects-security-group._jsii"
    ],
    "package_data": {
        "aspects-security-group._jsii": [
            "cdk-aspects-library-security-group@1.0.38.jsii.tgz"
        ],
        "aspects-security-group": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-ec2>=1.140.0, <2.0.0",
        "aws-cdk.core>=1.140.0, <2.0.0",
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
