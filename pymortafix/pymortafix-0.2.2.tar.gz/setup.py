import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pymortafix",
    version="0.2.2",
    author="Moris Doratiotto",
    author_email="moris.doratiotto@gmail.com",
    description="A python module to collect some usefull stuff",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mortafix/PyMortafix",
    packages=setuptools.find_packages(),
    install_requires=["colorifix", "emoji"],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.8",
    keywords=[
        "telegram",
        "bot",
        "utils",
    ],
)
