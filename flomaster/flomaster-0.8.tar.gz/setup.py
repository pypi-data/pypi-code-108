from distutils.core import setup

setup(
  name = 'flomaster',         # How you named your package folder (MyLib)
  packages = ['flomaster'],   # Chose the same as "name"
  version = '0.8',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Package to automatically generate the most suitable plot for your data',   # Give a short description about your library
  author = 'Flomasterner',                   # Type in your name
  author_email = 'flo.master@pingisht.metric',      # Type in your E-Mail
  url = 'https://github.com/narine998',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/HaykTarkhanyan/flomasterplot/archive/refs/tags/v_08.tar.gz',    # I explain this later on
  keywords = ['plotly', 'data frame', 'automation'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'pandas',
          'streamlit', 
          'plotly', 
          'pillow',
          'matplotlib',
          'wordcloud', 
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.7',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)