from setuptools import setup, find_packages

VERSION = '0.2.2' 
DESCRIPTION = 'A package for modeling behavior in decision from experience experiments'
LONG_DESCRIPTION = 'A package for modeling, estimating and analyzing behavior in decision from experience experiments'

# Setting up
setup(
       # the name must match the folder name 
        name="DEBM", 
        version=VERSION,
        author="Ofir Yakobi",
        author_email="<debm.package@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=["numpy","pandas","scipy","matplotlib","tqdm","openpyxl","xlrd"], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['modeling', 'academic'],
        classifiers= [
            "Development Status :: 4 - Beta",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)