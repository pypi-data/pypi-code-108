import setuptools

# Setting up
setuptools.setup(
        name="micnet", 
        version="0.0.153",
        author="Natalia Favila, David Madrigal-Trejo, Daniel Legorreta",
        author_email="natalia.favila.v@gmail.com",
        description="Toolbox for the visualization and analysis of microbial datasets",
        long_description=open('README.md').read(),
        long_description_content_type='text/markdown',
	install_requires=['pandas',
			  'numba == 0.54.1',
		          'umap-learn == 0.5.1',
                          'webcolors',
                          'matplotlib',
                          'bokeh == 2.3.0',
			  'dask',
                          'h5py',
			  'scipy==1.7.1',
		          'python-louvain',
			  'networkx == 2.6.3',
			  'scikit-learn == 1.0.1',
		  	  'numpy == 1.19.0',
	],
        classifiers= [
            "Intended Audience :: Education",
            "Programming Language :: Python :: 3",
        ],
	include_package_data=True,
	packages=setuptools.find_packages(),
	package_data={'': ['data/*.txt']},
)