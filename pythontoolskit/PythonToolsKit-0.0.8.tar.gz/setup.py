import platform
import PythonToolsKit as package
from subprocess import check_call, DEVNULL
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install


class PostDevelopScript(develop):
    def run(self):

        if platform.system() == "Windows":
            check_call(
                [
                    r"C:\WINDOWS\system32\reg.exe",
                    "add",
                    r"HKEY_CURRENT_USER\Console",
                    "/v",
                    "VirtualTerminalLevel",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    "0x00000001",
                    "/f",
                ],
                stdout=DEVNULL,
                stderr=DEVNULL,
            )  # Active colors in console

        develop.run(self)


class PostInstallScript(install):
    def run(self):

        if platform.system() == "Windows":
            check_call(
                [
                    r"C:\WINDOWS\system32\reg.exe",
                    "add",
                    r"HKEY_CURRENT_USER\Console",
                    "/v",
                    "VirtualTerminalLevel",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    "0x00000001",
                    "/f",
                ],
                stdout=DEVNULL,
                stderr=DEVNULL,
            )  # Active colors in console

        install.run(self)


setup(
    name=package.__name__,
    version=package.__version__,
    packages=find_packages(include=[package.__name__]),
    install_requires=[],
    author=package.__author__,
    author_email=package.__author_email__,
    maintainer=package.__maintainer__,
    maintainer_email=package.__maintainer_email__,
    description=package.__description__,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url=package.__url__,
    project_urls={
        "Documentation Timeout": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/Timeout.html",
        "Documentation Terminal": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/Terminal.html",
        "Documentation StringF": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/StringF.html",
        "Documentation PrintF": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/PrintF.html",
        "Documentation Process": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/Process.html",
        "Documentation Logs": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/Logs.html",
        "Documentation GetPass": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/GetPass.html",
        "Documentation Encodings": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/Encodings.html",
        "Documentation DictObject": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/DictObject.html",
        "Documentation Report": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/Report.html",
        "Documentation urlopen": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/urlopen.html",
        "Documentation Dict": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/Dict.html",
        "Documentation Arguments": "https://mauricelambert.github.io/info/python/code/PythonToolsKit/Arguments.html",
    },
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.9",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.6",
    keywords=[
        "Timeout",
        "Terminal",
        "Colors",
        "Formatting",
        "Print",
        "Object",
        "Process",
        "CSV",
        "Logs",
        "Getpass",
        "Password",
        "Ask",
        "*",
        "Encodings",
        "Report",
        "Markdown",
        "HTML",
        "JSON",
        "Arguments",
        "Input",
        "Output",
    ],
    platforms=["Windows", "Linux", "MacOS"],
    license=package.__license__,
    cmdclass={
        "develop": PostDevelopScript,
        "install": PostInstallScript,
    },
)