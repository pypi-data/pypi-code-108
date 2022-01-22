import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="algotradingPythonSalem",
    version="0.0.2",
    author="AlgoTrading",
    author_email="AlgoTrading@gmail.com",
    description="Find and tag Git commits based on version numbers in commit messages.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://initialcommit.com/projects/algotradingPythonSalem.com",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'gitpython'
    ],
    keywords='git tag git-tagup tagup tag-up version autotag auto-tag commit message',
    project_urls={
        'Homepage': 'https://initialcommit.com/projects/algotradingPythonSalem.com',
    },
    entry_points={
        'console_scripts': [
            'git-tagup=main:app',
            'gtu=src.main:app',
        ],
    },
)