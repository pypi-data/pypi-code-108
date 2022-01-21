import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(name='basic_robotics',
      version='0.1.13',
      description='Basic Robotics Toolbox Developed in FASER Lab',
      url='http://github.com/storborg/funniest',
      author='William Chapin',
      author_email='liam@64b1t.com',
      license='MIT',
      packages=['basic_robotics'],
      install_requires=[
          'numpy',
          'scipy',
          'numba',
          'modern_robotics',
          'numpy-stl',
          'descartes',
          'alphashape',
          'trimesh',
      ],
      zip_safe=False)
