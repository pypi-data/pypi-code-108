import setuptools

with open("README.md") as buffer:
    long_description = buffer.read()

setuptools.setup(
    name="dskit",
    version="0.1.1",
    author="Illia Shkroba",
    author_email="is@pjwstk.edu.pl",
    description="Python Data Science Kit for Humans.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/shkroba/dskit",
    packages=setuptools.find_packages(),
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Typing :: Typed"
    ],
    python_requires='>=3.6',
    install_requires=(
      "nonion>=0.4.1",
      "numpy>=1.16",
      "pandas>=1.1.0",
      "scikit-learn>=0.24.2"
    )
)
