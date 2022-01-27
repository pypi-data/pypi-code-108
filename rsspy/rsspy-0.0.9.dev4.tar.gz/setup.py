import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rsspy",
    version="0.0.9dev4",
    author="GaoangLiu",
    author_email="GaoangLau@gmail.com",
    description="Simple site summary generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GaoangLiu/rss",
    packages=setuptools.find_packages(),
    install_requires=['codefast==0.6.3', 'pydantic',
                      'authc', 'requests', 'redis', 'feedparser'],
    entry_points={'console_scripts': ['rss=rss.schedular:rsspy']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
