import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "renovosolutions.aws-cdk-managed-instance-role",
    "version": "1.0.37",
    "description": "AWS CDK Construct Library to create an instance role for instances managed by SSM and capable of joining an AWS managed domain.",
    "license": "Apache-2.0",
    "url": "https://github.com/RenovoSolutions/cdk-library-managed-instance-role.git",
    "long_description_content_type": "text/markdown",
    "author": "Renovo Solutions<webmaster+cdk@renovo1.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/RenovoSolutions/cdk-library-managed-instance-role.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "managed_instance_role",
        "managed_instance_role._jsii"
    ],
    "package_data": {
        "managed_instance_role._jsii": [
            "cdk-library-managed-instance-role@1.0.37.jsii.tgz"
        ],
        "managed_instance_role": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-iam>=1.140.0, <2.0.0",
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
