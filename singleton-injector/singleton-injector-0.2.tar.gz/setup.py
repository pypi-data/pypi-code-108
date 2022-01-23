from distutils.core import setup

README_FILE = open("README.md", 'r').read()

setup(
    name="singleton-injector",
    packages=["singleton_injector"],
    version="0.2",
    license="MIT",
    description="Simple library to unify singleton and injection with a decorator",
    long_description=README_FILE,
    long_description_content_type='text/markdown',
    author="Santiago Melo Medina",
    author_email="smelomedina05@gmail.com",
    url="https://github.com/santiagoMeloMedina/singleton-injector",
    download_url="https://github.com/santiagoMeloMedina/singleton-injector/archive/refs/tags/0.1.tar.gz",
    keywords=[
        "Injection",
        "Singleton",
        "Simple",
    ],
    install_requires=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
    ],
)
