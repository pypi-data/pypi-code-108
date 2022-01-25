import setuptools

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="new_timer",
    version="0.0.10",
    author="Overcomer",
    author_email="michael31703@gmail.com",
    description="Program timer.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Michael07220823/new_timer.git",
    keywords="timer",
    python_requires='>=3',
    install_requires=['numpy'],
    license="MIT License",
    packages=setuptools.find_packages(include=["new_timer", "new_timer.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

)