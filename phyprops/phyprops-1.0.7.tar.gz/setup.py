import setuptools

setuptools.setup(
    name="phyprops",
    version="1.0.7",
    author="Cheng Maohua",
    author_email="cmh@seu.edu.cn",
    packages=['phyprops'],
    description="The simple interface of CoolProp",
    long_description=open("./phyprops/README.rst", "r", encoding="utf8").read(),
    platforms=["Windows", "Linux"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
