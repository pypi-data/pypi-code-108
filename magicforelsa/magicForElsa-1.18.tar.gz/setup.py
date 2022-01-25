from distutils.core import setup

setup(
    name="magicForElsa",
    packages=["Magic"],
    version="1.18",
    license="GPLv3+",
    description="A package for the personal assistant Elsa",
    author="George Rahul",
    author_email="georgerahul24@gmail.com",
    url="https://github.com/georgerahul24/MagicForElsa",
    keywords=["program", "automate", "task", "magic"],
    install_requires=["pyttsx3", "win10toast", "PyQt5", "task1", "talk1"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
           "Programming Language :: Python :: 3.9",
    ],
)
