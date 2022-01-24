import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="botshop",
    version="0.0.35",
    author="Freddy Snijder",
    author_email="botshop@visionscapers.com",
    description="Framework for chatbot model inference, optimized for neural conversation models.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nuhame/botshop",
    packages=setuptools.find_packages(),
    install_requires=[
        'numpy',
        'visionscaper-pybase'
    ],
    dependency_links=[],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)