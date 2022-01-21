from setuptools import setup, find_packages

VERSION = '0.0.52' 
DESCRIPTION = 'A simple styling package for making console programmes great again.'
LONG_DESCRIPTION = open('README.md','r',encoding='utf-8').read()

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="colorain", 
        version=VERSION,
        author="Susmit Islam",
        author_email="<susmitislam31@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type='text/markdown',
        url = 'https://github.com/susmit31/colorain',
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['colour','color','terminal']
)