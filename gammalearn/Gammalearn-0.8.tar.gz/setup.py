import setuptools
from pathlib import Path


this_directory = Path(__file__).parent
long_description = Path(__file__).parent.joinpath("README.md").read_text()

setuptools.setup(
    name="Gammalearn",
    author="M. Jacquemont, T. Vuillaume",
    author_email="jacquemont@lapp.in2p3.fr",
    description="A framework to easily train deep learning model on Imaging Atmospheric Cherenkov Telescopes data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.lapp.in2p3.fr/GammaLearn/GammaLearn",
    install_requires=[
        "torch>=1.7",
        "tensorboard",
        "torchvision",
        "numpy",
        "matplotlib",
        "tables",
        "pytorch-lightning>=1.4",
        "indexedconv>=1.3",
        "ctapipe>=0.10",
        "ctaplot",
        "dl1_data_handler~=0.10",
        "lstchain>=0.7",
    ],
    setup_requires=["setuptools_scm"],
    tests_require=['pytest'
                   'coverage',
                   ],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license='MIT',
    entry_points={
        'console_scripts': {
            'gammalearn = gammalearn.experiment_runner:main'
        }
    },
    include_package_data=True,
    package_data={'': ['data/camera_parameters.h5']},
    use_scm_version={
        "write_to": Path(__file__).parent.joinpath("gammalearn/_version.py"),
        "write_to_template": "__version__ = '{version}'",
    },
)
