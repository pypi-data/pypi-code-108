from setuptools import setup, find_packages

setup(name='peewee_extension',
      version='0.1.9',
      description='Extension peewee functionality',
      classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords='peewee',
      url='https://github.com/GhostNA/peewee_extension',
      author='Specter NA',
      author_email='naspecter@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'peewee',
      ],
      include_package_data=True,
      zip_safe=False)
