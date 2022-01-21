import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tools-lyc7456",
    version="0.0.36",
    author="lyc7456",
    author_email="lyc7456gg1@gmail.com",
    description="lyc7456 运维开发小工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/lyc7456/tools-lyc7456.git",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        "requests",
        "bce-python-sdk>=0.8.61",
        "ucloud-sdk-python3",
        "tencentcloud-sdk-python",
        "paramiko==2.7.1",
        "alibabacloud_swas_open20200601==1.0.2",
    ],
)