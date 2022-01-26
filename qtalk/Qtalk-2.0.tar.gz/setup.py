from setuptools import setup, find_packages

VERSION = '2.0' 
DESCRIPTION = 'Mattermost integration package'
LONG_DESCRIPTION = 'Use these functions to send alerts to Mattermost using webhooks'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="Qtalk", 
        version=VERSION,
        author="Lucia Kina",
        author_email="<lkina@quanticotrends.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'mattermost', 'alerts', 'qtalk'],
        classifiers= [
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)