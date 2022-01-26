import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cloudyns",
    version="0.0.1",
    author="yoyojlf",
    author_email="jordhan@computerapes.com",
    description="cloudyns is a mini tool for managing cloud dns, mainly DigitalOcean, support for other services is "
                "expected to be added soon",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yoyojlf/cloudyns",
    project_urls={
        "Bug Tracker": "https://github.com/yoyojlf/cloudyns/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
