import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="uscalendar",
    version="0.0.1",
    author="Matthew McElhaney",
    author_email="matt@lamplightlab.com",
    description="Package that contains modules for US Federal Holidays and US Market Opens",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mmcelhan/us_calendar_source",
    project_urls={
        "blog post": "https://lamplightlab.com/?p=61",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
