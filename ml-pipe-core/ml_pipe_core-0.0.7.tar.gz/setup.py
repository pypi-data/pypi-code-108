

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ml_pipe_core",
    version="0.0.7",
    author="Michael Boese",
    author_email="michael.boese@desy.de",
    description="Machine learning pipeline for accelerators",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/desy-ml/ml-pipeline",
    project_urls={
        "Bug Tracker": "https://github.com/desy-ml/ml-pipeline/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    install_requires=['confluent-kafka', 'requests', 'pyyaml', 'python-logstash', 'numpy', 'dacite', 'mysql-connector-python', 'accelerator-toolbox'],
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
)
