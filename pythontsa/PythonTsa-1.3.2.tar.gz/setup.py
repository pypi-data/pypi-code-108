import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PythonTsa",
    version="1.3.2",
    author="Changquan Huang",
    author_email="cqhuang@xmu.edu.cn",
    description="Package for Applied Time Series Analysis and Forecasting with Python, Springer 2022",
    long_description=long_description,
    long_description_content_type="text/markdown",
   
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    package_data={'PythonTsa': ['Ptsadata/*.csv', 'Ptsadata/*.txt', 'Ptsadata/*.xlsx',  'Ptsadata/*.dat']}
)