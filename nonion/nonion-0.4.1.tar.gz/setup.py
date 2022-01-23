import setuptools

with open("README.md") as buffer:
    long_description = buffer.read()

setuptools.setup(
    name="nonion",
    version="0.4.1",
    author="Illia Shkroba",
    author_email="is@pjwstk.edu.pl",
    description="Python Functional Programming for Humans.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/shkroba/nonion",
    packages=setuptools.find_packages(),
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Typing :: Typed",
    ],
    python_requires=">=3.6",
)
