import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="minetext",
    version="0.2.3",
    author="Triet Doan",
    author_email="triet.doan@gwdg.de",
    description="Python client for MINE system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.gwdg.de/mine/mine-python",
    packages=setuptools.find_packages(),
    install_requires=[
        'elasticsearch-dsl'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Development Status :: 1 - Planning"
    ],
    python_requires='>=3.6',
)
