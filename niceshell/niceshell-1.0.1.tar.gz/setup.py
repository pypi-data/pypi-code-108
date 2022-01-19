import setuptools

with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

setuptools.setup(
    name="niceshell",
    version="1.0.1",
    author="Andrew Voynov",
    author_email="andrewvoynov.b@gmail.com",
    description="Integration of shell and basic GNU core unilities for better coding.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/Andrew15-5/niceshell",
    download_url="https://github.com/Andrew15-5/niceshell/releases/download/v1.0.1/niceshell-1.0.1-py3-none-any.whl",
    packages=["niceshell", "niceshell/tests"],
    package_data={
        "niceshell": ['*']
    },
    python_requires=">=3.6",
    extras_require={
        "pytest": "pytest"
    },
    install_requires=["regex"],
    keywords=["nice", "shell", "GNU", "coreutils", "sh"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Topic :: System :: System Shells",
    ]
)
