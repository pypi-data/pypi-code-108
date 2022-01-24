import setuptools
import aws_mlops

setuptools.setup(
    name="aws-mlops",
    version=aws_mlops.__version__,
    author=aws_mlops.__author__,
    author_email="alessandra.bilardi@gmail.com",
    description="AWS MLOps Python package",
    long_description=open('README.rst').read(),
    long_description_content_type="text/x-rst",
    url="https://aws-mlops.readthedocs.io/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    project_urls={
        "Source":"https://github.com/bilardi/aws-mlops",
        "Bug Reports":"https://github.com/bilardi/aws-mlops/issues",
        "Funding":"https://donate.pypi.org",
    },
)
