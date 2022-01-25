import setuptools


setuptools.setup(
    name="awsservicespkg",
    author="yashleo1018",
    description="awsservicespkg for AWS services",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    py_modules=["awsservicespkg"],
    include_package_data=True,
    install_requires=['boto3==1.18.36', 'botocore~=1.21.42']
)
