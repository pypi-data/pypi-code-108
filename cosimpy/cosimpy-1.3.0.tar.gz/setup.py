import setuptools

with open(".//docs//README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    
setuptools.setup(name="cosimpy", version="1.3.0", licence="MIT", url='https://umbertozanovello.github.io/CoSimPy/', packages=setuptools.find_packages(), author="Umberto Zanovello", description="Python electromagnetic co-simulation library", long_description=long_description, long_description_content_type="text/markdown", classifiers=["Programming Language :: Python :: 3", "License :: OSI Approved :: MIT License", "Operating System :: OS Independent",], python_requires='>=3.5',)
