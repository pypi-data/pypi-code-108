import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="UsefulTools",
    version="1.1.3",
    author="Mojave2021",
    author_email="HTTcode2020@126.com",
    description="A small useful package by Mojave2021",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NTFS2020/UsefulTool",
    packages=setuptools.find_packages(),
    python_requires='>=3',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],install_setup_requires=[
        'pyecharts<=0.5.11,>=0.5.11','matplotlib','pillow','jieba','wordcloud'
    ]
)
