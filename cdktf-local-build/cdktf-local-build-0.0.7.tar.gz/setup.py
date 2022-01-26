import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdktf-local-build",
    "version": "0.0.7",
    "description": "A construct that encapsulates different building methods, e.g. for Node, Rust, Docker.",
    "license": "Apache-2.0",
    "url": "https://github.com/DanielMSchmidt/cdktf-local-build.git",
    "long_description_content_type": "text/markdown",
    "author": "Daniel Schmidt<danielmschmidt92@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/DanielMSchmidt/cdktf-local-build.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdktf_local_build",
        "cdktf_local_build._jsii"
    ],
    "package_data": {
        "cdktf_local_build._jsii": [
            "cdktf-local-build@0.0.7.jsii.tgz"
        ],
        "cdktf_local_build": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "cdktf-cdktf-provider-null>=0.5.0",
        "cdktf-local-exec>=0.0.20",
        "cdktf>=0.9.0, <0.10.0",
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
