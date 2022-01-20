from setuptools import find_packages, setup
from xes import AIspeak

if __name__ == '__main__':
    import sys

    sys.argv += ["sdist"]

setup(
    name="tkinter-stat",
    version=str(float(1)),
    description="好用的tkinter状态栏/A useful tkinter statusbar plugin",
    author="Ruoyu Wang", author_email='fuck@yopmail.com', long_description="tkinter没有状态栏？此扩展可以给他加一个！/" +
                                                                           AIspeak.translate("tkinter"
                                                                                             "没有状态栏？"
                                                                                             "此扩展可以给他加一个！"),
    packages=find_packages('.')
    # , requires=["xes-lib"]
)
