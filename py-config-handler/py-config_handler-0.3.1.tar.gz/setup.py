from setuptools import setup

with open("README.md", "r") as f:
    README = f.read()

setup(
    name="py-config_handler",
    version="0.3.1",
    description="Create, update, and remove values from a configuration file made by ConfigHandler.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Chris1320/ConfigHandler-python",
    author="Chris1320",
    author_email="chris1320is@protonmail.com",
    license="MIT",
    classifiers=[  # https://pypi.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7"
    ],
    packages=["config_handler"],
    include_package_data=True,
    install_requires=["pycryptodomex", "prettytable"],
    entry_points={
        "console_scripts": [
            "config_handler=config_handler.__main__:main",
        ]
    },
)
