#!/usr/bin/env python

### setup.py

from setuptools import setup, find_packages
import sys, os

setup(name='ComputationalGraphPrimer',
      version='1.0.7',
      author='Avinash Kak',
      author_email='kak@purdue.edu',
      maintainer='Avinash Kak',
      maintainer_email='kak@purdue.edu',
      url='https://engineering.purdue.edu/kak/distCGP/ComputationalGraphPrimer-1.0.7.html',
      download_url='https://engineering.purdue.edu/kak/distCGP/ComputationalGraphPrimer-1.0.7.tar.gz',
      description='An educational module meant to serve as a prelude to talking about automatic differentiation in deep learning frameworks (such as in the Autograd module of PyTorch)',
      long_description='''

Consult the module API page at

      https://engineering.purdue.edu/kak/distCGP/ComputationalGraphPrimer-1.0.7.html

for all information related to this module, including information related
to the latest changes to the code.  

::

        from ComputationalGraphPrimer import *
        
        cgp = ComputationalGraphPrimer(
                       expressions = ['xx=xa^2',
                                      'xy=ab*xx+ac*xa',
                                      'xz=bc*xx+xy',
                                      'xw=cd*xx+xz^3'],
                       output_vars = ['xw'],
                       dataset_size = 10000,
                       learning_rate = 1e-6,
                       grad_delta    = 1e-4,
                       display_vals_how_often = 1000,
              )
        
        cgp.parse_expressions()
        cgp.display_network1()                                                                    
        cgp.gen_gt_dataset(vals_for_learnable_params = {'ab':1.0, 'bc':2.0, 'cd':3.0, 'ac':4.0})
        cgp.train_on_all_data()
        cgp.plot_loss()

          ''',

      license='Python Software Foundation License',
      keywords='computing in a graph',
      platforms='All platforms',
      classifiers=['Topic :: Scientific/Engineering', 'Programming Language :: Python :: 2.7', 'Programming Language :: Python :: 3.6'],
      packages=['ComputationalGraphPrimer']
)
