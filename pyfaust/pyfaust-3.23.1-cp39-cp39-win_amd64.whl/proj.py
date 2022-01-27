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

## @package pyfaust.proj @brief This module provides matrix projectors.
import _FaustCorePy
from pyfaust.factparams import *
from abc import ABC, abstractmethod

from pyfaust.fact import _check_fact_mat

class proj_gen(ABC):
    """
    The parent abstract class to represent projectors (as functors).
    """
    @abstractmethod
    def __init__(self):
        pass

    def __call__(self, M):
        return self.constraint.project(M)

class toeplitz(proj_gen):
    """
    Functor for the TOEPLITZ projector.

    Example:
    >>> from pyfaust.proj import toeplitz
    >>> from numpy.random import rand
    >>> M = rand(5,5)
    >>> p = toeplitz(M.shape)
    >>> p(M)
    array([[ 0.38925701,  0.89077942,  0.43467682,  0.68566158,  0.29709396],
           [ 0.62199717,  0.38925701,  0.89077942,  0.43467682, 0.68566158],
           [ 0.29650327,  0.62199717,  0.38925701,  0.89077942, 0.43467682],
           [ 0.65125443,  0.29650327,  0.62199717,  0.38925701, 0.89077942],
           [ 0.35021359,  0.65125443,  0.29650327,  0.62199717, 0.38925701]])

    """
    def __init__(self, shape, normalized=False, pos=False):
        """
        Args:
            shape: the size of the input matrix.
            normalized: True to normalize the projection image according to its Frobenius norm.
            pos: True to skip negative values (replaced by zero) of the matrix to project.
        """

        self.constraint = ConstraintMat('toeplitz', np.empty(shape), normalized, pos)

class circ(proj_gen):
    """
    Functor for the CIRC(ulant) projector.


    Example:
        >>> from pyfaust.proj import circ
        >>> from numpy.random import rand
        >>> M = rand(5,5)
        >>> circ(M.shape)
        >>> p = circ(M.shape)
        >>> p(M)
        array([[ 0.58798272,  0.65139062,  0.56169998,  0.4051127 , 0.47563316],
               [ 0.47563316,  0.58798272,  0.65139062,  0.56169998, 0.4051127 ],
               [ 0.4051127 ,  0.47563316,  0.58798272,  0.65139062, 0.56169998],
               [ 0.56169998,  0.4051127 ,  0.47563316,  0.58798272, 0.65139062],
               [ 0.65139062,  0.56169998,  0.4051127 ,  0.47563316, 0.58798272]])

    """
    def __init__(self, shape, normalized=False, pos=False):
        """
        Args:
            shape: the size of the input matrix.
            normalized: True to normalize the projection image according to its Frobenius norm.
            pos: True to skip negative values (replaced by zero) of the matrix to project.


        """
        self.constraint = ConstraintMat('circ', np.empty(shape), normalized, pos)

class hankel(proj_gen):
    """
    Functor for the HANKEL projector.

    Example:
        >>> from pyfaust.proj import hankel
        >>> from numpy.random import rand
        >>> M = rand(5,5)
        >>> p = hankel(M.shape)
        >>> p(M)
        array([[ 0.00854525,  0.41578004,  0.54722872,  0.31191184, 0.74059554],
               [ 0.41578004,  0.54722872,  0.31191184,  0.74059554, 0.46299776],
               [ 0.54722872,  0.31191184,  0.74059554,  0.46299776, 0.50574944],
               [ 0.31191184,  0.74059554,  0.46299776,  0.50574944, 0.4539859 ],
               [ 0.74059554,  0.46299776,  0.50574944,  0.4539859 , 0.81595711]])

    """
    def __init__(self, shape, normalized=False, pos=False):
        """
        Args:
            shape: the size of the input matrix.
            normalized: True to normalize the projection image according to its Frobenius norm.
            pos: True to skip negative values (replaced by zero) of the matrix to project.
        """

        self.constraint = ConstraintMat('hankel', np.empty(shape), normalized, pos)


