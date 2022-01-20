from setuptools import setup, find_packages

with open('requirements.txt') as f:
	requirements = f.readlines()

long_description = "A set of tools to aid in creating US legislative district maps."

setup(
		name ="redistricting-tools",
		version ="0.0.5",
		author ="Mike Yin",
		author_email ="mikeyin@mikeyin.org",
		url ="https://github.com/yincrash/redistricting-tools",
		description ="Tools for redistricting.",
		long_description = long_description,
		long_description_content_type ="text/markdown",
		license ="MIT",
		packages = find_packages(),
		entry_points ={
			"console_scripts": [
				"combine-districts = redistrictingtools.combine_districts:main",
				"nest-districts = redistrictingtools.nest_districts:main",
				"remove-districts = redistrictingtools.remove_districts:main"
			]
		},
		classifiers =(
			"Programming Language :: Python :: 3",
			"License :: OSI Approved :: MIT License",
			"Operating System :: OS Independent",
		),
		keywords ="redistricting tools",
		install_requires = requirements,
		zip_safe = False
)
