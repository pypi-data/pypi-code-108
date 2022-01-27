# -*- coding: utf-8 -*-
# ##########################################################################################
# Copyright (c) 2021, INRIA                                                              #
# All rights reserved.                                                                   #
#                                                                                        #
# BSD License 2.0                                                                        #
#                                                                                        #
# Redistribution and use in source and binary forms, with or without                     #
# modification, are permitted provided that the following conditions are met:            #
# * Redistributions of source code must retain the above copyright notice,               #
# this list of conditions and the following disclaimer.                                  #
# * Redistributions in binary form must reproduce the above copyright notice,            #
# this list of conditions and the following disclaimer in the documentation              #
# and/or other materials provided with the distribution.                                 #
# * Neither the name of the <copyright holder> nor the names of its contributors         #
# may be used to endorse or promote products derived from this software without          #
# specific prior written permission.                                                     #
#                                                                                        #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND        #
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED          #
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.     #
# IN NO EVENT SHALL INRIA BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,       #
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF     #
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) #
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,  #
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS  #
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.                           #
#                                                                                        #
# Contacts:                                                                              #
# 	Remi Gribonval  : remi.gribonval@inria.fr                                        #
# 	Hakim Hadj-dji. : hakim.hadj-djilani@inria.fr                                    #
#                                                                                        #
# Authors:                                                                               #
# 	Software Engineers:                                                              #
# 		Nicolas Bellot                                                           #
# 		Thomas Gautrais,                                                         #
# 		Hakim Hadj-Djilani,                                                      #
# 		Adrien Leman,                                                            #
#                                                                                        #
# 	Researchers:                                                                     #
# 		Luc Le Magoarou,                                                         #
# 		Remi Gribonval                                                           #
#                                                                                        #
# 	INRIA Rennes, FRANCE                                                             #
# 	http://www.inria.fr/                                                             #
##########################################################################################


from __future__ import print_function
from pylab import *
import os,sys

## @package pyfaust.demo @brief The pyfaust demo module.
##
## The run*() functions produce the results (by default in demo.DEFT_RESULTS_DIR)
## and the fig*() functions produce the figures based on the results (by
## default in demo.DEFT_FIG_DIR).
## @warning this demo module is a recent port from matlab version and should be considered in beta status.


## \brief The default output directory for the demo results.
DEFT_RESULTS_DIR = 'pyfaust_demo_output'
## \brief The default figure output directory for the demos.
DEFT_FIG_DIR = 'pyfaust_demo_figures'

def get_data_dirpath(silent=True):
    """
        Returns the data directory path which varies according to the way pyfaust was installed.
    """
    from pkg_resources import resource_filename
    from os.path import exists, join, expanduser, isfile
    from os import sep, listdir, mkdir
    from pyfaust.datadl import download_uncompress
    path = resource_filename(__name__, 'data')
    if (sys.platform == 'win32' and not os.path.exists(path)):
        try:
            from pyfaust import _NSI_INSTALL_PATH
        except:
            _NSI_INSTALL_PATH = ''
        # in windows nsis based installation the data can be anywhere
        # users choose to install faust
        # the nsi installer is responsible to set this const var
        # at installation stage
        # in this case, matlab is inst so point to its data dir
        path = _NSI_INSTALL_PATH+sep+'matlab'+sep+'data'
    if(not exists(path)):
        # fallback to matlab wrapper data
        # it will not help if we are from pip pkg
        # but it shouldn't happen
        path = ''
    if(exists(path)):
        loc_files = [f for f in listdir(path) if isfile(join(path, f))]
    else:
        loc_files = []
    if(len(loc_files) == 0):
        # download data in user folder
        path = join(expanduser('~'), "pyfaust_data")
        if(not exists(path)):
            mkdir(path)
        download_uncompress(path, already_downloaded_msg=not silent)
    return path

def runall():
    """Runs all the demos in a row.
    Example:
        >>> from pyfaust.demo import runall, allfigs
        >>> runall()
        >>> # benchmark data files go in DEFT_RESULTS_DIR
        >>> allfigs()
        >>> # figures resulting from benchmark go in DEFT_FIG_DIR
    """
    def print_header(title):
        print("******************** Running", title, "demo")
    for func,title in zip([ quickstart.run, runtimecmp.run, bsl.run,
                 fft.speed_up_fourier, hadamard.run_fact, hadamard.run_norm_hadamard,
                 hadamard.run_speedup_hadamard], ["quickstart", "runtime"+
                                                  " comparison", "BSL", "FFT",
                                                  "Hadamard factorization",
                                                  "Hadamard norm", "Hadamard"+
                                                  " speedup"]):
        print_header(title)
        func()

def allfigs():
    """
    Renders all the demo figures into files.

    NOTE: The function must be call after runall() or after each demo run* function executed
    separately.
    """
    def print_header(title):
        print("******************** Rendering figure: ", title, "demo")
    for func,title in zip([ runtimecmp.fig, bsl.fig,
                 fft.fig_speed_up_fourier, hadamard.figs], ["quickstart", "runtime"+
                                                  " comparison", "BSL", "FFT",
                                                  "Hadamard factorization,"+
                                                           "norm and speedup"]):
        print_header(title)
        func()

class quickstart:
    """
        The FAuST quickstart script, a good place to look at for a first tour.
    """
    @staticmethod
    def run():
        """
            Launches the quickstart demo.
        """
        import pyfaust;

        # import module to generate data
        import scipy
        from scipy import sparse as sp
        import numpy as np


        # generate the factors of the Faust
        dim1 = 1000;
        dim2 = 2000;
        nb_factor = 2;
        list_factor_sparse=[0]*nb_factor
        list_factor=[0]*nb_factor
        int_max = 120
        density_per_fact=0.1;
        list_factor_sparse[0]=int_max*sp.random(dim1,dim1,density=density_per_fact,format='csr',dtype=np.float64);
        list_factor[0]=list_factor_sparse[0].toarray();
        list_factor_sparse[1]=int_max*sp.random(dim1,dim2,density=density_per_fact,format='csr',dtype=np.float64);
        list_factor[1]=list_factor_sparse[1].toarray();


        #print(list_factor[0])
        #print(list_factor[1])


        # create a Faust named F from its factors
        A = pyfaust.Faust(list_factor)

        # get the size of the Faust
        print("dimension of the Faust : ", A.shape)

        # transpose a Faust
        A_trans = A.transpose()

        # multiplication a numpy array by a Faust
        x = np.random.randint(int_max, size=(dim2,1))
        y = A @ x

        # convert a faust to numpy array
        A_numpy = A.toarray()

        # slicing
        coeff = A[0,0]
        col_2nd = A[:,1];
        submatrix_A = A[3:5,2:3]



        # speed-up multiplication
        import time
        nb_mult = 100
        t_dense = 0.0;
        t_faust = 0.0;

        for i in range(nb_mult):
            x=np.random.randint(int_max, size=(dim2,1))

            t_begin = time.time()
            y_dense = A_numpy.dot(x)
            t_elapsed = time.time() - t_begin
            t_dense += t_elapsed

            t_begin = time.time()
            y_faust=A@x;
            t_elapsed = time.time()-t_begin
            t_faust += t_elapsed

        print("multiplication SPEED-UP using Faust")
        print("Faust is "+str(t_dense/t_faust)+" faster than a full matrix")
        print("Faust nnz: "+str(A.nnz_sum()))
        print("Faust density: "+str(A.density()))
        print("Faust RCG: "+str(A.rcg()))
        print("Faust norm: "+str(A.norm()))
        print("Faust nb of factors: "+str(A.numfactors()))
        for i in range(0,A.numfactors()):
            #print("Faust size of factor ",i,"=",A.factors(i).shape)
            # test Faust gets back the same sparse factors given at init
            assert((A.factors(i) == list_factor_sparse[i]).all())
            #print(A.factors(i))

        # test Faust saving
        A.save("A.mat")
        As = pyfaust.Faust(filepath="A.mat")
        assert((A.factors(0) == As.factors(0)).all())
        assert((A.factors(1) == As.factors(1)).all())

        # test Faust transpose
        #print(A.factors(0))
        tA = A.transpose()
        tf1 = tA.factors(1)
        #print(tf1)
        f1 = np.transpose(tf1)
        assert(not (tf1 == A.factors(0)).all() or (tf1 == f1).all())
        assert((f1 == A.factors(0)).all())

        print("end quickstart.py")

