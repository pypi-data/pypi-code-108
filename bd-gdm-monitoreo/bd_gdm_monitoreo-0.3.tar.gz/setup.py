from distutils.core import setup

setup(
  name = 'bd_gdm_monitoreo',
  packages = ['bd_gdm_monitoreo'],
  version = '0.3',
  license='MIT',
  description = 'Libreria para monitorear los modelos de forma local',
  author = 'Juan Felipe Romero - GDM',
  author_email = 'juan.romero@davivienda.com',
  url = 'https://github.com/joelbarmettlerUZH/Scrapeasy',
  download_url = 'https://github.com/joelbarmettlerUZH/Scrapeasy/archive/pypi-0_1_3.tar.gz',
  keywords = ['gdm'],
  install_requires=[
          'firebase_admin'
      ],
  classifiers=[  # Optional
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 4 - Beta',

    # Indicate who your project is intended for
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',

    # Pick your license as you wish
    'License :: OSI Approved :: MIT License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)