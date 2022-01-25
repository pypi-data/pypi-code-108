import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdktf-cdk8s",
    "version": "0.0.17",
    "description": "A compatability layer for using cdk8s constructs within Terraform CDK.",
    "license": "MIT",
    "url": "https://github.com/DanielMSchmidt/cdktf-cdk8s.git",
    "long_description_content_type": "text/markdown",
    "author": "Daniel Schmidt<danielmschmidt92@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/DanielMSchmidt/cdktf-cdk8s.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdktf_cdk8s",
        "cdktf_cdk8s._jsii"
    ],
    "package_data": {
        "cdktf_cdk8s._jsii": [
            "cdktf-cdk8s@0.0.17.jsii.tgz"
        ],
        "cdktf_cdk8s": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "cdk8s>=2.1.6",
        "cdktf-cdktf-provider-kubernetes>=0.5.129",
        "cdktf>=0.8.5, <0.9.0",
        "constructs>=10.0.25, <11.0.0",
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
