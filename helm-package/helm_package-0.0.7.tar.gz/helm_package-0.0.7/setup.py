import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="helm_package",
    version="0.0.7",
    author="tinson",
    author_email="tinson.liu@6317.io",
    description="helm bin package for wins and macos including helm2 and helm3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/helm_bin",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/helm_bin/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    data_files=[
        ('/helm_package/bin/macos',['src/helm_package/bin/macos/helm2']),
        ('/helm_package/bin/macos',['src/helm_package/bin/macos/helm3']),
        ('/helm_package/bin/windows',['src/helm_package/bin/windows/helm2.exe']),
        ('/helm_package/bin/windows',['src/helm_package/bin/windows/helm3.exe'])
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)