class sp(proj_gen):
    """
    Functor for the SP projector.

    A, the image matrix, is such that \f$ \| A \|_0 = k,  \| A\|_F = 1 \f$ (if normalized == True).


    Example:
        >>> from pyfaust.proj import sp
        >>> from numpy.random import rand
        >>> M = rand(5,5)
        >>> p = sp(M.shape, 3)
        >>> p(M)
        array([[ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ],
               [ 0.        ,  0.        ,  0.        ,  0.        ,  0.
               ],
               [ 0.        ,  0.        ,  0.        ,  0.        ,  0.
               ],
               [ 0.57513065,  0.        ,  0.        ,  0.58444931,  0.
               ],
               [ 0.57240172,  0.        ,  0.        ,  0.        ,  0.
               ]])

    """

    def __init__(self, shape, k, normalized=False, pos=False):
        """

        Args:
            k: the number of nonzeros of the projection image.
            normalized: True to normalize the projection image according to its Frobenius norm.
            pos: True to skip negative values (replaced by zero) of the matrix to project.

        """
        self.constraint = ConstraintInt('sp', shape[0], shape[1], k, normalized, pos)

class splin(proj_gen):
    """
    Functor for the SPLIN projector.

    A, the image matrix, is defined by \f$
    \forall i \in \{0,...,shape[0]-1\} \| \f$ the i-th row \f$ A_{i,*}\f$ is
    such that \f$ \| A_{i,*}\|_0 = k,  \| A\|_F = 1\f$ (if normalized == True).


    Example:
        >>> from pyfaust.proj import splin
        >>> from numpy.random import rand
        >>> M = rand(5,5)
        >>> p = sp(M.shape, 3)
        >>> p(M)
        array([[ 0.15336612,  0.25445984,  0.        ,  0.        ,0.25009889],
               [ 0.        ,  0.        ,  0.22222948,  0.37763972, 0.        ],
               [ 0.33240149,  0.16788946,  0.32267917,  0.25270611,0.24133112],
               [ 0.10634037,  0.        ,  0.22578806,  0.        ,0.26885935],
               [ 0.        ,  0.31022779,  0.        ,  0.2479237 , 0.        ]])

    """
    def __init__(self, shape, k, normalized=False, pos=False):
        """
        Args:
            k: the number of nonzeros of the projection image.
            normalized: True to normalize the projection image according to its Frobenius norm.
            pos: True to skip negative values (replaced by zero) of the matrix to project.

        """
        self.constraint = ConstraintInt('splin', shape[0], shape[1], k, normalized, pos)

class spcol(proj_gen):
    """
    Functor for the SPCOL projector. A, the image matrix, is defined by \f$ \forall j \in \{0,...,shape[1]-1\} \f$ the j-th column \f$ A_{*,j}\f$ is such that \f$ \| A_{*,j}\|_0 = k,  \| A\|_F = 1 (if normalized == True)\f$.

    Example:
        >>> from pyfaust.proj import spcol
        >>> from numpy.random import rand
        >>> M = rand(5,5)
        >>> p = spcol(M.shape, 3)
        >>> p(M)
        array([[ 0.15336612,  0.25445984,  0.        ,  0.        ,0.25009889],
               [ 0.        ,  0.        ,  0.22222948,  0.37763972, 0.        ],
               [ 0.33240149,  0.16788946,  0.32267917,  0.25270611,0.24133112],
               [ 0.10634037,  0.        ,  0.22578806,  0.        ,0.26885935],
               [ 0.        ,  0.31022779,  0.        ,  0.2479237 , 0.        ]])


    """
    def __init__(self, shape, k, normalized=False, pos=False):
        """

        Args:
            S: the support matrix.
            normalized: True to normalize the projection image according to its Frobenius norm.
            pos: True to skip negative values (replaced by zero) of the matrix to project.

        """
        self.constraint = ConstraintInt('spcol', shape[0], shape[1], k, normalized, pos)

