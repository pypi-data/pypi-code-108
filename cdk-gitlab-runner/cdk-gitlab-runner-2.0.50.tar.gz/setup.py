import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-gitlab-runner",
    "version": "2.0.50",
    "description": "Use AWS CDK to create a gitlab runner, and use gitlab runner to help you execute your Gitlab pipeline job.",
    "license": "Apache-2.0",
    "url": "https://github.com/neilkuan/cdk-gitlab-runner.git",
    "long_description_content_type": "text/markdown",
    "author": "Neil Kuan<guan840912@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/neilkuan/cdk-gitlab-runner.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_gitlab_runner",
        "cdk_gitlab_runner._jsii"
    ],
    "package_data": {
        "cdk_gitlab_runner._jsii": [
            "cdk-gitlab-runner@2.0.50.jsii.tgz"
        ],
        "cdk_gitlab_runner": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk-lib>=2.1.0, <3.0.0",
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
