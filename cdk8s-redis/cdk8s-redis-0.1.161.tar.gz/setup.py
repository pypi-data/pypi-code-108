import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk8s-redis",
    "version": "0.1.161",
    "description": "Basic implementation of a Redis construct for cdk8s.",
    "license": "Apache-2.0",
    "url": "https://github.com/cdk8s-team/cdk8s-redis.git",
    "long_description_content_type": "text/markdown",
    "author": "Amazon Web Services<https://aws.amazon.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/cdk8s-team/cdk8s-redis.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk8s_redis",
        "cdk8s_redis._jsii"
    ],
    "package_data": {
        "cdk8s_redis._jsii": [
            "cdk8s-redis@0.1.161.jsii.tgz"
        ],
        "cdk8s_redis": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "cdk8s>=1.4.13, <2.0.0",
        "constructs>=3.3.200, <4.0.0",
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
        "Development Status :: 4 - Beta",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
