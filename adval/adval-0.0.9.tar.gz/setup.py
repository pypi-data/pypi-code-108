from setuptools import setup

# reading long description from file
with open('DESCRIPTION.txt') as file:
    Long_description = file.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# some more details
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    ]

# calling the setup function 
setup(name='adval',
      version='0.0.9',
      description='Adversarial validation for train-test datasets',
      long_description=Long_description,
      url='https://github.com/alikula314/adval',
      author='Muhammet Ali Kula',
      author_email='alikula3.14@gmail.com',
      license='MIT',
      packages=['validation'],
      classifiers=CLASSIFIERS,
      install_requires=requirements,
      keywords='adversarial validation train-test-split data-sceince machine-learning'
      )
