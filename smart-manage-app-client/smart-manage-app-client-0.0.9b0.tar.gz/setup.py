from setuptools import setup, find_packages

setup(
    name="smart-manage-app-client",
    version='0.0.9b',
    packages=find_packages(),
    install_requires=["requests>=2.18.2", "pytz", "smart-manage-crypt"],
)
