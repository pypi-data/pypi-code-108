from distutils.core import setup

setup(name='ct_data',
      version='0.1.1',
      packages=['ct_data'],
      license='MIT',
      description = 'finance management tool',
      author = 'Dan',
      author_email = 'daniel.js.campbell@gmail.com',
      url = 'https://github.com/dn757657/ct_data2.git',
      download_url = 'https://github.com/dn757657/ct_data/archive/refs/tags/0.1.1.tar.gz',
      keywords = ['Management', 'finance', 'automation'],
      install_requires=[
            'pandas',
            'tabulate',
            'web3',
            'python-dateutil',
            'textblob',
            'colorama',
            'docopt',
            'qtrade',
            'pandas_datareader',
            'textblob',
      ],
      classifiers=[
            'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
            'Intended Audience :: Developers',      # Define that your audience are developers
            'Topic :: Software Development :: Build Tools',
            'License :: OSI Approved :: MIT License',   # Again, pick a license
            'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
      ],
      )
