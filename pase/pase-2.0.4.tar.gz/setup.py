import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "readme.md").read_text()

# This call to setup() does all the work
setup(
    name="pase",
    version="2.0.4",
    description="Python Audio Spectrogram Explorer: a GUI to visualize audio files as spectrograms, log annotations and extract time-frequency shapes",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/sebastianmenze/Python-Audio-Spectrogram-Explorer",
    author="Sebastian Menze",
    author_email="sebastian.menze@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["pase"],
    include_package_data=True,
    install_requires=["soundfile","simpleaudio","scikit-image"])
    # entry_points={
    #     "console_scripts": [
    #         "pase=pase.__main__:main",
        # ]
    # },
# )
