import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="datatransformer", # Replace with your own username
    version="0.1.7",
    author="Tim Su",
    author_email="omg80827@gmail.com",
    description="A package for data transformation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nextfortune/datatransformer.git",
    project_urls={
        "Bug Tracker": "https://github.com/nextfortune/datatransformer/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "tensorflow>=2.6.0",
        "vaex>=4.4.0"
    ]
)
