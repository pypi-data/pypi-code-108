from setuptools import setup

setup(
    name="textanalysis",
    packages=[
        "tfa",
    ],
    install_requires=[
        "wheel",
        "python-levenshtein",
        "ipython",
    ],
    python_requires=">=3.9.0",
    zip_safe=False,
    entry_points={},
    version='0.0.1',
    description="""Ways to plough through texts in search of patterns""",
    author="Dirk Roorda",
    author_email="text.annotation@icloud.com",
    url="https://github.com/annotation/textanalysis",
    keywords=[
        "text",
        "linguistics",
        "graph",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Framework :: Jupyter",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: Filters",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Text Processing :: Markup",
    ],
    long_description="""\
Tools to perform various kinds of analysis of text corpora,
without knowledge of its content or language.
""",
)
