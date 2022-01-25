import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="G1Race",
    version="0.0.7",
    author="Kiuchi_424",
    author_email="s1922059@stu.musashino-u.ac.jp",
    description="A package designed to help you understand the trends of nations that host high-level G1 races.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Kiuchi424/G1Race",
    project_urls={
        "G1Race": "https://github.com/ytakefuji/score-covid-19-policy",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    py_modules=['G1Race'],
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    entry_points = {
        'console_scripts': [
            'G1Race = G1Race:main'
        ]
    },
)
