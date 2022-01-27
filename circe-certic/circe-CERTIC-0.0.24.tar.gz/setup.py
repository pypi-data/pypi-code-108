import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="circe-CERTIC",
    version="0.0.24",
    author="Mickaël Desfrênes",
    author_email="mickael.desfrenes@unicaen.fr",
    description="Circe server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.unicaen.fr/fnso/i-fair-ir/circe-server",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "requests",
        "argh",
        "sanic",
        "huey",
        "asyncio",
        "itsdangerous",
        "aiofiles",
        "markdown2",
        "python-json-logger",
        "python-dotenv",
    ],
    python_requires=">=3.6",
    include_package_data=True,
    entry_points={
        "console_scripts": ["circe=circe.__main__:run_cli"],
    },
)
