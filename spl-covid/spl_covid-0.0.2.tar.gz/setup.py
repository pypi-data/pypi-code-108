import setuptools

setuptools.setup(
    name="spl_covid",
    version="0.0.2",
    author="Colin Simon-Fellowes",
    author_email="colin.tsf@gmail.com",
    description="Covid Statistics mini-widget for the amusement of Robert Remez",

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=['tableauscraper', 'xlsxwriter', 'pandas'],
    python_requires=">=3.6",
)
