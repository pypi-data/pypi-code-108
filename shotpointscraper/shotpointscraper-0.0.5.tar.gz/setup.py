import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="shotpointscraper",
    version="0.0.5",
    author="Daiki Azuma",
    author_email="s1922052@stu.musashino-u.ac.jp",
    description="A package for scrap shot data from Understats",
    project_urls={
        "shot_point_scraper": "https://github.com/DaikiAzuma/shot_point_scraper",
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    py_modules=['shotpointscraper'],
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.9",
    entry_points = {
        'console_scripts': [
            'shotpointscraper = shotpointscraper:main'
        ]
    },
)