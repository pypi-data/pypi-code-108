from setuptools import setup, find_packages

setup(
	name="car_drive_ai",
	version="1.0.7",
	description="with this package you can easily setup a car drive ai with pygame on you own raceing track",
	author="Timo Pickelmann",
	author_email="timo.pickelmann.opensource@gmail.com",
	url="https://github.com/timo42453189/car_drive_ai",
	install_requires=["pygame", "neat-python", "numpy", "matplotlib", "wget"],
	packages=find_packages(),
)