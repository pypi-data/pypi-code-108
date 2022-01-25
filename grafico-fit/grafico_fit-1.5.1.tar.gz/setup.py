import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="grafico_fit",
    version="1.5.1",
    author="Luca Cremonesi",
    author_email="luca.cremonesi@sns.it",
    description="Package per generare grafici di fit partendo da dati in fogli Excel",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/cremo_sns/json_fit.git",
    project_urls={
        "Bug Tracker": "https://gitlab.com/cremo_sns/json_fit/-/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"grafico_fit": "src/grafico_fit"},
    packages=['grafico_fit'],
    python_requires=">=3.6",
    install_requires=[
        "numpy",
        "matplotlib",
        "scipy",
        "pandas",
        "openpyxl",
        "pint"
    ]
)