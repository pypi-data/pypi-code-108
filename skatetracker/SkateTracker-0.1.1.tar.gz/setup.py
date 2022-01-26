from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name="SkateTracker",
    version="0.1.1",
    description="CLI tool to track speed skating races",
    long_description=readme(),
    long_description_content_type="text/markdown",
    author="Hidde Fokkema",
    url="https://github.com/HiddeFok/CLI_speed_skating_tracker",
    license="MIT",
    keywords="CLI sports visualization",
    packages=[
        "SkateTracker"
    ],
    python_requires=">=3.5",
    install_requires=[
        "numpy==1.22.0",
        "plotext==4.1.5",
        "rich==11.0.0"
    ],
    entry_points={
        "console_scripts": [
            "SkateTracker = SkateTracker.main:main"
        ]
    }
)