import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ytspace",
    version="14.81",
    author="Yugam Sehgal",
    author_email="yugamsehgal4254@gmail.com",
    url="https://github.com/Yugam4254/YT-Space",
    description="Python-MySQL project to download YouTube videos and music from terminal using pytube.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["ytspace", "ytspace/pytube"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    py_modules=["ytspace", "packages", "run", "funcs", "yt_funcs", "sql_funcs"],
    #package_dir={'':''},
    install_requires=["pytube", "mysql-connector"]
)
