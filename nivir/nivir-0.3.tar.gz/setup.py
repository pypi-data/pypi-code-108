from setuptools import setup

readme = open("./README.md", "r")

setup(
    name = "nivir",
    packages=['nivir'],
    version='0.3',
    description="Nivir is a simple game engine",
    long_description=readme.read(),
    long_description_content_type='text/markdown',
    author = "Rinka",
    author_email="labatanightcore@gmail.com",
    license='MIT',
    include_package_data=True
)