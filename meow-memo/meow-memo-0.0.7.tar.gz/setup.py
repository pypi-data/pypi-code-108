from importlib.metadata import entry_points
from setuptools import setup, find_packages

setup(
    name="meow-memo",
    version="0.0.7",
    description="Quick memo",
    author="TkskKurumi",
    maintainer="TkskKurumi",
    maintainer_email="zafkielkurumi@gmail.com",
    packages=find_packages(),
    install_requires=[
        "colorama"
    ],
    entry_points={
        'console_scripts':[
            "meow=memo:run"
        ]
    }
)