from setuptools import setup, find_packages

VERSION = '1.0.5.1'
DESCRIPTION = 'Deploy machine learning models to Docker'
LONG_DESCRIPTION = 'Python package for packaging and deploying machine learning models as invokable endpoints in Docker containers.'

# Setting up
setup(
       # the name must match the folder name 'ml_unleash'
        name="ml_unleash",
        version=VERSION,
        author="Dwayne Thomson",
        author_email="dwaynethomson14@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=["Flask"], # add any additional packages that
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'docker', 'mlops'],
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: Microsoft :: Windows",
        ]
)