class splincol(proj_gen):
    """
    Functor for the SPLINCOL projector.

    It's the union of SPLIN and SPCOL projectors.

    Example:
        >>> from pyfaust.proj import splincol
        >>> from numpy.random import rand
        >>> M = rand(5,5)
        >>> p1 = splin(M.shape, 3)
        >>> p2 = spcol(M.shape, 3)
        >>> p = splincol(M.shape, 3)
        >>> p1(M)
        array([[ 0.        ,  0.73732727,  0.76317487,  0.        , 0.95740247],
               [ 0.45374662,  0.7458585 ,  0.        ,  0.        , 0.25951363],
               [ 0.        ,  0.42327175,  0.        ,  0.47653549, 0.26252904],
               [ 0.81674889,  0.74824695,  0.        ,  0.        , 0.68645765],
               [ 0.67261832,  0.60062852,  0.        ,  0.39818073,  0.
               ]])
        >>> p2(M)
        array([[ 0.        ,  0.73732727,  0.76317487,  0.43095515, 0.95740247],
               [ 0.45374662,  0.7458585 ,  0.20794305,  0.        ,  0.  ],
               [ 0.        ,  0.        ,  0.        ,  0.47653549, 0.26252904],
               [ 0.81674889,  0.74824695,  0.18272054,  0.        , 0.68645765],
               [ 0.67261832,  0.        ,  0.        ,  0.39818073,  0.  ]])
        >>> p(M)
        array([[ 0.        ,  0.73732727,  0.76317487,  0.43095515, 0.95740247],
               [ 0.45374662,  0.7458585 ,  0.20794305,  0.        , 0.25951363],
               [ 0.        ,  0.42327175,  0.        ,  0.47653549, 0.26252904],
               [ 0.81674889,  0.74824695,  0.18272054,  0.        , 0.68645765],
               [ 0.67261832,  0.60062852,  0.        ,  0.39818073,  0.
               ]])
        >>> p1M = p1(M)
        >>> p2M = p2(M)
        >>> p1M[p1M == p2M] = 0
        >>> p1M+p2M
        array([[ 0.        ,  0.73732727,  0.76317487,  0.43095515, 0.95740247],
               [ 0.45374662,  0.7458585 ,  0.20794305,  0.        , 0.25951363],
               [ 0.        ,  0.42327175,  0.        ,  0.47653549, 0.26252904],
               [ 0.81674889,  0.74824695,  0.18272054,  0.        , 0.68645765],
               [ 0.67261832,  0.60062852,  0.        ,  0.39818073,  0.  ]])
        >>> (p1M+p2M == p(M)).all()
        True
    """
    def __init__(self, shape, k, normalized=False, pos=False):
        """

        Args:
            k: the integer sparsity (number of nonzeros) targeted per-row and
            per-column.
            normalized: True to normalize the projection image according to its Frobenius norm.
            pos: True to skip negative values (replaced by zero) of the matrix to project.

        """
        self.constraint = ConstraintInt('splincol', shape[0], shape[1], k, normalized, pos)