class fft:
    """
    FFT demo: multiplication runtime comparison between DFT matrix-vector and Faust(FFT)-vector.
    """

    _nb_mults = 500
    _log2_dims = arange(6,12)
    _dims = 2**_log2_dims

    _FFT_FAUST_FULL=0
    _FFT_FAUST=1
    _FFT_NATIVE=2

    _NUM_FFT_TYPES=3


    @staticmethod
    def fig_speed_up_fourier(input_dir=DEFT_RESULTS_DIR,
                             output_dir=DEFT_FIG_DIR):
        """
            Builds the speedup figure.
        """
        import os.path

        input_path = input_dir+os.sep+'speed_up_fourier.txt'
        mult_times = loadtxt(input_path).reshape(fft._nb_mults, len(fft._dims), fft._NUM_FFT_TYPES)
        # fft._NUM_FFT_TYPES == 3 is for fft._FFT_FAUST, fft._FFT_FAUST_FULL, fft._FFT_NATIVE

        mean_mult_times = squeeze(mult_times.mean(axis=0))

        curve_thickness = 2
        legend_loc = 'upper left'

        plt.rcParams['figure.figsize'] = [12.0, 8]
        subplot(211)

        #hold(True)
        line_marker_types = [ 'ro-', 'bo-', 'go-', 'r+-', 'b+-', 'g+-' ]

        title('Runtime Fourier A*x')
        for i in range(0,fft._NUM_FFT_TYPES):
            semilogy(fft._log2_dims, mean_mult_times[:,i],line_marker_types[i],
                     lw=curve_thickness)
            ylabel('Computed Time (sec)')
        # legend(['dense', 'Faust', 'fft'], loc=legend_loc) # in first subplot
        grid(True)
        axes([fft._log2_dims[0], fft._log2_dims[-1], mean_mult_times.min(),
              mean_mult_times.max()])
        xticks(fft._log2_dims)

        subplot(212)
        grid(True)
        title('Speedup Fourier A*x')
        for i in range(1,fft._NUM_FFT_TYPES):
            semilogy(fft._log2_dims, mean_mult_times[:,0]/mean_mult_times[:,i],
                     line_marker_types[i], lw=curve_thickness)
            ylabel('Speedup Fourier A*x')
            xlabel ('log(dim)')

        figlegend(figure(1).get_axes()[0].get_lines(),['dense', 'faust',
                                                       'fft'],loc='best')


        if(not os.path.exists(output_dir)):
            os.mkdir(output_dir)
        savefig(output_dir+os.sep+'Fourier-RuntimeComp-Speedup.png',
                dpi=200)
        show(block=False)



    @staticmethod
    def speed_up_fourier(output_dir=DEFT_RESULTS_DIR):
        """
            Runs the multiplication benchmark.
        """
        from pyfaust import Faust, dft
        threshold = 10**-10

        print('Speedup Fourier')
        print("===============")
        print('Generating data...')

        fft_mats = []
        fft_fausts = []

        for k in range(0,len(fft._dims)):
            print('\rFFT fft._dims processed: ', fft._dims[0:k+1], end='')
            F = dft(fft._dims[k], normed=False)
            fft_mat = F.toarray()#fft(eye(fft._dims[k])) # or TODO: F.toarray() ?
            fft_fausts += [ F ]
            fft_mats += [ fft_mat ]
        print()

        print("Gathering computation times...")

        mult_times = ndarray(shape=(fft._nb_mults, len(fft._dims), 3))
        # 3 for: fft._FFT_FAUST_FULL, fft._FFT_FAUST, fft._FFT_NATIVE


        for i in range(0,fft._nb_mults):
            print('\r#muls:',i+1,'/', fft._nb_mults, end='')
            for k in range(0,len(fft._dims)):
               dim = fft._dims[k]
               fft_mat = fft_mats[k]
               fft_faust = fft_fausts[k]
               ydense = empty(dim)
               yfaust = empty(dim)
               yfft = empty(dim)
               ydense_trans = empty(dim)
               yfaust_trans = empty(dim)
               x = rand(dim,1)
               t = _timer()
               ydense = fft_mat.dot(x)
               mult_times[i,k,fft._FFT_FAUST_FULL] = _timer()-t
               t = _timer()
               yfaust = fft_faust@x
               mult_times[i,k,fft._FFT_FAUST] = _timer()-t
               t = _timer()
               yfft = fft2(x)
               mult_times[i,k,fft._FFT_NATIVE] = _timer()-t
               if(norm(ydense-yfaust)>threshold):
                   raise Exception('Multiplication error: larger error than '
                                   'threshold for ydense.')

               from numpy.fft import fft as npfft
               ref_fft = np.eye(fft._dims[k])
               n1 = norm(npfft(ref_fft)-fft_faust.toarray())/norm(ref_fft)
               assert(n1 < threshold)
               if(norm(yfft-yfaust)/norm(yfft)>threshold):
                   print('\nerror:', norm(yfft-yfaust))
                   raise Exception('Multiplication error: larger error than '
                                   'threshold for yfaust')

        print()


        import os.path
        if(not os.path.exists(output_dir)):
           os.mkdir(output_dir)
        output_path = output_dir+os.sep+'speed_up_fourier.txt'
        savetxt(output_path, mult_times.reshape(mult_times.size))

        # test
        # mult_times_r = loadtxt(output_path).reshape(mult_times.shape)
        # assert(all(mult_times_r == mult_times))



