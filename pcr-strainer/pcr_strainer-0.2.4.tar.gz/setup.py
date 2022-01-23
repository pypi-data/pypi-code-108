import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pcr_strainer",
    version="0.2.4",
    author="Kevin Kuchinski",
    author_email="kevin.kuchinski@bccdc.ca",
    description="A tool for assessing the inclusivity of PCR oligos for diagnostic assays and amplicon sequencing schemes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KevinKuchinski/PCR_strainer",
    project_urls={
        "Bug Tracker": "https://github.com/KevinKuchinski/PCR_strainer/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
    entry_points={
    'console_scripts': [
        'pcr_strainer = pcr_strainer.pcr_strainer_v_0_2_4:main',
    ],
    }
)
