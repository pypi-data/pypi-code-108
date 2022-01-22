import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="authc",
    version="0.1.1",  # Latest version .
    author="R2FsCg",
    author_email="r2fscg@gmail.com",
    description="For authentication.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/private_repo/codefast",
    packages=setuptools.find_packages(),
    install_requires=['codefast'],
    entry_points={'console_scripts': ['auth=authc:authc']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
