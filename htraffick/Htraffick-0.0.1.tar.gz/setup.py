import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Htraffick",
    version="0.0.1",
    author="sana okubo",
    author_email="s1922004@stu.musashino-u.ac.jp",
    description="A package for scoring policies of Indian Trafficking Law",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sachan-37/Htraffick",
    project_urls={
        "Bug Tracker": "https://github.com/sachan-37/Htraffick",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    py_modules=['Htraffick'],
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.9",
    entry_points = {
        'console_scripts': [
            'Htraffick = Htraffick:main'
        ]
    },
)
