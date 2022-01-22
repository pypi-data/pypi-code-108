import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="FairDynamicRec",
    version="0.0.24",
	scripts=['fair_dynamic_rec/__main__.py'] ,
    author="Masoud Mansoury",
    author_email="masoodmansoury@gmail.com",
    description=
    "The FairDynamicRec project aims to facilitate recommender system experiments in dynamic setting where system is operating over time.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/that-recsys-lab/librec-auto",
    packages=setuptools.find_packages(),
	include_package_data=True,
	install_requires=['matplotlib',
                      'pandas',
                      'numpy',
                      'progressbar',
                      'lxml',
                      'scipy',
                      'tqdm'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