class runtimecmp:
    """
        Runtime comparison demo: Faust-vector and dense matrix-vector multiplications, differents RCGs, transpose.
    """
    _rcgs = [2, 4, 8]
    _dims = [128, 256, 512]
    _nb_facts = [2, 4, 8]
    _nb_mults = 500
    _constraint = True # 'per_row' # per_col
    _dims_len = len(_dims)
    _rcgs_len = len(_rcgs)
    _nb_facts_len = len(_nb_facts)

    @staticmethod
    def run(output_dir=DEFT_RESULTS_DIR):
        """
        Runs the runtime comparision benchmark.
        """
        from pyfaust import (Faust, rand as frand)

        matrix_or_vector = 'vector'


        fausts = ndarray(shape=(runtimecmp._dims_len, runtimecmp._rcgs_len, runtimecmp._nb_facts_len), dtype=Faust)
        dense_mats =  list()


        # loading all the different Fausts and dense matrices
        for j in range(0,runtimecmp._dims_len):
            dim = runtimecmp._dims[j]
            A = rand(dim, dim)
            dense_mats.append(A)

            for k in range(0,runtimecmp._rcgs_len):
                rcg = runtimecmp._rcgs[k]

                for l in range(0,runtimecmp._nb_facts_len):
                    nf = runtimecmp._nb_facts[l]
                    F = frand(dim, dim, nf, density=1./(nf*rcg),
                                          per_row=runtimecmp._constraint, fac_type='sparse')
                    assert(F.rcg() == rcg)
                    fausts[j,k,l] = F
                    assert(F.shape == (dim,dim))



        tdense = ndarray(shape=(runtimecmp._nb_mults, runtimecmp._dims_len, 2))
        tfaust = ndarray(shape=(runtimecmp._nb_mults, runtimecmp._dims_len,
                                runtimecmp._rcgs_len, runtimecmp._nb_facts_len, 2))

        for i in range(0, runtimecmp._nb_mults):
            print("\r\r #muls =",i+1,'/',runtimecmp._nb_mults, end='')
            for j in range(0,runtimecmp._dims_len):
                dim = runtimecmp._dims[j]

                if(matrix_or_vector == 'matrix'):
                    dim2 = dim # mul. by a square matrix
                elif(matrix_or_vector == 'vector'):
                    dim2 = 1
                else:
                    raise("matrix_or_vector string must be equal to matrix or"
                          " vector")

                for k in range(0,runtimecmp._rcgs_len):
                    rcg = runtimecmp._rcgs[k]

                    for l in range(0,runtimecmp._nb_facts_len):
                        nf = runtimecmp._nb_facts[l]
                        x = rand(dim,dim2)

                        if(k == 0 and l == 0):
                            A = dense_mats[j]
                            t = _timer()
                            y = A.dot(x)
                            tdense[i,j,0] = _timer()-t
                            t = _timer()
                            y_trans = A.T.dot(x)
                            tdense[i,j,1] = _timer()-t

                        F = fausts[j,k,l]
                        t = _timer()
                        yfaust = F@x
                        tfaust[i,j,k,l,0] = _timer()-t
                        t = _timer()
                        yfaust_trans = F.T@x
                        tfaust[i,j,k,l,1] = _timer()-t

        print()
        import os.path
        if(not os.path.exists(output_dir)):
           os.mkdir(output_dir)
        path_tfaust = output_dir+os.sep+'runtime_cmp_tfaust-'+matrix_or_vector+'.txt'
        path_tdense = output_dir+os.sep+'runtime_cmp_tdense-'+matrix_or_vector+'.txt'
        savetxt(path_tdense, tdense.reshape(tdense.size))
        savetxt(path_tfaust, tfaust.reshape(tfaust.size))

        # test
        #tfaust_r = loadtxt(path_tfaust).reshape(tfaust.shape)
        #assert(all(tfaust_r == tfaust))
        #tdense_r = loadtxt(path_tdense).reshape(tdense.shape)
        #assert(all(tdense_r == tdense))

    @staticmethod
    def fig(input_dir=DEFT_RESULTS_DIR,
                               output_dir=DEFT_FIG_DIR):
        """
        Renders in file the demo figure in file from the results of runtimecmp.run.

        """
        import os.path, os
        input_file_existing = False

        for matrix_or_vector in  ('vector', 'matrix'):
            path_tfaust = input_dir+os.sep+'runtime_cmp_tfaust-'+matrix_or_vector+'.txt'
            path_tdense = input_dir+os.sep+'runtime_cmp_tdense-'+matrix_or_vector+'.txt'
            if(os.path.exists(path_tfaust) and os.path.exists(path_tdense)):
                input_file_existing = True
                break

        if(not input_file_existing):
            raise Exception("Input files don't exist, please run"
                            " runtimecmp.run() first.")

        if(not os.path.exists(output_dir)):
            os.mkdir(output_dir)

        tfaust = loadtxt(path_tfaust).reshape(runtimecmp._nb_mults,
                                              runtimecmp._dims_len, runtimecmp._rcgs_len, runtimecmp._nb_facts_len, 2)
        tdense = loadtxt(path_tdense).reshape(runtimecmp._nb_mults, runtimecmp._dims_len, 2)


        # average the mul. times according the number of runs
        mean_tdense = squeeze(tdense.mean(axis=0))
        mean_tfaust = squeeze(tfaust.mean(axis=0))

        # avoid legend overlapping axis
        plt.rcParams['figure.figsize'] = [12.0, 8]
        #print("mean_tdense=", mean_tdense, mean_tdense.shape)

        # plot the time computed in logscale with a fixed number of factors in a given figure
        # in each figure we have in x-axis the log2(dimension) of the square matrix
        #                         in y-axis the time
        # all times for faust multiplication with different RCG (density)
        # and the times for dense matrix multiplication are plotted

        curve_thickness = 2

        # hold differents figures in the same box
        ymin = min(mean_tdense.min(), mean_tfaust.min())
        ymax = max(mean_tdense.max(), mean_tfaust.max())

        legendy = [ 'Time (A*x)', 'Time (A.T*x)']

        fig, ax = subplots(2,runtimecmp._nb_facts_len, sharex=True, sharey=True)#, h*runtimecmp._nb_facts_len+nf+1)
        for h in arange(0,2):
            for nf in range(0,runtimecmp._nb_facts_len):

                legend_curve = []
                lines = []
                for k in range(0, runtimecmp._rcgs_len):
                    lines.append(*ax[h,nf].semilogy(log2(runtimecmp._dims), mean_tfaust[:, k, nf, h],
                             '-+', lw=curve_thickness))
                    legend_curve.append('Faust RCG '+str(runtimecmp._rcgs[k]))
                    #hold(True)

                lines.append(*ax[h,nf].semilogy(log2(runtimecmp._dims), squeeze(mean_tdense[:,h]), '-+', c=(0, .8, .8),
                         lw=curve_thickness))

                legend_curve.append('Dense ')

                ax[h,nf].grid(True)
                axes([log2(runtimecmp._dims[0]), log2(runtimecmp._dims[-1]), ymin, ymax])
                if(h == 0):
                    ax[h,nf].set_title('#factors: '+str(runtimecmp._nb_facts[nf]))
                # legend for it axis (a bit heavy to read)
                #ax[h,nf].legend(legend_curve)
                #legend('best')
                if(nf == 0):
                    if(h == 1):
                        ax[h,nf].set_xlabel("log2(Dimension)")
                    ax[h,nf].set_ylabel(legendy[h])

        figlegend(lines,legend_curve,loc='upper left')
        # TODO: figure.Name matlab ?
        constraint_str = 'sp'
        # fig_name = 'Faust-'+matrix_or_vector+' multiplication '
        #        '(_constraint: 'constraint_str+')')
        savefig(output_dir+os.sep+'RuntimeComp-'+matrix_or_vector+'_multiplication_constraint_'+constraint_str+'.png',
               dpi=200)
        #tight_layout()
        show(block=False)

