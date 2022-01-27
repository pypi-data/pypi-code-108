import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "monocdk-nag",
    "version": "1.4.34",
    "description": "Check CDK applications for best practices using a combination on available rule packs.",
    "license": "Apache-2.0",
    "url": "https://github.com/cdklabs/cdk-nag.git",
    "long_description_content_type": "text/markdown",
    "author": "Arun Donti<donti@amazon.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/cdklabs/cdk-nag.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "monocdk_nag",
        "monocdk_nag._jsii"
    ],
    "package_data": {
        "monocdk_nag._jsii": [
            "monocdk-nag@1.4.34.jsii.tgz"
        ],
        "monocdk_nag": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.core>=1.123.0, <2.0.0",
        "constructs>=3.2.27, <4.0.0",
        "jsii>=1.52.1, <2.0.0",
        "monocdk>=1.123.0, <2.0.0",
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