class supp(proj_gen):
    """
        Functor for the SUPP projector. A, the image matrix, is such that np.nonzero(A) == np.nonzero(S).

        Example:
            >>> from pyfaust.proj import supp
            >>> from numpy.random import rand
            >>> from numpy import zeros
            >>> M = rand(5,5)
            >>> S = zeros((5,5))
            >>> S[M>.5] = 1
            >>> p = supp(S)
            >>> M
            array([[ 0.        ,  0.        ,  0.22763947,  0.35813742,
                    0.32570465],
                   [ 0.        ,  0.33306546,  0.        ,  0.        ,
                    0.        ],
                   [ 0.2284932 ,  0.        ,  0.        ,  0.        ,
                    0.38999188],
                   [ 0.24800284,  0.29485492,  0.24955369,  0.28659952,
                    0.        ],
                   [ 0.        ,  0.        ,  0.        ,  0.32517346,
                    0.        ]])
            >>> p(M)
            array([[ 0.,  0.,  1.,  1.,  1.],
                   [ 0.,  1.,  0.,  0.,  0.],
                   [ 1.,  0.,  0.,  0.,  1.],
                   [ 1.,  1.,  1.,  1.,  0.],
                   [ 0.,  0.,  0.,  1.,  0.]])

    """
    def __init__(self, S, normalized=False, pos=False):
        """

        Args:
            S: the support matrix.
            normalized: True to normalize the projection image according to its Frobenius norm.
            pos: True to skip negative values (replaced by zero) of the matrix to project.
        """
        self.constraint = ConstraintMat('supp', S, normalized, pos)

class const(proj_gen):
    """
        Functor for the CONST projector. A, the image matrix, is such that A == C.

        Example:
            >>> from pyfaust.proj import const
            >>> from numpy.random import rand
            >>> M = rand(5,5)
            >>> C = rand(5,5)
            >>> p = const(C)
            >>> C
            array([[ 0.62642491,  0.76480497,  0.1401435 ,  0.88598704,
                    0.05882356],
                   [ 0.54101377,  0.49137532,  0.72109984,  0.08346243,
                    0.91622991],
                   [ 0.20559201,  0.24064159,  0.57447222,  0.7184664 ,
                    0.61717141],
                   [ 0.19869533,  0.29402892,  0.04731566,  0.29117326,
                    0.20695774],
                   [ 0.67846268,  0.28522381,  0.89401783,  0.09240229,
                    0.81469085]])
            >>> M
            array([[ 0.8379613 ,  0.38696355,  0.36753559,  0.82832917,
                    0.44945077],
                   [ 0.18825132,  0.38174789,  0.1552487 ,  0.18795349,
                    0.16286817],
                   [ 0.66470399,  0.37575792,  0.43372606,  0.10168977,
                    0.25626987],
                   [ 0.64667378,  0.12663425,  0.80530654,  0.86820131,
                    0.69952691],
                   [ 0.82429298,  0.21722392,  0.77599932,  0.76112641,
                    0.38104096]])
            >>> p(M)
            array([[ 0.62642491,  0.76480497,  0.1401435 ,  0.88598704,
                    0.05882356],
                   [ 0.54101377,  0.49137532,  0.72109984,  0.08346243,
                    0.91622991],
                   [ 0.20559201,  0.24064159,  0.57447222,  0.7184664 ,
                    0.61717141],
                   [ 0.19869533,  0.29402892,  0.04731566,  0.29117326,
                    0.20695774],
                   [ 0.67846268,  0.28522381,  0.89401783,  0.09240229,
                    0.81469085]])

    """
    def __init__(self, C, normalized=False):
        """

        Args:
            C: the constant matrix.
            normalized: True to normalize the projection image according to its Frobenius norm.
            pos: True to skip negative values (replaced by zero) of the matrix to project.

        """
        self.constraint = ConstraintMat('const', C, normalized, pos=False)

class normcol(proj_gen):
    """
        Functor for the NORMCOL projector. A, the image matrix, is defined by \f$ \forall j \in \{0,...,shape[1]-1\} \f$ the j-th column \f$ A_{*,j} \f$ is such that \f$\| A_{*,j}\|_2 = s  \f$.

    """
    def __init__(self, shape, s=1):
        """
        Args:
            shape: the input matrix shape.
            s: the column 2-norm (default to 1).

        Example:
            >>> from pyfaust.proj import normcol
            >>> from numpy.random import rand
            >>> from numpy.linalg import norm
            >>> M = rand(5,5)
            >>> p = normcol(M.shape, .01)
            >>> norm(p(M)[:,0], 2)
            0.01
        """
        if(s < 0):
            raise ValueError('A norm can\'t be negative')
        normalized=False
        pos=False
        self.constraint = ConstraintReal('normcol', shape[0], shape[1], s, normalized, pos)