class hadamard:
    """
        The demo for the hierarchical factorization of Hadamard matrices.
    """
    _nb_mults = 500
    _nb_norms = 10
    _n = 5
    _nfacts = _n
    _tdense_fname = 'hadamardfact_mul_runtime_dense.txt'
    _tfaust_fname = 'hadamardfact_mul_runtime_faust.txt'
    _had_faust_fname = 'hadamardfact_faust.mat'
    _speedup_times_fname = 'hadamardfact_speedup_times.txt'
    _norm_times_fname = 'hadamard_norm_times.txt'
    _norm_err_fname = 'hadamard_norm_errs.txt'
    _norm_rcgs_fname = 'hadamard_norm-rcgs.txt'
    _fig1_fname = 'Hadamard-factorization.png'
    _fig2_fname = 'Hadamard-factorization_nnz_coeff.png'
    _fig_speedup = 'Hadamard-speedup.png'
    _fig_norm = 'Hadamard-norm.png'
    _HAD_DENSE, _HAD_FAUST, _HAD_TRANS_DENSE, _HAD_TRANS_FAUST = range(0,4)
    _NUM_TIME_TYPES = 4
    _log2_dims = arange(6,15)
    _dims = 2**_log2_dims
    _norm_log2_dims = arange(6,12)
    _norm_dims = 2**_norm_log2_dims
    _NUM_NORM_TIME_TYPES = 2

    @staticmethod
    def run_fact(output_dir=DEFT_RESULTS_DIR):
        """This demo hierarchically factorizes the Hadamard dictionary and then plots the results.
        This essentially reproduces figure 2 from [1].

        [1] Le Magoarou L. and Gribonval R., "Flexible multi-layer sparse
        approximations of matrices and applications", Journal of Selected
        Topics in Signal Processing, 2016.

        """
        from pyfaust import wht
        from pyfaust.factparams import ParamsHierarchical, ConstraintInt, \
        ConstraintName, StoppingCriterion
        from pyfaust.fact import hierarchical

        # generate a Hadamard transform and factorize its full matrix
        n = hadamard._n
        d = 2**n
        H = wht(d)
        full_H = H.toarray()

        params = ParamsHierarchical([ConstraintInt(ConstraintName(ConstraintName.SPLINCOL),d,d,2)
                                        for i in range(0,n-1)],
                                        [ConstraintInt(ConstraintName(ConstraintName.SPLINCOL),d,d,int(d/2.**(i+1)))
                                         for i in range(0,n-1)],
                                        StoppingCriterion(num_its=30),StoppingCriterion(num_its=30),
                                        is_update_way_R2L=True)
        had_faust = hierarchical(H.toarray(), params)
        full_had_faust = had_faust.toarray()
        rel_err = norm(full_had_faust-full_H)/norm(full_H)
        print("\n\nRelative error between hadamard matrix and its transform: ",
              rel_err)

        # gather computation times
        _nb_mults = hadamard._nb_mults
        dense_times = empty(_nb_mults)
        faust_times = empty(_nb_mults)

        for i in range(0,_nb_mults):
            print("\r\r #muls =",i+1,'/', _nb_mults, end='')
            x = rand(d,1)

            t = _timer()
            y_X = full_H.dot(x)
            dense_times[i] = _timer()-t

            t = _timer()
            y_faust = had_faust@x
            faust_times[i] = _timer()-t



        print()


        path_tdense = _write_array_in_file(output_dir,
                                           hadamard._tdense_fname,
                                           dense_times)
        path_tfaust = _write_array_in_file(output_dir,
                                           hadamard._tfaust_fname,
                                           faust_times)
        had_faust.save(_prefix_fname_with_dir(output_dir,
                                              hadamard._had_faust_fname))

        # test
