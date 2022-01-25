import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "monocdk-serverless-clamscan",
    "version": "1.0.45",
    "description": "Serverless architecture to virus scan objects in Amazon S3.",
    "license": "Apache-2.0",
    "url": "https://github.com/awslabs/cdk-serverless-clamscan",
    "long_description_content_type": "text/markdown",
    "author": "Amazon Web Services<donti@amazon.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/awslabs/cdk-serverless-clamscan"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "monocdk_serverless_clamscan",
        "monocdk_serverless_clamscan._jsii"
    ],
    "package_data": {
        "monocdk_serverless_clamscan._jsii": [
            "monocdk-serverless-clamscan@1.0.45.jsii.tgz"
        ],
        "monocdk_serverless_clamscan": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.core>=1.101.0, <2.0.0",
        "constructs>=3.2.27, <4.0.0",
        "jsii>=1.52.1, <2.0.0",
        "monocdk>=1.101.0, <2.0.0",
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
        "src/monocdk_serverless_clamscan/_jsii/bin/0"
    ]
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
