from setuptools import find_packages, setup

version = "0.4"

setup(
    name="nig-upload",
    version=version,
    description="CLI script for automated uploads of NIG studies",
    url="",
    license="MIT",
    packages=find_packages(where=".", exclude=["tests*"]),
    package_data={"nig": []},
    python_requires=">=3.7.0",
    entry_points={
        "console_scripts": ["nig-upload=nig.__main__:main"],
    },
    install_requires=[
        "python-dateutil",
        "pytz",
        "requests>=2.6.1",
        "typer[all]==0.4.0",
        "click==8.0.1",
        "pyOpenSSL",
    ],
    classifiers=[
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        # End-of-life: 2023-06-27
        "Programming Language :: Python :: 3.7",
        # End-of-life: 2024-10
        "Programming Language :: Python :: 3.8",
        # End-of-life: 2025-10
        "Programming Language :: Python :: 3.9",
    ],
)