class normlin(proj_gen):
    """
        Functor for the NORMLIN projector. A, the image matrix, is defined by \f$ \forall i \in \{0,...,shape[0]-1\}\f$ the i-th row \f$ A_{i,*} \f$ is such that \f$ \| A_{i,*} \|_2 = s \f$.

        Example:
            >>> from pyfaust.proj import normlin
            >>> from numpy.random import rand
            >>> from numpy.linalg import norm
            >>> M = rand(5,5)
            >>> p = normlin(M.shape, .01)
            >>> p(M)
            array([[ 0.00107735,  0.00332753,  0.00522087,  0.00518604,  0.00579779],
                   [ 0.00191403,  0.00506089,  0.00570792,  0.00088102,  0.00611288],
                   [ 0.00058959,  0.00136085,  0.00241409,  0.00280571,  0.00917064],
                   [ 0.00530324,  0.00616326,  0.00218585,  0.00347406,  0.00412831],
                   [ 0.00636684,  0.005042  ,  0.00023021,  0.00218801,  0.00540381]])
            >>> norm(p(M)[0,:], 2)
            0.01
    """

    def __init__(self, shape, s=1):
        """
        Args:
            shape: the input matrix shape.
            s: the row 2-norm (default to 1).

        """
        if(s < 0):
            raise ValueError('A norm can\'t be negative')
        normalized=False
        pos=False
        self.constraint = ConstraintReal('normlin', shape[0], shape[1], s, normalized, pos)

class blockdiag(proj_gen):
    """
	Functor for the BLOCKDIAG projector. It sets all values to zero except for the diagonal blocks of the support defined by block_shapes. The i-th diagonal block starts at the row and column indices (block_shapes[i-1][0], block_shapes[i-1][1]) or (0,0) if i == 0 and ends at the row and columns indices (block_shapes[i][0]-1, block_shapes[i][1]-1) or (shape[0], shape[1]) if i == len(block_shapes)-1. 

        Example:
>>> from pyfaust.proj import blockdiag
>>> from numpy.random import rand
>>> M = rand(15,15)
>>> p = blockdiag(M.shape, [(1,1), (2,2), (3,3), (4,4), (5,5)])
>>> M_ = p(M)
>>> for i in range(M.shape[0]):
>>>     for j in range(M.shape[1]):
>>>         print(("%2.1f" % (M_[i,j])), " ", end='')
>>>     print()
	0.3  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0
	0.0  0.2  0.4  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0
	0.0  0.1  0.9  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0
	0.0  0.0  0.0  0.7  0.9  0.9  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0
	0.0  0.0  0.0  0.8  0.6  0.9  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0
	0.0  0.0  0.0  1.0  0.9  0.4  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0
	0.0  0.0  0.0  0.0  0.0  0.0  0.9  0.2  0.3  0.9  0.0  0.0  0.0  0.0  0.0
	0.0  0.0  0.0  0.0  0.0  0.0  0.2  0.4  1.0  0.3  0.0  0.0  0.0  0.0  0.0
	0.0  0.0  0.0  0.0  0.0  0.0  0.1  0.4  0.9  0.4  0.0  0.0  0.0  0.0  0.0
	0.0  0.0  0.0  0.0  0.0  0.0  0.5  0.1  0.7  0.8  0.0  0.0  0.0  0.0  0.0
	0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.9  0.4  0.1  0.3  0.8
	0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.5  0.6  0.1  0.8  0.6
	0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.6  0.9  0.1  0.1  0.9
	0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.9  0.5  0.2  0.1  0.1
	0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.4  0.1  0.8  0.0  0.4


    """

    def __init__(self, shape, block_shapes, normalized=False, pos=False):
        """
        Constructor.

        Args:
            shape: the size of the input matrix.
            block_shapes: the list of tuples defining the lower right corner of
            successive diagonal blocks (see class description and example).
            normalized: True to normalize the projection image matrix.
            pos: True to ignore negative values (replaced by 0).
        """
        self._m_vec = [ sh[0] for sh in block_shapes ]
        self._n_vec = [ sh[1] for sh in block_shapes ]
        self._shape = shape
        self._block_shapes = block_shapes
        self.normalized = normalized
        self.pos = pos
