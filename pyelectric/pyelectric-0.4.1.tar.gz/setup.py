import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyelectric",
    version="0.4.1",
    author="luanws",
    author_email="luan.w.silveira@gmail.com",
    description="Python package for electric circuits",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/luanws/pyelectric",
    packages=setuptools.find_packages(include=['pyelectric', 'pyelectric.*']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'numpy',
        'matplotlib',
    ],
    python_requires='>=3.7',
)
