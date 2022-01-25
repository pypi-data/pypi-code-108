#!/usr/bin/env python

##  graph_based_dataflow.py

##  The goal of this script is to demonstrate forward propagation of input data
##  through a DAG while computing the partial derivatives of the output at each
##  dependent node with respect to the learnable parameters associated with the links
##  of the incoming arcs.  These partial derivatives are subsequently used to update
##  the values of the link parameters.

##  Note that the DAG specified by the 'expressions' constructor parameter below is
##  NOT a real learning network since it does not include any activations.

import random

seed = 0           
random.seed(seed)

from ComputationalGraphPrimer import *

cgp = ComputationalGraphPrimer(
               expressions = ['xx=xa^2', 
                              'xy=ab*xx+ac*xa', 
                              'xz=bc*xx+xy', 
                              'xw=cd*xx+xz^3'],
               output_vars = ['xw'],
               dataset_size = 10000,
               learning_rate = 1e-6,
               display_loss_how_often = 1000,
               grad_delta = 1e-4,
      )

cgp.parse_expressions()

#cgp.display_network1()
cgp.display_network2()

cgp.gen_gt_dataset(vals_for_learnable_params = {'ab':1.0, 'bc':2.0, 'cd':3.0, 'ac':4.0})

cgp.train_on_all_data()

cgp.plot_loss()

