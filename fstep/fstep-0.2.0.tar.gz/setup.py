import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fstep",
    version="0.2.0",
    license='MIT',
    author='jiang hongyong',
    author_email="hongyong_jiang@hotmail.com",
    description="python mock up pku-minic/first-step",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/allegrofb/fstep",
    project_urls={
    "Bug Tracker": "https://github.com/allegrofb/fstep/issues",
    },
    classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
        'fstep = fstep.app:main',
        ]
    },
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
)