#        tfaust_r = loadtxt(path_tfaust)
#        assert(all(tfaust_r == faust_times))
#        tdense_r = loadtxt(path_tdense)
#        assert(all(tdense_r == dense_times))


    @staticmethod
    def fig_fact(input_dir=DEFT_RESULTS_DIR, output_dir=DEFT_FIG_DIR):
        """
        Renders in file the figure for the results produced by hadamard.run_fact.
        """
        from pyfaust import Faust
        fig_dir = DEFT_FIG_DIR
        if(not os.path.exists(fig_dir)):
            os.mkdir(fig_dir)
        #hold(True)

        had_faust = Faust(filepath=_prefix_fname_with_dir(input_dir,
                                                          hadamard._had_faust_fname))
        fig1 = figure(1)
        subplot("1"+str(had_faust.numfactors()+1)+'1')
        imshow(had_faust.toarray())
        xticks([])
        yticks([])
        facts = [];
        for i in range(0,had_faust.numfactors()):
            subplot("1"+str(hadamard._nfacts+1)+str(i+2))
            # all factors are normally sparse
            fac = had_faust.factors(i)
            facts.append(fac)
            if(not isinstance(fac,ndarray)):
                fac = fac.toarray()
            imshow(fac)
            xticks([])
            yticks([])

        fig2 = figure(2)
        subplot("1"+str(had_faust.numfactors()+1)+'1')
        imshow(had_faust.toarray())
        xticks([])
        yticks([])
        for i in range(0,had_faust.numfactors()):
            subplot("1"+str(hadamard._nfacts+1)+str(i+2))
            title("nz = "+str(count_nonzero(fac)))
            spy(facts[i], markersize=1)
            xticks([])
            yticks([])

        _write_fig_in_file(output_dir, hadamard._fig1_fname, fig1)
        _write_fig_in_file(output_dir, hadamard._fig2_fname, fig2)
        show(block=False)

    @staticmethod
    def _create_hadamard_fausts_mats(dims, log2_dims):
        from pyfaust import wht
        had_mats = []
        had_fausts = []
        for k in range(0, len(log2_dims)):
            print("\rHadamard dims processed: ", dims[0:k+1], end='')
            F = wht(2**log2_dims[k])
            had_fausts += [ F ]
            had_mats += [ F.toarray() ]
        print()
        return had_mats, had_fausts

    @staticmethod
    def run_speedup_hadamard(output_dir=DEFT_RESULTS_DIR):
        """
		This demo makes some time comparison between (Hadamard matrix)-vector multiplication and (Hadamard factorisation i.e a FAuST)-vector multiplication for Hadamard matrices of different sizes.
        """
        threshold = 10.**-10
        print("Speedup Hadamard")
        print("================")
        print("Generating data...")
        _dims, _log2_dims = hadamard._dims, hadamard._log2_dims

        had_mats, had_fausts = hadamard._create_hadamard_fausts_mats(_dims, _log2_dims)

        print("Gathering multiplication computation times...")

        _nb_mults = hadamard._nb_mults
        _NUM_TIME_TYPES = hadamard._NUM_TIME_TYPES
        _HAD_DENSE, _HAD_TRANS_DENSE, _HAD_FAUST, _HAD_TRANS_FAUST = \
                hadamard._HAD_DENSE, hadamard._HAD_TRANS_DENSE, \
                hadamard._HAD_FAUST, hadamard._HAD_TRANS_FAUST
        mult_times = ndarray(shape=(_nb_mults, len(_dims), _NUM_TIME_TYPES))

        for i in range(0,_nb_mults):
            print('\r#muls:',i+1,'/', _nb_mults, end='')
            for k in range(0,len(_dims)):
                dim = _dims[k]
                had_mat = had_mats[k]
                had_faust = had_fausts[k]

                x = rand(dim,1)

                t = _timer()
                ydense = had_mat.dot(x)
                mult_times[i,k,_HAD_DENSE] = _timer()-t

                t = _timer()
                yfaust = had_faust*x
                mult_times[i,k,_HAD_FAUST] = _timer()-t

                if(norm(ydense-yfaust) > threshold):
                   raise Exception("speedup hadamard: mul. error greater than "
                                   "threshold")

                t = _timer()
                ydense_trans = had_mat.T.dot(x)
                mult_times[i,k,_HAD_TRANS_DENSE] = _timer()-t

                t = _timer()
                yfaust_trans = had_faust.T*x
                mult_times[i,k,_HAD_TRANS_FAUST] = _timer()-t

                if(norm(yfaust_trans-ydense_trans) > threshold):
                   raise Exception("speedup_hadamard: mul. error on transpose "
                                   "faust/mat.")


        print()

        path_mult_times = _write_array_in_file(output_dir,
                                              hadamard._speedup_times_fname,
                                              mult_times.reshape(mult_times.size))
        mult_times_r = loadtxt(path_mult_times)
        assert(all(mult_times_r.reshape(mult_times.shape) == mult_times))

    @staticmethod
    def fig_speedup_hadamard(output_dir=DEFT_FIG_DIR, input_dir=DEFT_RESULTS_DIR):
        """
        Renders in file the figure for the results produced by hadamard.run_speedup_hadamard.
        """
        times_txt_fpath = _prefix_fname_with_dir(input_dir, hadamard._speedup_times_fname)
        if(not os.path.exists(times_txt_fpath)):
            raise Exception("Input file doesn't exist, please call "
                            "run_speedup_hadamard() before calling "
                            "fig_speedup_hadamard()")
        _nb_mults, _dims, _NUM_TIME_TYPES = hadamard._nb_mults, \
                hadamard._dims, hadamard._NUM_TIME_TYPES
        mult_times = loadtxt(times_txt_fpath).reshape(_nb_mults, len(_dims),
                                                      _NUM_TIME_TYPES)

        _HAD_DENSE, _HAD_TRANS_DENSE, _HAD_FAUST, _HAD_TRANS_FAUST = \
               hadamard._HAD_DENSE, hadamard._HAD_TRANS_DENSE, \
               hadamard._HAD_FAUST, hadamard._HAD_TRANS_FAUST
        _log2_dims = hadamard._log2_dims

        # mean times of each category and speedups
        mean_mult_times = mult_times.mean(axis=0)
        print(mult_times)
        speedup_trans = mean_mult_times[:,_HAD_TRANS_DENSE] / \
        mean_mult_times[:,_HAD_TRANS_FAUST]
        speedup = mean_mult_times[:,_HAD_DENSE] / mean_mult_times[:,_HAD_FAUST]
        plt.rcParams['figure.figsize'] = [12.0, 8]

        # plot results
        line_width = 2.
        for t in [("1","A*x", _HAD_FAUST, _HAD_DENSE),("3", "A.T*x",
                                                       _HAD_TRANS_FAUST,
                                                       _HAD_TRANS_DENSE)]:
            ymin = min(min(mean_mult_times[:,t[2]]),
                       min(mean_mult_times[:,t[3]]))
            ymax = max(max(mean_mult_times[:,t[2]]),
                       max(mean_mult_times[:,t[3]]))

            subplot("22"+t[0])
            title('Runtime Hadamard '+t[1])
            grid(True)
            #hold(True)
            semilogy(_log2_dims, mean_mult_times[:,t[2]], lw=line_width)
            semilogy(_log2_dims, mean_mult_times[:, t[3]], lw=line_width)
            ylabel('Computed Time (sec)')
            if(t[0] == "3"): xlabel('log(dim)')
            legend(['Faust', 'Dense'])
            axes([_log2_dims[0], _log2_dims[-1], ymin, ymax])

        for t in [("2","A*x", speedup),("4", "A.T*x", speedup_trans)]:
            ymin = min(t[2])
            ymax = max(t[2])

            subplot("22"+t[0])
            title('Speedup Hadamard '+t[1])
            grid(True)
            #hold(True)
            semilogy(_log2_dims, t[2], lw=line_width)
            semilogy(_log2_dims, t[2]/t[2], lw=line_width, c='black')
            ylabel('Speedup')
            if(t[0] == "4"): xlabel('log(dim)')
            legend(['Faust', 'Neutral'])
            axes([_log2_dims[0], _log2_dims[-1], ymin, ymax])

        _write_fig_in_file(output_dir, hadamard._fig_speedup, figure(1))
        show(block=False)

    @staticmethod
    def run_norm_hadamard(output_dir=DEFT_RESULTS_DIR):
        """
        This demo makes some time comparison between the 2-norm of the Hadamard matrix and its Faust representation for differents sizes of the Hadamard matrix.

        """
        threshold = 10.**-10
        print("2-Norm Hadamard")
        print("================")
        print("Generating data...")

        _dims, _log2_dims = hadamard._norm_dims, \
                hadamard._norm_log2_dims
        _nb_norms = hadamard._nb_norms
        _HAD_DENSE, _HAD_FAUST = hadamard._HAD_DENSE, \
        hadamard._HAD_FAUST
        had_mats, had_fausts = hadamard._create_hadamard_fausts_mats(_dims, _log2_dims)
        rcgs = empty((len(_dims)))
        norm_faust = empty(len(_dims))
        norm_dense = empty(len(_dims))
        norm_times = ndarray(shape=(_nb_norms, len(_dims), len([_HAD_DENSE,
                                                                _HAD_FAUST])))

        for i in range(0,_nb_norms):
            print('\r#norm:', i+1,'/', _nb_norms, end='')
            for k in range(0,len(_dims)):
                had_mat = had_mats[k]
                had_faust = had_fausts[k]
                if(i == 0):
                    rcgs[k] = had_faust.rcg()

                t = _timer()
                norm_dense[k] = norm(had_mat, 2)
                norm_times[i, k, _HAD_DENSE] = _timer()-t

                t = _timer()
                norm_faust[k] = had_faust.norm(2)
                norm_times[i, k, _HAD_FAUST] = _timer()-t

        print()
        expected_norm = sqrt(2.**(_log2_dims))

        norm_errs = empty((2, len(_dims)))
        norm_errs[_HAD_DENSE,:] = sqrt((norm_dense - expected_norm)**2)
        #print("norm_errs[_HAD_DENSE,:]=", norm_errs[_HAD_DENSE,:])
        #print("norm_dense=", norm_dense)
        norm_errs[_HAD_FAUST,:] = sqrt((norm_faust - expected_norm)**2)
        #print("norm_errs[_HAD_FAUST,:]=", norm_errs[_HAD_FAUST,:])
        #print("norm_faust=", norm_faust)

        h = hadamard
        _write_array_in_file(output_dir, h._norm_times_fname, norm_times)
        _write_array_in_file(output_dir, h._norm_err_fname, norm_errs)
        _write_array_in_file(output_dir, h._norm_rcgs_fname, rcgs)
