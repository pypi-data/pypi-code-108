import setuptools
import smltk

setuptools.setup(
    name="smltk",
    version=smltk.__version__,
    author=smltk.__author__,
    author_email="alessandra.bilardi@gmail.com",
    description="Simple Machine Learning Tool Kit package",
    long_description=open('README.rst').read(),
    long_description_content_type="text/x-rst",
    url="https://smltk.readthedocs.io/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    project_urls={
        "Source":"https://github.com/bilardi/smltk",
        "Bug Reports":"https://github.com/bilardi/smltk/issues",
        "Funding":"https://donate.pypi.org",
    },
)
