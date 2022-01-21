import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="DatabaseDataGenerator",
    version="1.6.0",
    author="PhatDave",
    author_email="kosmodiskclassic0@gmail.com",
    description="Generates any amount of data for supported databases (currently postgresql and sqlite)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PhatDave/DatabaseDataGenerator",
    project_urls={
        "Bug Tracker": "https://github.com/PhatDave/DatabaseDataGenerator/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        "Faker>=11.3.0",
        "py-postgresql>=1.2.2",
        "python-dateutil>=2.8.2",
        "six>=1.16.0",
        "text-unidecode>=1.3",
        "faker-vehicle>=0.2.0",
        "tqdm>=4.62.3",
    ]
)