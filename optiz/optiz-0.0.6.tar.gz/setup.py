import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="optiz",
    version="0.0.6",
    license="MIT",
    description="Optimization library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Lucas Marandat",
    author_email="lucas.mrdt@gmail.com",
    url="https://github.com/lucasmrdt/optiz",
    keywords=["optimisation"],
    packages=setuptools.find_packages(),
    install_requires=[
        "inquirer==2.9.1",
        "ortools==9.2.9972"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    py_modules=["optiz"],
)
