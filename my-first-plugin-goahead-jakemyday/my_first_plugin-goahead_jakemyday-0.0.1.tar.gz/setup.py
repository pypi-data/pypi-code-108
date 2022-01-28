import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="my_first_plugin-goahead_jakemyday",
    version="0.0.1",
    author="Jake Mackinlay",
    author_email="jmackinlay@lumination.com.au",
    description="A small example package to learn how to upload packages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jakemackinlay/opensesame_plugin_0.1",
    # project_urls={
    #     "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    # },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)