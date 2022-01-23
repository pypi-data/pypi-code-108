import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="EvtPlugins", 
    version="0.99.30",
    author="Eise Hoekstra and Mark Span (primary developer)",
    author_email="m.m.span@rug.nl",
    description="Plugin Package to communicate with RUG developed hardware",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/markspan/EvtPlugins",
    packages=setuptools.find_packages(),
	install_requires=[
          'pyEVT'
      ],
	classifiers=[
		'Intended Audience :: Science/Research',
		'Topic :: Scientific/Engineering',
		'Environment :: MacOS X',
		'Environment :: Win32 (MS Windows)',
		'Environment :: X11 Applications',
		'License :: OSI Approved :: Apache Software License',
		'Programming Language :: Python :: 3',
	],
    python_requires='>=3.6',
	
	data_files=[
		# First target folder.
		('share/opensesame_plugins/VAS',
		# Then a list of files that are copied into the target folder. Make sure
		# that these files are also included by MANIFEST.in!
		[
			'opensesame_plugins/VAS/VAS.md',
			'opensesame_plugins/VAS/VAS.png',
			'opensesame_plugins/VAS/VAS_large.png',
			'opensesame_plugins/VAS/VAS.py',
			'opensesame_plugins/VAS/info.yaml',
			]
		),
		# Corresponding Demo
		('share/opensesame_extensions/example_experiments/examples/VAS',
		['opensesame_plugins/VAS/experiment.osexp',
			]
		),
		# Second target folder.
		('share/opensesame_plugins/EVTxx',
		# Then a list of files that are copied into the target folder. Make sure
		# that these files are also included by MANIFEST.in!
		[
			'opensesame_plugins/EVTxx/EVTxx.md',
			'opensesame_plugins/EVTxx/EVTxx.png',
			'opensesame_plugins/EVTxx/EVTxx_large.png',
			'opensesame_plugins/EVTxx/EVTxx.py',
			'opensesame_plugins/EVTxx/info.yaml',
			]
		),
		# Third target folder.
		('share/opensesame_plugins/ResponseBox',
		# Then a list of files that are copied into the target folder. Make sure
		# that these files are also included by MANIFEST.in!
		[
			'opensesame_plugins/ResponseBox/ResponseBox.md',
			'opensesame_plugins/ResponseBox/ResponseBox.png',
			'opensesame_plugins/ResponseBox/ResponseBox_large.png',
			'opensesame_plugins/ResponseBox/ResponseBox.py',
			'opensesame_plugins/ResponseBox/info.yaml',
			]
		),
		# Fourth target folder.
		('share/opensesame_plugins/RGB_Led_Control',
		# Then a list of files that are copied into the target folder. Make sure
		# that these files are also included by MANIFEST.in!
		[
			'opensesame_plugins/RGB_Led_Control/RGB_Led_Control.png',
			'opensesame_plugins/RGB_Led_Control/RGB_Led_Control_large.png',
			'opensesame_plugins/RGB_Led_Control/RGB_Led_Control.py',
			'opensesame_plugins/RGB_Led_Control/info.yaml',
			]
		),
				# Fourth target folder.
		('share/opensesame_plugins/Shocker',
		# Then a list of files that are copied into the target folder. Make sure
		# that these files are also included by MANIFEST.in!
		[
			'opensesame_plugins/Shocker/Shocker.png',
			'opensesame_plugins/Shocker/Shocker_large.png',
			'opensesame_plugins/Shocker/Shocker.py',
			'opensesame_plugins/Shocker/info.yaml',
			]
		)
	],)
	
