import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lostlifevalue",
    version="0.0.5",
    author="Kiuchi_424",
    author_email="s1922059@stu.musashino-u.ac.jp",
    description="A package to find out the true extent of the damage caused by Covid-19 to the country.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Kiuchi424/Lostlifevalue",
    project_urls={
        "Lostlifevalue": "https://github.com/Kiuchi424/Lostlifevalue",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    py_modules=['lostlifevalue'],
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    entry_points = {
        'console_scripts': [
            'lostlifevalue = lostlifevalue:main'
        ]
    },
)
