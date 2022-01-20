import setuptools
from setuptools import find_namespace_packages

with open("README.md", "r", encoding='utf8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="arcfutil-cvkit",
    version="0.0.2",
    author=".direwolf",
    author_email="kururinmiracle@outlook.com",
    description="OpenCV related plugin for arcfutil",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/feightwywx/arcfutil-cvkit",
    packages=find_namespace_packages('src', include=['arcfutil.*']),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion"
    ],
    python_requires='>=3.8',
    install_requires=[
        'arcfutil>=0.7.0',
        'numpy==1.22.1',
        'opencv-python==4.5.5.62',
    ],
    zip_safe=False,
)
