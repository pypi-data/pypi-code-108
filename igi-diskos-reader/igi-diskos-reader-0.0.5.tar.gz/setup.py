import setuptools


setuptools.setup(
    name="igi-diskos-reader",
    version="0.0.5",
    author="IGI",
    author_email="chris.prosser@igiltd.com",
    description="Diskos -> Excel Conversion",
    long_description="Parse Diskos file and generate Excel sheets.",
    long_description_content_type="text/markdown",
    url="https://github.com/IGILtd/data_transformation_scripts/tree/master/import_file_formats/diskos",
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Topic :: Database",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Pre-processors",
        "Topic :: Text Processing",
        "Typing :: Typed",
    ],
    python_requires='>=3.7',
    packages=setuptools.find_packages(exclude=["tests"]),
    install_requires=["openpyxl", "pandas", "igi-file-transformation-contract"]
)
