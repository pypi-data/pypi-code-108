import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk8s-cluster-autoscaler-aws",
    "version": "0.1.0",
    "description": "@opencdk8s/cdk8s-cluster-autoscaler-aws",
    "license": "Apache-2.0",
    "url": "https://github.com/opencdk8s/cdk8s-cluster-autoscaler-aws",
    "long_description_content_type": "text/markdown",
    "author": "Hunter Thompson<aatman@auroville.org.in>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/opencdk8s/cdk8s-cluster-autoscaler-aws"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk8s_cluster_autoscaler_aws",
        "cdk8s_cluster_autoscaler_aws._jsii"
    ],
    "package_data": {
        "cdk8s_cluster_autoscaler_aws._jsii": [
            "cdk8s-cluster-autoscaler-aws@0.1.0.jsii.tgz"
        ],
        "cdk8s_cluster_autoscaler_aws": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk-lib==2.8.0",
        "cdk8s>=2.1.23, <3.0.0",
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
