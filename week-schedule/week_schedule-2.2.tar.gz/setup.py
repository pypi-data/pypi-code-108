from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
	long_description = fh.read()

setup(
	name="week_schedule",
	version="2.2",
	author="Jacob Hilbert",
	author_email="jacob.hilbert.tree@gmail.com",
	description="Create schedule images of your weekly classes",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/JacobHilbert/week_schedule",
	packages=["week_schedule"],
	install_requires=[
		"numpy",
		"matplotlib"
	],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	license="LICENSE",
	zip_safe=True
)
