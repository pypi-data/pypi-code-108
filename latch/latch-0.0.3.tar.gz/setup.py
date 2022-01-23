from setuptools import find_packages, setup

setup(
    name="latch",
    version="0.0.3",
    author_email="kenny@latch.bio",
    description="latch sdk",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "latch=latch.cli.main:main",
        ]
    },
    install_requires=[
        "pyjwt==2.3.0",
        "requests==2.27.1",
        "click==7.1.2",
        "flyte==git+ssh://git@github.com/latchbio/flaightkit",
    ],
)
