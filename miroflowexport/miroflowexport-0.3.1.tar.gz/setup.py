from distutils.core import setup

setup(name='miroflowexport',
      version='0.3.1',
      description='Derive a Gantt-like plan from Miro sticky note workflow',
      author='Sven Flake',
      author_email='sven.flake@gmail.com',
      url='https://gitlab.com/sven.flake/miroflowexport',
      packages=['miroflowexport'],
      install_requires=[
            "flexlog",
            "coolname",
            "pandas",
            "openpyxl",
      ],
     )