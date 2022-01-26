import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk8s-operator",
    "version": "0.0.162",
    "description": "Create Kubernetes CRD Operators using CDK8s Constructs",
    "license": "Apache-2.0",
    "url": "https://github.com/eladb/cdk8s-pack-prototype.git",
    "long_description_content_type": "text/markdown",
    "author": "Amazon Web Services",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/eladb/cdk8s-pack-prototype.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk8s_operator",
        "cdk8s_operator._jsii"
    ],
    "package_data": {
        "cdk8s_operator._jsii": [
            "cdk8s-operator@0.0.162.jsii.tgz"
        ],
        "cdk8s_operator": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "cdk8s>=1.4.13, <2.0.0",
        "constructs>=3.3.199, <4.0.0",
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
    "scripts": [
        "src/cdk8s_operator/_jsii/bin/cdk8s-server"
    ]
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