#        if(self._m_vec[-1] != shape[0]): raise ValueError("The last index of (row"
#                                                    " offsets) _m_vec"
#                                                    " must be equal to"
#                                                    " shape[0]")
#        if(self._n_vec[-1] != shape[1]): raise ValueError("The last index of (column"
#                                                    " offsets) _n_vec"
#                                                    " must be equal to"
#                                                    " shape[1]")
        cons_value = np.asfortranarray(np.array(block_shapes, dtype=float))
        self.constraint = ConstraintMat('blockdiag', cons_value,
                                        normalized, pos,
                                        cons_value.size)

    def __call__(self, M):
        """
        Implements the functor.
        """
        if(M.shape != self._shape): raise ValueError('The dimension of the '
                                                   'projector and matrix must '
                                                   'agree.')

        is_real = np.empty((1,))
        M = _check_fact_mat('prox_blockdiag.__call__', M, is_real)
        if is_real:
            is_float = M.dtype == 'float32'
            if is_float:
                return _FaustCorePy.ConstraintMatCoreFlt.prox_blockdiag(M, self._block_shapes, self.normalized,
                                                                        self.pos)
            else:
                return _FaustCorePy.ConstraintMatCoreDbl.prox_blockdiag(M, self._block_shapes, self.normalized,
                                                                        self.pos)

        else:
            return _FaustCorePy.ConstraintMatCoreCplxDbl.prox_blockdiag(M, self._block_shapes, self.normalized,
                                                             self.pos)

#        M_ = np.zeros(M.shape)
#        m_ = 0
#        n_ = 0
#        for i,(m,n) in enumerate(zip(self.m_vec, self.n_vec)):
#            print("i=", i, "m=", m, "n=", n)
#            M_[m_:m,n_:n] = M[m_:m,n_:n]
#            m_ = m
#            n_ = n
#        return M_

class skperm(proj_gen):
    """
    Functor for the SKPERM projector.

    Example:
	>>> from pyfaust.proj import skperm
	>>> from numpy.random import rand
	>>> import numpy as np
	>>> from numpy import array
	>>>
	>>> k = 2
	>>> if len(sys.argv) > 1:
	>>>     k = int(sys.argv[1])
	>>>
	>>> M = array([[-0.04440802, -0.17569296, -0.02557815, -0.15559154],
	>>>             [-0.0083095,  -3.38725936, -0.78484126, -0.4883618 ],
	>>>             [-1.48942563, -1.71787215, -0.84000212, -3.71752454],
	>>>             [-0.88957883, -0.19107863, -5.92900636, -6.51064175]])
	>>> p = skperm(M.shape, k)
	>>> print(p(M))
	[[-0.04440802  0.         -0.02557815  0.        ]
	 [-0.0083095  -3.38725936  0.          0.        ]
	 [ 0.         -1.71787215  0.         -3.71752454]
	 [ 0.          0.         -5.92900636 -6.51064175]]
    """
    def __init__(self, shape, k, normalized=False, pos=False):
        """
        Projector constructor.

        Args:
            k: the integer sparsity (number of nonzeros) targeted per-row and
            per-column.
            normalized: True to normalize the projection image according to its Frobenius norm.
            pos: True to skip negative values (replaced by zero) of the matrix to project.

        """
        self.constraint = ConstraintInt('skperm', shape[0], shape[1], k, normalized, pos)

