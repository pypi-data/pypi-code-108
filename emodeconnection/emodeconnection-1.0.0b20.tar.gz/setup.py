import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="emodeconnection",
    version="1.0.0b20",
    author="EMode Photonix LLC",
    author_email="EModeSolver@gmail.com",
    description="Python connection for EMode",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/emode-photonix/emodeconnection",
    packages=setuptools.find_packages(),
    install_requires=[
        "numpy", "dill", "scipy",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
    ],
    python_requires='>=3.6',
)

