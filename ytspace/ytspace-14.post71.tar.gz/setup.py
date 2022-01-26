import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ytspace",                     # This is the name of the package
    version="14-71",                        # The initial release version
    author="Yugam Sehgal",
    author_email="yugamsehgal4254@gmail.com",
    url="https://github.com/Yugam4254/YT-Space",                   # Full name of the author
    description="Python-MySQL project to download YouTube videos and music from terminal using pytube.",
    long_description=long_description,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    packages=["ytspace", "ytspace/pytube"],    # List of all python modules to be installed
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.6',                # Minimum version requirement of the package
    py_modules=["ytspace", "packages", "run", "funcs", "yt_funcs", "sql_funcs"],             # Name of the python package
    #package_dir={'':''},     # Directory of the source code of the package
    install_requires=["pytube", "mysql-connector"]                     # Install other dependencies if any
)
