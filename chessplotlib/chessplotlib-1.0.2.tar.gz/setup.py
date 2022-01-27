import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="chessplotlib",
    description="Chess plots with matplotlib",
    long_description=long_description,
    long_description_content_type="text/markdown",
    scripts=["bin/pgn-viewer"],
    version="1.0.2",
    packages=["chessplotlib"],
    python_requires=">=3",
    install_requires=["matplotlib", "numpy", "chess"],
)
