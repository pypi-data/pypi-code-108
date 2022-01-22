import pathlib
import setuptools

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text(encoding="utf-8")
CVIOLET = "\33[35m"
CBOLD = "\033[1m"
print(CVIOLET + CBOLD + "JOIN THE SUPPORT SERVER FOR HELP!!")
print(CVIOLET + CBOLD + "https://discord.gg/fcZBB2v")

setuptools.setup(
    name="connecty",
    version="2.0.1",
    description="Discord.py bot to connect channels across servers",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://discord.gg/fcZBB2v",
    author="Znunu",
    packages=["connecty"],
    include_package_data=True,
    install_requires=["discord.py >= 1.7.0", "colorama"], # "pystray", "pillow"
    entry_points={
        "console_scripts": [
            "connecty=connecty.__main__:start",
        ]
    }
)





