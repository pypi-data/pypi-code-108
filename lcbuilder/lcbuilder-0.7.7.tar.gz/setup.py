import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
version = "0.7.7"
setuptools.setup(
    name="lcbuilder", # Replace with your own username
    version=version,
    author="M. Dévora-Pajares",
    author_email="mdevorapajares@protonmail.com",
    description="Easy light curve builder from multiple sources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PlanetHunders/lcbuilder",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['numpy==1.20.1; python_version>="3.7"',
                        'numpy==1.19; python_version<"3.7"',
                        'astropy==4.3.post1; python_version>="3.7"',
                        'astropy==4.1; python_version<"3.7"',
                        'pandas==1.3.1; python_version>="3.7"',
                        'pandas==1.1.5; python_version<"3.7"',
                        "lightkurve==2.0.9",
                        "photutils==1.0.2",
                        "scipy==1.5.4",
                        "tess-point==0.6.1",
                        'torch==1.9.0',
                        "foldedleastsquares==1.0.31",
                        "wotan==1.9"
    ]
)