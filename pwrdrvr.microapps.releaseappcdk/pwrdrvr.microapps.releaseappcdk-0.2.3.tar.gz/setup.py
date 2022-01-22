import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "pwrdrvr.microapps.releaseappcdk",
    "version": "0.2.3",
    "description": "Release app for the MicroApps framework, by PwrDrvr LLC. Provides the ability to control which version of an app is launched.",
    "license": "MIT",
    "url": "https://github.com/pwrdrvr/microapps-app-release",
    "long_description_content_type": "text/markdown",
    "author": "PwrDrvr LLC",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/pwrdrvr/microapps-app-release"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "pwrdrvr.microapps.releaseappcdk",
        "pwrdrvr.microapps.releaseappcdk._jsii"
    ],
    "package_data": {
        "pwrdrvr.microapps.releaseappcdk._jsii": [
            "microapps-app-release-cdk@0.2.3.jsii.tgz"
        ],
        "pwrdrvr.microapps.releaseappcdk": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk-lib>=2.8.0, <3.0.0",
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
