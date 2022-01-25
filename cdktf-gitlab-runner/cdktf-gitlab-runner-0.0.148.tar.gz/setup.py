import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdktf-gitlab-runner",
    "version": "0.0.148",
    "description": "The CDK for Terraform Construct for Gitlab Runner on GCP",
    "license": "Apache-2.0",
    "url": "https://github.com/neilkuan/cdktf-gitlab-runner.git",
    "long_description_content_type": "text/markdown",
    "author": "Neil Kuan<guan840912@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/neilkuan/cdktf-gitlab-runner.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdktf_gitlab_runner",
        "cdktf_gitlab_runner._jsii"
    ],
    "package_data": {
        "cdktf_gitlab_runner._jsii": [
            "cdktf-gitlab-runner@0.0.148.jsii.tgz"
        ],
        "cdktf_gitlab_runner": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "cdktf-cdktf-provider-google>=0.5.143, <0.6.0",
        "cdktf>=0.8.3, <0.9.0",
        "constructs>=10.0.0, <11.0.0",
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
