from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='nehushtan',
    version='0.4.27',
    packages=find_packages(),
    url='https://sinri.github.io/nehushtan/',
    license='MIT',
    author='Sinri Edogawa',
    author_email='e.joshua.s.e@gmail.com',
    description='A toolkit for projects in Python',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.8',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'psutil~=5.8.0',
    ]
)
