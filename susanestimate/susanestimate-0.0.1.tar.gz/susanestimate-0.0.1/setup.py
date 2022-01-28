import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="susanestimate",
    version="0.0.1",
    author="Susan Hou",
    author_email="1055306071@qq.com",
    description="A package to calculate precision and recall about detection model",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xuaner11111/susanestimate",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['numpy', 'matplotlib', 'opencv-python'],
    packages=setuptools.find_packages(where="susanestimate"),
    python_requires=">=3.6",
)