#        norm_times_r = \
#                loadtxt(_prefix_fname_with_dir(output_dir,h._norm_times_fname)).reshape(norm_times.shape)
#        assert(all(norm_times_r == norm_times))
#        norm_errs_r = \
#                loadtxt(_prefix_fname_with_dir(output_dir,h._norm_err_fname)).reshape(norm_errs.shape)
#        assert(all(norm_errs_r == norm_errs))
#        rcgs_r = \
#        loadtxt(_prefix_fname_with_dir(output_dir,h._norm_rcgs_fname)).reshape(rcgs.shape)
#        assert(all(rcgs_r == rcgs))



    @staticmethod
    def fig_norm_hadamard(input_dir=DEFT_RESULTS_DIR, output_dir=DEFT_FIG_DIR):
        """
        Renders in file the figure for the results produced by hadamard.run_norm_hadamard.
        """
        h = hadamard
        _nb_norms, _dims, _HAD_DENSE, _HAD_FAUST = h._nb_norms, h._norm_dims, \
                h._HAD_DENSE, h._HAD_FAUST
        num_types = len([_HAD_DENSE, _HAD_FAUST])

        #TODO test file existences

        norm_times_fpath = _prefix_fname_with_dir(input_dir,
                                                  h._norm_times_fname)
        norm_errs_fpath = _prefix_fname_with_dir(input_dir,
                                                 h._norm_err_fname)
        rcgs_fpath = _prefix_fname_with_dir(input_dir, h._norm_rcgs_fname)
        norm_times = loadtxt(norm_times_fpath).reshape(_nb_norms,
                                                       len(_dims),
                                                       num_types)
        norm_errs = loadtxt(norm_errs_fpath).reshape(num_types, len(_dims))

        rcgs = loadtxt(rcgs_fpath)

        line_width = 3

        mean_times = norm_times.mean(axis=0)
        faust_speedup = mean_times[:,_HAD_DENSE] / mean_times[:,_HAD_FAUST]

        plt.rcParams['figure.figsize'] = [13.0, 8]

        # runtime
        subplot(131)
        #hold(True)
        grid(True)
        axis([ h._norm_log2_dims[0], h._norm_log2_dims[-1], mean_times.min(),
              mean_times.max() ])
        semilogy(h._norm_log2_dims, mean_times[:,_HAD_FAUST], lw=line_width)
        semilogy(h._norm_log2_dims, mean_times[:,_HAD_DENSE], lw=line_width)
        legend(['Faust','Dense'])
        ylabel('Computed Time (sec)')
        xlabel('log(dim)')
        title('Runtime')

        # speedup
        subplot(132)
        #hold(True)
        grid(True)
        axis([h._norm_log2_dims[0], h._norm_log2_dims[-1],
              min(faust_speedup.min(), rcgs.min(), 1),
              max(faust_speedup.max(), rcgs.max(), 1)])
        semilogy(h._norm_log2_dims, faust_speedup, lw=line_width)
        semilogy(h._norm_log2_dims, rcgs, lw=line_width)
        semilogy(h._norm_log2_dims, ones(len(_dims)), lw=line_width, c='black')
        ylabel('Speedup')
        xlabel('log(dim)')
        legend(['Faust', 'Theoritical', 'Neutral'])
        title("Speedup norm(A)")

        # errors
        subplot(133)
        #hold(True)
        grid(True)
        #indices = find(norm_errs[_HAD_DENSE,:]>0)
        indices = range(0,len(h._norm_log2_dims))
        plot(h._norm_log2_dims[indices], norm_errs[_HAD_DENSE, indices],
             lw=line_width)
        #indices = find(norm_errs[_HAD_FAUST,:]>0)
        plot(h._norm_log2_dims[indices], norm_errs[_HAD_FAUST, indices],"r^-",
             lw=line_width)
        axis([h._norm_log2_dims[0], h._norm_log2_dims[-1],
              norm_errs.min(),
              norm_errs.max()])
        legend(['Faust', 'Dense'])
        ylabel('error')
        xlabel('log(dim)')
        title('Error')

        _write_fig_in_file(output_dir, hadamard._fig_norm, figure(1))




        show(block=False)

    @staticmethod
    def figs(input_dir=DEFT_RESULTS_DIR, output_dir=DEFT_FIG_DIR):
        """
        Calls all hadamard.fig_* functions in a row.
        """
        h = hadamard
        h.fig_norm_hadamard(input_dir, output_dir)
        h.fig_fact(input_dir, output_dir)
        h.fig_speedup_hadamard()

