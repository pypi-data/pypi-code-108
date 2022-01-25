from distutils.core import setup

setup(name='sql_docopt_queries',
      version='0.0.4',
      packages=['sql_queries'],
      license='MIT',
      description='sqlite interface',
      author='Dan',
      author_email='daniel.js.campbell@gmail.com',
      url='https://github.com/dn757657/sql-queries.git',
      download_url='https://github.com/dn757657/sql-queries/archive/refs/tags/0.0.4.tar.gz',
      keywords=['docopt', 'sqlite', 'ct-finance'],
      install_requires=[
            'pathlib~=1.0.1',
            'pandas~=1.3.5'
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
