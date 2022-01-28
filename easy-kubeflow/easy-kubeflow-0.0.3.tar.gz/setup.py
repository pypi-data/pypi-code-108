import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="easy-kubeflow",  # Replace with your own name
    version="0.0.3",
    author="CrazyBean",
    author_email="liuweibin@stonewise.cn",
    description="sdk help users for a better use of kubeflow",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://service.stonewise.cn:8029/liuweibin/easy-kubeflow.git",
    install_requires=[
        'docker>=4.2.1',
        'kfp==1.3.0',
        'pandas>=1.1.5',
        'tqdm>=4.56.0'
    ],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
