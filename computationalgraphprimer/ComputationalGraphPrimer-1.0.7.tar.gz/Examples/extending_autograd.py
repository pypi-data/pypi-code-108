#!/usr/bin/env python

##  extending_autograd.py

"""This script is for experimenting with extending Autograd and it calls on
DLStudio's inner class AutogradCustomization for the demonstration.

The purpose of this inner class is to illustrate how to extend Autograd with
additional functionality. That inner class implements the what is mentioned
at the following doc page

               https://pytorch.org/docs/stable/notes/extending.html

for extending Autograd.

Extending Autograd requires that you define a new verb class, as I have with the
class DoSillyWithTensor shown in the main module file, with definitions for two
static methods, "forward()" and "backward()".  An instance constructed from this
class is callable.  So when, in the "forward()" of the network, you pass a training
sample through an instance of DoSillyWithTensor, it is subject to the code shown
in the "forward()" of DoSillyWithTensor.
"""

import random
import numpy
import torch
import os, sys


seed = 0           
random.seed(seed)
torch.manual_seed(seed)
torch.cuda.manual_seed(seed)
numpy.random.seed(seed)
torch.backends.cudnn.deterministic=True
torch.backends.cudnn.benchmarks=False
os.environ['PYTHONHASHSEED'] = str(seed)


##  watch -d -n 0.5 nvidia-smi

from ComputationalGraphPrimer import *

cgp =  ComputationalGraphPrimer(
                  learning_rate = 1e-6,
                  epochs = 5,
              )

ext_auto = ComputationalGraphPrimer.AutogradCustomization( 
                                           cgp = cgp,
                                           num_samples_per_class = 1000,
                                         )                 
ext_auto.gen_training_data()
ext_auto.train_with_straight_autograd()
ext_auto.train_with_extended_autograd()

