from setuptools import setup, find_packages
VERSION = '1.0'
DESCRIPTION = 'Stitcher - mesh builder'
LONG_DESCRIPTION = 'Package that takes in a sequence of plane contours and create a 3D mesh'
setup(
        name="brain-stitcher",
        version=VERSION,
        author="Heitor Gessner",
        author_email="<lab.metabio@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        python_requires='>=3.0, <4',
        install_requires=["numpy"],
        keywords=['mesh', 'Sticher'],
        classifiers= [
            'Development Status :: 4 - Beta',
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: Unix"
        ],
        project_urls={
        'Source':'https://github.com/labmetabio/Stitcher'
    }
)
