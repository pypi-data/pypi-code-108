import setuptools


setuptools.setup(
    name="UTubeToMP",
    version="0.0.1",
    author="Russian-Dev",
    author_email="russian.devv@gmail.com",
    description="Convert a YouTube video to MP4 or MP3.",
    url="https://github.com/Russian-Dev/UTubeToMP",
    project_urls={
        "Bug Tracker": "https://github.com/Russian-Dev/UTubeToMP/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.0",
)