import os
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

try:
    requirementsFilePath = os.path.dirname(os.path.abspath(__file__)) + "/requirements.txt"
    requirements = open(requirementsFilePath, "r").read().splitlines()
except Exception:
    requirements = ["nwmodule", "numpy", "h5py", "torch", "tqdm", "media-processing-lib", "nwutils", "overrides", \
        "scikit-learn", "matplotlib", "graphviz", "pyyaml", "opencv-python", "flow_vis", "natsort"]

setuptools.setup(
    name="ngclib", # Replace with your own username
    version="0.03",
    author="Mihai Cristian Pîrvu",
    author_email="mihaicristianpirvu@gmail.com",
    description="Generic PyTorch high level neural API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/neuralwrappers/ngclib",
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
