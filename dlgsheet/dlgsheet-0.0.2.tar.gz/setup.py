import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dlgsheet",
    version="0.0.2",
    author="Luighi Viton-Zorrilla",
    author_email="luighiavz@gmail.com",
    description="Script to Google Sheets to JSON files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LuighiV/download-gsheet",
    project_urls={
        "Bug Tracker": "https://github.com/openpolitica/download-gsheet/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License ",
        "Operating System :: POSIX :: Linux ",
    ],
    packages=["dlgsheet"],
    python_requires=">=3.6",
    install_requires=[
        'colorlog',
        'google_api_python_client',
        'python-dotenv'],
    entry_points={
        'console_scripts': [
            'dlgsheet=dlgsheet.cli:main',
        ],
    },
)
