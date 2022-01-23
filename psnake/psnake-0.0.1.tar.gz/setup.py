import setuptools

setuptools.setup(
    name="psnake",
    version="0.0.1",
    author="Berk Karaal",
    author_email="iletisim.berkkaraal@gmail.com",
    description="Simple snake game with Python",
    long_description="https://github.com/berk-karaal/psnake",
    long_description_content_type="text/markdown",
    url="https://github.com/berk-karaal/psnake",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["psnake"],
    entry_points={"console_scripts": ["psnake=psnake.psnake:run"]},
    python_requires=">=3.8",
)
