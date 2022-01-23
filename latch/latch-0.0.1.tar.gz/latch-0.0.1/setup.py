from setuptools import setup

setup(
    name="latch",
    version="0.0.1",
    author_email="kenny@latch.bio",
    description="latch sdk",
    entry_points={
        "console_scripts": [
            "latch=latch.cli.main:main",
        ]
    },
)