class bsl:
    """
        Brain Source Localization demo.
    """

    _speedup_fig_fname = 'BSL-speed_up_omp_solver.png'
    _time_cmp_fig_fname = 'BSL-runtime_comparison_omp_solver.png'
    _convergence_fig_fname = 'BSL-convergence_Cpp_omp_solver.png'

    @staticmethod
    def sparse_coeffs(D, ntraining, sparsity):
        """Generates sparse coefficients.
        Gamma = sparse_coeffs(D, ntraining, sparsity) generates ntraining sparse
        vectors stacked in a matrix Gamma.

        Each sparse vector is of size the number of atoms in the dictionary D,
        its support is drawn uniformly at
        random and each non-zero entry is iid Gaussian.

          References:
              [1] Le Magoarou L. and Gribonval R., "Learning computationally efficient
              dictionaries and their implementation as fast transforms", submitted to
              NIPS 2014
        """
        natoms = D.shape[1]
        gamma = zeros((natoms, ntraining))
        for i in range(0, ntraining):
            r = randn(sparsity, 1)
            pos_temp = permutation(natoms)
            pos = pos_temp[0:sparsity]
            gamma[pos,i:i+1] = r
        return gamma

    @staticmethod
    def run(input_data_dir=get_data_dirpath(silent=False),
            output_dir=DEFT_RESULTS_DIR, on_gpu=False):
        """This function performs brain source localization.
        It uses several gain matrices [2], including FAuSTs, and OMP solver.
        It reproduces the source localization experiment of [1].
        The results are stored in output_dir+"results_BSL_user.mat".

        Args:
            on_gpu: if True the demo is ran on GPU (if cuda backend is
            available).

        DURATION:
            Computations should take around 3 minutes.

        The MEG gain matrices used are the precomputed ones in
        get_data_dirpath()+"/faust_MEG_rcg_X.mat"
        (in the installation directory of the FAuST toolbox)

            References:

                [1] Le Magoarou L. and Gribonval R., "Flexible multi-layer
                sparse approximations of matrices and applications", Journal of
                Selected Topics in Signal Processing, 2016.
                https://hal.archives-ouvertes.fr/hal-01167948v1

                [2] A. Gramfort, M. Luessi, E. Larson, D. Engemann, D.
                Strohmeier, C. Brodbeck, L. Parkkonen, M. Hamalainen, MNE
                software for processing MEG and EEG data
                http://www.ncbi.nlm.nih.gov/pubmed/24161808, NeuroImage, Volume
                86, 1 February 2014, Pages 446-460, ISSN 1053-8119
        """
        from pyfaust import Faust
        from scipy.io import loadmat,savemat
        from pyfaust.tools import greed_omp_chol
        MEG_Faust_filenames = [
            'faust_MEG_rcg_6.mat','faust_MEG_rcg_8.mat','faust_MEG_rcg_16.mat','faust_MEG_rcg_25.mat']
        num_MEG_Fausts = len(MEG_Faust_filenames)
        num_MEGs = num_MEG_Fausts + 1 # MEG Faust approximations + MEG original matrix
        MEG_Fausts = []
        MEG_Faust_rcgs = []
        MEGs = []

        MEG_matrix = loadmat(input_data_dir+os.sep+'matrix_MEG.mat')['matrix']
        # print(MEG_matrix.shape, type(MEG_matrix))
        # normalize the matrix through a Faust
        MEG_matrix = Faust(MEG_matrix).T.normalize(2).toarray()
        points = loadmat(input_data_dir+os.sep+'matrix_MEG.mat')['points']
        MEGs.append(matrix(MEG_matrix))


        #print(MEG_matrix)

        for filename in MEG_Faust_filenames:
            scale = loadmat(input_data_dir+os.sep+filename)['lambda'][0,0]
            facts = loadmat(input_data_dir+os.sep+filename)['facts']
            # convert facts to a list (it was a ndarray of sparse mats)
            facts = [facts[0,i] for i in range(facts.shape[1]) ]
            MEG_Fausts.append(Faust(facts, scale=scale).normalize(2))
            MEG_Faust_rcgs.append(MEG_Fausts[-1].rcg())
            # print(MEG_Fausts[-1].shape)
            # input()
            if(on_gpu):
              MEG_Fausts[-1].m_faust.set_Fv_mul_mode(10)
            MEGs.append(MEG_Fausts[-1])

        M = MEG_matrix.shape[1] # number of points used in the MEG matrix
        Ntraining = 500 # number of trainings
        sparsity = 2 # number of sources per training vector
        dist_paliers = [0.01,0.05,0.08,0.5]

        resDist = zeros((num_MEGs, len(dist_paliers)-1, sparsity, Ntraining))
        compute_times = zeros((num_MEGs, len(dist_paliers)-1, Ntraining))

        for k in range(0,len(dist_paliers)-1):
            # parameter settings
            # generates the different source positions
            gamma = zeros((M,Ntraining))
            for j in range(0,Ntraining):
                dist_sources = -1
                while not (dist_paliers[k] < dist_sources and dist_sources <
                           dist_paliers[k+1]):
                    gamma[:,j:j+1] = bsl.sparse_coeffs(MEG_matrix, 1, sparsity)
                    #idx = find(gamma[:,j])
                    idx = nonzero(ravel(gamma[:,j]))[0]
                    dist_sources = norm(points[idx[0],:] - points[idx[1],:])

            # compute the data registered by MEG sensor
            data = MEG_matrix.dot(gamma)
#            print("data.shape=", data.shape)
#            print("gamma.shape=", gamma.shape)
#            print("MEG_matrix.shape=", MEG_matrix.shape)
            for i in range(0,Ntraining):
                print("Brain Source Localization : MEG matrix and its faust "
                  "approximations with omp solver, progress:",
                      100*(k*Ntraining+i)/(len(dist_paliers)-1)/Ntraining)
                # index of the real source localization
                # idx = find(gamma[:,i])
                idx = nonzero(ravel(gamma[:,i]))[0]
                for j in range(0,num_MEGs):

                    MEG = MEGs[j]

                    #find active source
                    t = _timer()
                    #print(matrix(data[:,i:i+1]).shape,  MEG.shape, M)
                    n = max(matrix(data[:,i:i+1]).shape)
                    solver_sol = greed_omp_chol(matrix(data[:,i:i+1]), MEG,
                                                maxiter=sparsity,
                                                tol=10**-8*np.sqrt(n),
                                                relerr=False,
                                                verbose=False)
                    # about tol: it's the square root of 10**-16 (because
                    # the square of tol is used into greed_omp_chol) 
                    compute_times[j,k,i] = _timer() - t
                    # compute the disntance between estimated source and the
                    # real one
                    solver_idx = solver_sol.nonzero()
                    # print("solver_idx=", solver_idx)
                    # input()
                    resDist[j,k,0,i] = min(norm(points[idx[0],:] -
                                                points[solver_idx[0][0],:], 2),norm(points[idx[0],:]
                                                                              - points[solver_idx[0][1],:],
                                                                                   2));
                    resDist[j,k,1,i] = min(norm(points[idx[1],:] -
                                                points[solver_idx[0][0],:],2),norm(points[idx[1],:]
                                                                              - points[solver_idx[0][1],:],2));


        _create_dir_if_doesnt_exist(output_dir)
        # keep matlab demo version names for mat file
        savemat(output_dir+os.sep+"results_BSL_user.mat", { 'resDist' :
                                                           resDist, 'Sparsity'
                                                           : np.float(sparsity),
                                                           'RCG_list' :
                                                           array(MEG_Faust_rcgs),
                                                           'compute_Times':
                                                           compute_times,
                                                           'Ntraining':
                                                           np.float(Ntraining),
                                                           'nb_MEG_matrix':
                                                           np.float(len(MEGs))})

    @staticmethod
    def fig(input_dir=DEFT_RESULTS_DIR, output_dir=DEFT_FIG_DIR):
        """Calls all fig*() functions of bsl demo.
        Note: Must be call after the bsl.run function.
        """
        bsl.fig_time_cmp(input_dir, output_dir)
        bsl.fig_speedup(input_dir, output_dir)
        bsl.fig_convergence(input_dir, output_dir)

    @staticmethod
    def fig_time_cmp(input_dir=DEFT_RESULTS_DIR, output_dir=DEFT_FIG_DIR,
                     use_precomputed_data=False):
        """
            Builds the time comparison figure for the BSL with the differents Faust representations of the MEG matrix.
        """
        from scipy.io import loadmat
        if(use_precomputed_data):
            mat_file_entries = \
            loadmat(os.path.join(get_data_dirpath(silent=False),"results_BSL_user.mat"))
        else:
            mat_file_entries = loadmat(input_dir+os.sep+'results_BSL_user.mat')
        compute_times = mat_file_entries['compute_Times']
        RCG_list = mat_file_entries['RCG_list']

        #times = [squeeze(compute_times[i,:,:]*1000) for i in
        #         range(0,compute_times.shape[0])] # in ms
        times = \
            [squeeze(compute_times[i,:,:]*1000).reshape(compute_times.shape[1]*compute_times.shape[2])
                \
             for i in range(0,compute_times.shape[0])]
        fig = figure()
        boxplot(times, showfliers=False)
        plt.rc('text', usetex=True)
        #plt.rcParams['figure.figsize'] = [12.0, 8]
        plt.rc('figure', figsize=[12.0, 8])
        minY = min(yticks()[0])
        text(xticks()[0][0], minY,
             '${\mathbf{M}}$',
             horizontalalignment='center', verticalalignment='baseline')


        for i in range(1,len(times)):
            text(xticks()[0][i], minY,
                 '$\widehat{\mathbf{M}}_{'+str(int(round(RCG_list[0][i-1])))+'}$',
                horizontalalignment='center', verticalalignment='baseline')

        legend()
        xticks([])
        ylabel("Computed Time (ms)")
        title("BSL - time comparison (FAUST vs dense matrix) omp solver")

        _write_fig_in_file(output_dir, bsl._time_cmp_fig_fname, fig)

        show(block=False)

    @staticmethod
    def fig_speedup(input_dir=DEFT_RESULTS_DIR, output_dir=DEFT_FIG_DIR):
        """
            Builds the speedup comparison figure for the BSL with the differents Faust representations of the MEG matrix.
        """
