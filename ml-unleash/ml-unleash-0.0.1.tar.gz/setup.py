from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'Deploy machine learning models to Docker'
LONG_DESCRIPTION = 'Python package for packaging and deploying machine learing models as callable endpoints in Docker containers.'

# Setting up
setup(
       # the name must match the folder name 'ml-unleash'
        name="ml-unleash",
        version=VERSION,
        author="Dwayne Thomson",
        author_email="dwaynethomson14@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=["Flask"], # add any additional packages that
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'docker'],
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: Microsoft :: Windows",
        ]
)