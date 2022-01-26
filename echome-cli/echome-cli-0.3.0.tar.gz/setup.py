import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="echome-cli",
    version="0.3.0",
    author="Marcus Gutierrez",
    author_email="markg90@gmail.com",
    description="EcHome CLI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mgtrrz/echome-cli",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'echome-sdk<=1.0.0',
        'requests>=2.24',
        'tabulate>=0.8.7'
    ],
    entry_points = {
        'console_scripts': [
            'echome=cli:ecHomeCli'
        ]
    },
)
