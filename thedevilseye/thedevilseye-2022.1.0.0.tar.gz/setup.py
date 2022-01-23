import setuptools

with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

setuptools.setup(
    name="thedevilseye",
    version="2022.1.0.0",
    author="Richard Mwewa",
    author_email="richardmwewa@duck.com",
    packages=["eye"],
    description="Darkweb OSINT tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rly0nheart/thedevilseye",
    license="GNU General Public License v3 (GPLv3)",
    install_requires=["requests==2.26.0","beautifulsoup4==4.10.0"],
    classifiers=[
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',  
        'Operating System :: POSIX :: Linux',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
    ],
    entry_points={
        "console_scripts": [
            "eye=eye.main:thedevilseye",
        ]
    },
)
