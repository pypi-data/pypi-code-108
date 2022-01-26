import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="seavoice-sdk",
    version="0.2.4",
    author="Seasalt.ai",
    author_email="info@seasalt.ai",
    description="SeaVoice SDK: Client for Seasalt speech recognition and speech synthesis.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[
        'websocket-client==0.57.0',
        'websockets==8.1',
        'ws4py==0.5.1'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
