import setuptools
from setuptools import setup

setup(
    name="asr-library",
    version="0.0.3",
    description="Automatic Speech Recognition inference for wav2vec2 models",
    url="https://github.com/neerajchhimwal/asr",
    author="Neeraj Chhimwal",
    author_email="neerajchhimwal21197@gmail.com",
    license="MIT",

    platforms=["linux", "unix"],
    python_requires=">3.6",
    include_package_data=True,
    install_requires=[
        "packaging", 
        "soundfile",
        "nnresample",
        "webrtcvad"],
    packages=setuptools.find_packages(),
    zip_safe=False,
)