#        Ntraining          1x1                       8  double
#        RCG_list           1x4                      32  double
#        Sparsity           1x1                       8  double
#        compute_Times      5x3x500               60000  double
#        nb_MEG_matrix      1x1                       8  double
#        resDist            5x3x2x500            120000  double
        from scipy.io import loadmat
        mat_file_entries = loadmat(input_dir+os.sep+'results_BSL_user.mat')
        compute_times = mat_file_entries['compute_Times']
        RCG_list = mat_file_entries['RCG_list']

        #times = concatenate((compute_times[:,0,:], compute_times[:,1,:],
        #                    compute_times[:,2,:]), axis=0)
        mean_times = compute_times.mean(axis=1)
        mean_times = mean_times.mean(axis=1)
        dense_matrix_time = mean_times[0]
        real_RCGs = dense_matrix_time/mean_times
        fig = figure()
        plot(arange(0,mean_times.shape[0]-1), real_RCGs[1:], lw=1.5)
        #hold(True)
        plot(arange(0,mean_times.shape[0]-1), ones((mean_times.shape[0]-1)),
            lw=1.5)
        legend(["speed up FAuST", "neutral speed up"])
        title("BSL -speed up using FAUST OMP solver")
        minY = min(min(real_RCGs[1:]), .9)
        maxY = max(max(real_RCGs[1:]), .9)
        xticks([])
        #tight_layout()
        plt.rc('text', usetex=True)
        #plt.rcParams['figure.figsize'] = [12.0, 8]
        plt.rc('figure', figsize=[12.0, 8])
        for i in range(0,len(real_RCGs)-1):
            text(i, minY - (maxY-minY)/20,
                 '$\widehat{\mathbf{M}}_{'+str(int(round(RCG_list[0][i])))+'}$',
                horizontalalignment='center', verticalalignment='top')

        _write_fig_in_file(output_dir, bsl._speedup_fig_fname, fig)

        show(block=False)

        print("**** MEG with OMP solver time comparison ****")
        print("M time:", mean_times[0]*1000)
        for i in range(1,mean_times.shape[0]):
            print('M_'+str(int(round(RCG_list[0][i-1]))),'time:',
                  mean_times[i]*1000,'ms', 'speedup: ',
                  real_RCGs[i])

    @staticmethod
    def fig_convergence(input_dir=DEFT_RESULTS_DIR, output_dir=DEFT_FIG_DIR):
        """This function builds a figure similar to the BSL figure (Fig 9) used in [1].

        References:
            [1] Le Magoarou L. and Gribonval R., "Flexible multi-layer sparse
            approximations of matrices and applications", Journal of Selected
            Topics in Signal Processing, 2016.
            https://hal.archives-ouvertes.fr/hal-01167948v1 
        """
#        Ntraining          1x1                       8  double
#        RCG_list           1x4                      32  double
#        Sparsity           1x1                       8  double
#        compute_Times      5x3x500               60000  double
#        nb_MEG_matrix      1x1                       8  double
#        resDist            5x3x2x500            120000  double
        from scipy.io import loadmat
        mat_file_entries = loadmat(input_dir+os.sep+'results_BSL_user.mat')
        res_dist = mat_file_entries['resDist']
        Ntraining = mat_file_entries['Ntraining'][0,0]
        sparsity = mat_file_entries['Sparsity'][0,0]
        RCG_list = mat_file_entries['RCG_list']
        ntest = Ntraining*sparsity

        plt.rc('figure', figsize=[12.0, 8])
        plt.rc('text', usetex=True)
        d = []
        test2 = []
        for i in range(0,3):
            d.append([])
            for j in range(0,res_dist.shape[0]):
                test2.append(100*np.concatenate((res_dist[j,i,0,:],
                                             res_dist[j,i,1,:]), axis=0))
            #test2.append(squeeze(d[-1]))
            if(i < 2):
                test2.append(zeros(1,ntest))

        fig = figure()
        print(len(test2))
        T = boxplot(test2, showfliers=False)
        #legend(T['means'])
        plt.rc('figure', figsize=[12.0, 8])
        for j in range(0,3):
            text(xticks()[0][res_dist.shape[0]*j+j], min(yticks()[0]),
                 '${\mathbf{M}}$',
                 horizontalalignment='center', verticalalignment='bottom')

            for i in range(1,res_dist.shape[0]):
                text(xticks()[0][j*res_dist.shape[0]+i+j], min(yticks()[0]),
                     '$\widehat{\mathbf{M}}_{'+str(int(round(RCG_list[0][i-1])))+'}$',
                     horizontalalignment='center', verticalalignment='bottom')

        xticks(xticks()[0], ['' for i in range(xticks()[0].shape[0])])

        ylabel("Distance between true and estimated sources (cm)")
        title("BSL - convergence (C++ wrapper faust) omp solver")

        show(block=False)
        _write_fig_in_file(output_dir, bsl._convergence_fig_fname, fig)




def _write_array_in_file(output_dir, fname, array):
    """
    output_dir: directory folder created if doesn't exist.
    fname: output file in output_dir.
    array: the numpy ndarray is flattened before saving. (N-D to 1D). You need
    to keep the dimensions to read-reshape to original array.
    """
    _create_dir_if_doesnt_exist(output_dir)
    fpath = _prefix_fname_with_dir(output_dir, fname)
    savetxt(fpath, array.reshape(array.size))
    return fpath

def _write_fig_in_file(output_dir, fname, fig, dpi=200):
    """
    output_path: directory folder created if doesn't exist.
    fname: output file in output_dir.
    fig: the figure to save.
    """
    _create_dir_if_doesnt_exist(output_dir)
    fpath = _prefix_fname_with_dir(output_dir, fname)
    if(not isinstance(fig, Figure)):
        raise Exception("fig must be a Figure object")
    fig.savefig(fpath,dpi=dpi)

def _prefix_fname_with_dir(dir, fname):
    import os.path
    return dir+os.sep+fname

def _create_dir_if_doesnt_exist(output_dir):
    import os.path
    if(not os.path.exists(output_dir)):
        os.mkdir(output_dir)

# time comparison function to use
from time import time, process_time
if sys.platform == 'win32':
    _timer = process_time
else:
    _timer = time
