from setuptools import setup


def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="delphai_backend_utils",
    version="1.0.10",
    description="A Python package to manage kube secrets.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/delphai/delphai-backend-utils",
    author="Delphai",
    author_email="ziyad@delphai.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["delphai_backend_utils"],
    include_package_data=True,
    install_requires=[
        'omegaconf', 'memoization',
        'azure-identity==1.4.0b3', 'azure-keyvault',
        'python-dotenv', 'coloredlogs',
        'kubernetes', 'keyring'],
)
