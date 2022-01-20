import os
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

try:
    requirementsFilePath = os.path.dirname(os.path.abspath(__file__)) + "/requirements.txt"
    requirements = open(requirementsFilePath, "r").read().splitlines()
except Exception:
    requirements = ["torch", "matplotlib", "tqdm", "opencv-python", "h5py", "overrides", "scikit-learn", \
        "graphviz", "returns", "pims", "nwutils"]

setuptools.setup(
    name="nwmodule", # Replace with your own username
    version="0.4",
    author="Mihai Cristian Pîrvu",
    author_email="mihaicristianpirvu@gmail.com",
    description="Generic PyTorch high level neural API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/neuralwrappers/nwmodule",
    keywords = ["PyTorch", "neural network", "high level api"],
    packages=setuptools.find_packages(),
    install_requires=requirements,
    license="WTFPL",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
