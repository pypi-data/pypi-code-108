import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-codepipeline-badge-notification",
    "version": "2.0.35",
    "description": "cdk-codepipeline-badge-notification",
    "license": "Apache-2.0",
    "url": "https://github.com/kimisme9386/cdk-codepipeline-badge-notification",
    "long_description_content_type": "text/markdown",
    "author": "Chris Yang",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/kimisme9386/cdk-codepipeline-badge-notification"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_codepipeline_badge_notification",
        "cdk_codepipeline_badge_notification._jsii"
    ],
    "package_data": {
        "cdk_codepipeline_badge_notification._jsii": [
            "cdk-codepipeline-badge-notification@2.0.35.jsii.tgz"
        ],
        "cdk_codepipeline_badge_notification": [
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
