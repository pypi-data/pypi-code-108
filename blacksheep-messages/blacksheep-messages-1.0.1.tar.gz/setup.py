from setuptools import setup


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="blacksheep-messages",
    version="1.0.1",
    description="Extension for BlackSheep that similiar with flask flashes messages",
    long_description=readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/riordanz/BlackSheep-Messages",
    author="Riordan Ganezo",
    author_email="black.ganezo@gmail.com",
    keywords="blacksheep flask flashes message messages",
    license="MIT",
    packages=["blacksheep_messages"],
    install_requires=["blacksheep"],
    include_package_data=True,
    zip_safe=False,
)