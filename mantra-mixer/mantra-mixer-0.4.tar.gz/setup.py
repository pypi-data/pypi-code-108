from distutils.core import setup

install_requires = """
numpy==1.21.5
librosa==0.8.1
soundfile==0.10.3.post1
sounddevice==0.4.4
ffmpy==0.3.0
""".split()

setup(
    name="mantra-mixer",
    packages=["mantra_mixer"],
    version="0.4",
    license="MIT",
    description="Audio mixing library simplified.",
    author="Philippe Mathew",
    author_email="philmattdev@gmail.com",
    url="https://github.com/bossauh/mantra-mixer",
    download_url="https://github.com/bossauh/mantra-mixer/archive/refs/tags/v_04.tar.gz",
    keywords=["audio", "mixing", "mixer"],
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7"
    ]
)
