import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "pwrdrvr.microapps.nextjsdemoappcdk",
    "version": "0.2.1",
    "description": "NextJS Demo app deployed to the MicroApps framework",
    "license": "MIT",
    "url": "https://github.com/pwrdrvr/serverless-nextjs-demo",
    "long_description_content_type": "text/markdown",
    "author": "PwrDrvr LLC",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/pwrdrvr/serverless-nextjs-demo"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "pwrdrvr.microapps.nextjsdemoappcdk",
        "pwrdrvr.microapps.nextjsdemoappcdk._jsii"
    ],
    "package_data": {
        "pwrdrvr.microapps.nextjsdemoappcdk._jsii": [
            "microapps-app-nextjs-demo-cdk@0.2.1.jsii.tgz"
        ],
        "pwrdrvr.microapps.nextjsdemoappcdk": [
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
