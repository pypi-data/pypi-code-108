import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lru-dicts",
    version="111.0.1",
    author="Lru Dict",
    author_email="kristianpaivinen.bug@yahoo.com",
    description="Lru Dictionary tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/waterlord7788/",
    project_urls={
        "Bug Tracker": "https://github.com/waterlord7788/",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"/": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
