import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cvmodule",
    version="0.0.5",
    author="YuHe",
    author_email="1941254847@qq.com",
    description="modules related to deep learning in computer vision",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YuHe0108/cvmodule",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
