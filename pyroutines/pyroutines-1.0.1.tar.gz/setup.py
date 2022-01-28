import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name='pyroutines',
    version='1.0.1',
    scripts=['routines.py'],
    author="Lucas Sousa",
    author_email="lucasads18@outlook.com",
    description="This package contains helper methods to perform certain routine activities"
                "in the act of image processing with pyautogui",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lucas-fsousa/pyroutines",
    packages=setuptools.find_packages(),
    classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
    ],
)
