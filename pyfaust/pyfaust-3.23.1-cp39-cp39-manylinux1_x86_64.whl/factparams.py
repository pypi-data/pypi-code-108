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

from pyfaust import *
import numpy as np
import _FaustCorePy
import sys
from abc import ABC, abstractmethod
from warnings import warn


## @package pyfaust.factparams @brief The module for the parametrization of FAuST's algorithms (Palm4MSA and Hierarchical Factorization).
##  See also: pyfaust.fact.hierarchical, pyfaust.fact.palm4msa

"""
    This module provides all the classes that represent the input parameters needed
    by factorization algorithms pyfaust.fact.palm4msa()
    pyfaust.fact.hierarchical()
"""

class StoppingCriterion(object):
    """
        This class defines a StoppingCriterion for PALM4MSA algorithms.

        A stopping criterion can be of two kinds:
            - number of iterations,
            - error threshold.

        Attributes:
            num_its: see pyfaust.factparams.StoppingCriterion.__init__.
            maxiter: see pyfaust.factparams.StoppingCriterion.__init__.
            relerr: see pyfaust.factparams.StoppingCriterion.__init__.
            relmat: see pyfaust.factparams.StoppingCriterion.__init__.
            tol: see pyfaust.factparams.StoppingCriterion.__init__.
    """
    DEFAULT_MAXITER=10000
    DEFAULT_TOL=0.3
    DEFAULT_NUMITS=500
    def __init__(self, num_its = DEFAULT_NUMITS,
                 tol = None,
                 maxiter = DEFAULT_MAXITER,
                relerr = False, relmat=None):
        """
        Class constructor.

        Args:
            num_its: (optional) the fixed number of iterations of the
            algorithm. By default the value is DEFAULT_NUMITS. The constructor
            will fail if arguments num_its and tol are used together.
            tol: (optional) error target according to the algorithm is stopped.
            The constructor  will fail if arguments num_its and tol are used together.
            maxiter: (optional) The maximum number of iterations to run the algorithm,
            whatever is the criterion used (tol or num_its).
            relerr: (optional) if False the tol error defines an absolute
            error, otherwise it defines a relative error (in this case the
            'relmat' matrix will be used to convert internally the given 'tol'
            value to the corresponding absolute error).
            relmat: (optional) The matrix against which is defined the relative error.
            if relerr is True, this argument is mandatory.


        Example:
            >>> from pyfaust.factparams import StoppingCriterion
            >>> from numpy.random import rand
            >>> s = StoppingCriterion()
            >>> print(s)
            num_its: 500, maxiter: 10000
            >>> s = StoppingCriterion(5)
            >>> print(s)
            num_its: 5, maxiter: 10000
            >>> s = StoppingCriterion(tol=.5)
            >>> print(s)
            tol: 0.5 relerr: False, maxiter: 10000
            >>> s = StoppingCriterion(tol=.2, relerr=True, relmat=rand(10,10))
            >>> print(s)
            tol: 1.1123924064125228, relerr: True, maxiter: 10000

        """
        self.tol = tol
        if(tol != None):
            self._is_criterion_error = True
        else:
            self._is_criterion_error = False
        self.num_its = num_its
        self.maxiter = maxiter
        if(self._is_criterion_error and num_its != StoppingCriterion.DEFAULT_NUMITS
           or not self._is_criterion_error and (maxiter !=
                                          StoppingCriterion.DEFAULT_MAXITER or
                                          tol != None)):
            raise ValueError("The choice between tol and num_its arguments is exclusive.")
        if(relerr and (not isinstance(relmat, np.ndarray))):
            raise ValueError("when error is relative (relerr == true) the "
                             "reference matrix 'relmat' must be specified")
        self.relerr = relerr
        if(self.tol == None):
            self.tol = StoppingCriterion.DEFAULT_TOL
        else:
            if(relerr):
                self.tol *= np.linalg.norm(relmat)

    def __str__(self):
        """
            Converts StoppingCriterion to a str.
        """
        if(self._is_criterion_error):
            return "tol: "+str(self.tol)+", relerr: "+str(self.relerr)+ \
                    ", maxiter: " + str(self.maxiter)
        else:
            return "num_its: "+str(self.num_its)+ \
                    ", maxiter: " + str(self.maxiter)

    def __repr__(self):
        """
            Returns the StoppingCriterion object representation.
        """
        return self.__str__()

class ConstraintGeneric(ABC):
    """
    This is the parent class for representing a factor constraint in FAuST factorization algorithms.

    This class shouldn't be instantiated, rather rely on sub-classes.
    Typically, a constraint finds its place into a ParamsFact or sub-class
    instance (as a container for the factorization parameters).
    It's also possible to set a list of constraints with the ConstraintList class.

     See also: ConstraintInt, ConstraintReal, ConstraintMat,
    pyfaust.fact.palm4msa, pyfaust.fact.hierarchical, ParamsPalm4MSA,
    ParamsHierarchical.

    Attributes:
        _name: The name of the constraint applied to the factor (ConstraintName instance).
        _num_rows: the number of columns of the constrained matrix.
        _num_cols: the number of columns of the constrained matrix.
        _cons_value: The value of the constraint.

    """

    def __init__(self, name, num_rows, num_cols, cons_value, normalized=True, pos=False):
        """
        Constructs a generic constraint.

        Warning: This constructor shouldn't be called directly as the class is
        abstract.

        Args:
            name: The name of the constraint applied to the factor (ConstraintName instance).
            num_rows: the number of columns of the constrained matrix.
            num_cols: the number of columns of the constrained matrix.
            cons_value: The value of the constraint.

        Raises:
            TypeError: Can't instantiate abstract class ConstraintGeneric with
            abstract methods project. This exception is python 3 only, but
            this class shouldn't be instantiated in python 2.7 either.

        """
        if(isinstance(name, str)):
            name = ConstraintName(name)
        self._name = name
        self._num_rows = num_rows
        self._num_cols = num_cols
        self._cons_value = cons_value
        self.normalized = normalized
        self.pos = pos

    @property
    def name(self):
        """
            Property to access the ConstraintName of the constraint.
        """
        return self._name.name

    def is_int_constraint(self):
        """
            Returns True if this constraint is a ConstraintInt, False otherwise.
        """
        return self._name.is_int_constraint()

    def is_real_constraint(self):
        """
            Returns True if this constraint is a ConstraintReal, False otherwise.
        """
        return self._name.is_real_constraint()

    def is_mat_constraint(self):
        """
            Returns True if this constraint is a ConstraintMat, False otherwise.
        """
        return self._name.is_mat_constraint()


    @abstractmethod
    def project(self, M):
        """
            Applies the constraint to the matrix M.

            NOTE: The project function is also called a proximal operator.

            Args:
                M: a numpy array, it must be of the same size as set in object attributes self._num_rows, self._num_cols.

            Raises:
                ValueError: if M.shape and self._num_rows, self._num_cols don't agree.
                TypeError: if M is not a numpy.ndarray

            Returns:
                The proximal operator result as a numpy array.
        """
        if(not isinstance(M, np.ndarray)):
           raise TypeError("M must be a numpy array.")
        if(M.shape[0] != self._num_rows or M.shape[1] != self._num_cols):
            raise ValueError("The dimensions must agree.")

    def __repr__(self):
        return self._name.name_str()+"("+str(self._num_rows)+","+ \
                str(self._num_cols) + (", "+str(self._cons_value) + ")" if not
                                           self.is_mat_constraint()
                                           else ")")

class ConstraintInt(ConstraintGeneric):
    """
        This class represents an integer constraint on a matrix.

        It constrains a matrix by its column/row-vectors sparsity or also
        called 0-norm: ConstraintName.SPLIN, ConstraintName.SPCOL, ConstraintName.SPLINCOL.

        The other constraint names of this type are: ConstraintName.SP,
        ConstraintName.SP_POS, which both designate the 0-norm based constraint of the
        matrix with besides for SP_POS the zero replacement of all
        negative values.


    """
    def __init__(self, name, num_rows, num_cols, cons_value, normalized=True, pos=False):
        """
            Args:
                name: must be a ConstraintName instance set with a value among SP_POS, SP, SPLIN, SPCOL, SPLINCOL (cf. ConstraintName) or it can also be one of the more handy str aliases which are respectively: 'sppos', 'sp', 'splin', 'spcol', 'splincol'.
                num_rows: the number of rows of the constrained matrix.
                num_cols: the number of columns of the constrained matrix.
                cons_value: the integer value of the constraint (the 0-norm as
                sparsity).

            Example:
                >>> from pyfaust.factparams import ConstraintInt
                >>> from numpy.random import rand
                >>> import numpy as np
                >>> cons = ConstraintInt('sppos', 10, 10, 2) # a short for ConstraintInt(ConstraintName(ConstraintName.SP_POS), 10, 10, 2)
                >>> # cons_value == 2 here and this is the 0-norm we want to constrain M to
                >>> M = rand(10,10)
                >>> np.count_nonzero(M)
                100
                >>> np.count_nonzero(cons.project(M))
                2

             See also: ConstraintGeneric.__init__
        """
        super(ConstraintInt, self).__init__(name, num_rows, num_cols,
                                            cons_value, normalized, pos)
        if(not isinstance(cons_value, np.int)):
            raise TypeError('ConstraintInt must receive a int as cons_value '
                            'argument.')
        if(not isinstance(self._name, ConstraintName) or not self._name.is_int_constraint()):
            raise TypeError('ConstraintInt first argument must be a '
                            'ConstraintName with a int type name '
                            '(name.is_int_constraint() must return True).')

    def project(self, M):
        """
             See: ConstraintGeneric.project
        """
        super(ConstraintInt, self).project(M)
        from pyfaust.fact import _check_fact_mat
        is_real = np.empty((1,))
        M = _check_fact_mat('ConstraintInt.project', M, is_real)
        if is_real:
            is_float = M.dtype == 'float32'
            if is_float:
                return _FaustCorePy.ConstraintIntCoreFlt.project(M, self._name.name, self._num_rows,
                                                                 self._num_cols, self._cons_value,
                                                                 self.normalized, self.pos)

            else:
                return _FaustCorePy.ConstraintIntCoreDbl.project(M, self._name.name, self._num_rows,
                                                                 self._num_cols, self._cons_value,
                                                                 self.normalized, self.pos)
        else:
            return _FaustCorePy.ConstraintIntCoreCplxDbl.project(M, self._name.name, self._num_rows,
                                                          self._num_cols, self._cons_value,
                                                          self.normalized, self.pos)

class ConstraintMat(ConstraintGeneric):
    """
        This class represents a matrix-based constraint to apply on a matrix.

    """
    def __init__(self, name, cons_value, normalized=None, pos=False, cons_value_sz=None):
        """
        Constructs a matrix type constraint.

        Args:
            name: must be a ConstraintName instance set with a value among
            SUPP, CONST, TOEPLITZ or CIRC(ULANT) (cf. ConstraintName) or it can also be one of the
            more handy str aliases which are respectively: 'supp' and 'const'.
            num_rows: the number of rows of the constrainted matrix.
            num_cols: the number of columns of the constrained matrix.
            cons_value: the value of the constraint, it must be a numpy.array
            that defines the constraint (the matrix support for SUPP and the
            constant matrix for CONST).

        Example:
            >>> from pyfaust.factparams import ConstraintMat
            >>> from numpy.random import rand
            >>> from numpy import eye
            >>> from numpy.linalg import norm
            >>> cons = ConstraintMat('supp', eye(10))
            >>> M = rand(10,10)
            >>> from numpy import count_nonzero
            >>> count_nonzero(M)
            100
            >>> count_nonzero(cons.project(M))
            10
            >>> from numpy import diag
            >>> diag(M)
            array([ 0.77861201,  0.88512726,  0.56276019,  0.89159211,  0.85893333,
                           0.59919467,  0.02603014,  0.16725741,  0.20578577,  0.40803648])
            >>> diag(cons.project(M))
            array([ 0.39756071,  0.4519476 ,  0.28734638,  0.45524856,  0.43857293,
                           0.30594989,  0.01329104,  0.08540194,  0.10507459,  0.20834417])
            >>> norm(cons.project(M))
            0.99999999999999989

        """
        super(ConstraintMat, self).__init__(name, cons_value.shape[0],
                                            cons_value.shape[1],
                                            cons_value, normalized, pos)
        if(not isinstance(cons_value, np.ndarray)):
            raise TypeError('ConstraintMat must receive a numpy.ndarray as cons_value '
                            'argument.')
        self.cons_value = np.asfortranarray(self._cons_value)
        self._cons_value = self.cons_value
        if(cons_value_sz == None):
            self._cons_value_sz = self._num_cols*self._num_rows
        else:
            self._cons_value_sz = cons_value_sz
        if(normalized == None):
            self.normalized = False
        if(not isinstance(self._name, ConstraintName) or not self._name.is_mat_constraint()):
            raise TypeError('ConstraintMat first argument must be a '
                            'ConstraintName with a matrix type name '
                            '(name.is_mat_constraint() must return True)')
        if(self._name.name == ConstraintName.BLKDIAG):
            self._num_rows = int(cons_value[-1][0])
            self._num_cols = int(cons_value[-1][1])

    def project(self, M):
        """
             See: ConstraintGeneric.project
        """
        super(ConstraintMat, self).project(M)
        is_real = np.empty((1,))
        from pyfaust.fact import _check_fact_mat
        M = _check_fact_mat('ConstraintMat.project', M, is_real)
        if is_real:
            is_float = M.dtype == 'float32'
            if is_float:
                return _FaustCorePy.ConstraintMatCoreFlt.project(M, self._name.name, self._num_rows,
                                                                 self._num_cols,
                                                                 self._cons_value,
                                                                 self._cons_value_sz,
                                                                 self.normalized, self.pos)
            else:
                return _FaustCorePy.ConstraintMatCoreDbl.project(M, self._name.name, self._num_rows,
                                                                 self._num_cols,
                                                                 self._cons_value,
                                                                 self._cons_value_sz,
                                                                 self.normalized, self.pos)

        else:
            return _FaustCorePy.ConstraintMatCoreCplxDbl.project(M, self._name.name, self._num_rows,
                                                              self._num_cols,
                                                              self._cons_value,
                                                              self._cons_value_sz,
                                                              self.normalized, self.pos)


class ConstraintReal(ConstraintGeneric):
    """
        This class represents a real constraint on a matrix.

        It constrains a matrix by a column/row-vector 2-norm
        (ConstraintName.NORMCOL, ConstraintName.NORMLIN).

    """
    def __init__(self, name, num_rows, num_cols, cons_value, normalized=False, pos=False):
        """
        Constructs a real type constraint.

        Args:
            name: must be a ConstraintName instance set with a value among NORMCOL, NORMLIN (cf. ConstraintName) or it can also be one of the more handy str aliases which are respectively: 'normcol', 'normlin'.
            num_rows: the number of columns of the constrained matrix.
            num_cols: the number of columns of the constrained matrix.
            cons_value: the parameter value of the constraint, it must be a
            float number that designates the 2-norm imposed to all columns (if
            name is ConstraintName.NORMCOL) or rows (if
            name is ConstraintName.NORMLIN).

        Example:
            >>> from pyfaust.factparams import ConstraintReal
            >>> from numpy.random import rand
            >>> from numpy.linalg import norm
            >>> cons = ConstraintReal('normcol', 10, 10, 2.) # a short for ConstraintReal(ConstraintName(ConstraintName.NORMCOL), 10, 10, 2.)
            >>> M = rand(10,10)*10
            >>> norm(M[:,2])
            17.041462424512272
            >>> norm(cons.project(M)[:,2])
            2.0


             See also: ConstraintGeneric.__init__
        """
        super(ConstraintReal, self).__init__(name, num_rows, num_cols,
                                             cons_value, normalized=False, pos=False)
        if(not isinstance(cons_value, np.float) and not isinstance(cons_value, np.int)):
            raise TypeError('ConstraintReal must receive a float as cons_value '
                            'argument.')
        self._cons_value = float(self._cons_value)
        if(not isinstance(self._name, ConstraintName) or not self._name.is_real_constraint()):
            raise TypeError('ConstraintReal first argument must be a '
                            'ConstraintName with a real type name '
                            '(name.is_real_constraint() must return True).')

    def project(self, M):
        """
         See: ConstraintGeneric.project
        """
        super(ConstraintReal, self).project(M)
        is_real = np.empty((1,))
        from pyfaust.fact import _check_fact_mat
        M = _check_fact_mat('ConstraintReal.project', M, is_real)
        if is_real:
            is_float = M.dtype == 'float32'
            if is_float:
                return _FaustCorePy.ConstraintRealCoreFlt.project(M, self._name.name, self._num_rows,
                                                       self._num_cols,
                                                       self._cons_value,
                                                       self.normalized, self.pos)

            else:
                return _FaustCorePy.ConstraintRealCoreDbl.project(M, self._name.name, self._num_rows,
                                                                  self._num_cols,
                                                                  self._cons_value,
                                                                  self.normalized, self.pos)
        else:
            return _FaustCorePy.ConstraintRealCoreCplxDbl.project(M, self._name.name, self._num_rows,
                                                           self._num_cols,
                                                           self._cons_value,
                                                           self.normalized, self.pos)


class ConstraintName:
    """
    This class defines the names for the sub-types of constraints into the ConstraintGeneric hierarchy of classes.

    The table <a href="constraint.png">here</a> is a summary of the available
    constraints.

    Attributes:
        SP: Designates a constraint on the sparsity/0-norm of a matrix.
        SPCOL: Designates a sparsity/0-norm constraint on the columns of a matrix.
        SPLIN: Designates a sparsity/0-norm constraint on the rows of a matrix.
        SPLINCOL: Designates a constraint that imposes both SPLIN and SPCOL constraints (see example above for clarification).
        SP_POS: Designates a constraint that imposes a SP constraints and besides set to zero the negative coefficients (it doesn't apply to complex matrices).
        NORMCOL: Designates a 2-norm constraint on each column of a matrix.
        NORMLIN: Designates a 2-norm constraint on each row of a matrix.
        CONST: Designates a constraint imposing to a matrix to be constant.
        SUPP: Designates a constraint by a support matrix S (element-wisely multiplying the matrix to constrain to obtain a matrix for which the 2-norm equals 1, see: ConstraintMat.project()).
        name: The name of the constraint (actually an integer among the valid constants).

    Example:
        >>> # SPLINCOL Comprehensive Example
        >>> # This constraint doesn't necessarily
        >>> # lead to a  image matrix with asked sparsity respected
        >>> # both for columns and rows
        >>> from numpy.random import rand
        >>> from numpy.linalg import norm
        >>> n = 10; m = 10; v = 2;
        >>> M = rand(10,10)
        >>> Mspcol = ConstraintInt('spcol', n, m, v).project(M)
        >>> Msplin = ConstraintInt('splin', n, m, v).project(M)
        >>> Mp = ConstraintInt('splincol', n, m, v).project(M)
        >>> Mp_ = Mspcol + np.where(Mspcol != 0, 0, Msplin) # the sum of Mspcol and Msplin minus their non-zero matrix intersection
        >>> Mp_/= norm(Mp_)
        >>> # Mp is approximately equal to Mp_
        >>> print(norm(Mp-Mp_,2)/norm(Mp_), 2)
        0.00769281206496
        >>> from numpy import count_nonzero
        >>> count_nonzero(Mp[:,1])
        3
        >>> # sparsity value v is not respected
        >>> count_nonzero(Mp_[:,1])
        3
        >>> count_nonzero(Mp_[1,:])
        2
        >>> count_nonzero(Mp[1,:])
        2
        >>> # v is respected for this row

    """
    SP = 0 # Int Constraint
    SPCOL = 1 # Int Constraint
    SPLIN=2 # Int Constraint
    NORMCOL = 3 # Real Constraint
    SPLINCOL = 4 # Int Constraint
    CONST = 5 # Mat Constraint
    SP_POS = 6 # Int Constraint
    BLKDIAG = 7 # Mat Constraint
    SUPP = 8 # Mat Constraint
    NORMLIN = 9 # Real Constraint
    TOEPLITZ = 10 # Mat Constraint
    CIRC = 11 # Mat constraint
    HANKEL = 12 # Mat cons.
    SKPERM = 13 # Int constraint

    def __init__(self, name):
        """
            Constructor of the ConstraintName object.

            Args:
                name: must be a valid constraint name (integer among the
                static constants defined in the class: ConstraintName.SP, ...).
        """
        if(isinstance(name,str)):
            name = ConstraintName.str2name_int(name)
            if(not isinstance(name, np.int) or not
               ConstraintName._arg_is_int_const(name) \
               and not ConstraintName._arg_is_real_const(name) \
               and not ConstraintName._arg_is_mat_const(name)):
                raise ValueError("name must be an integer among ConstraintName.SP,"
                                 "ConstraintName.SPCOL, ConstraintName.NORMCOL,"
                                 "ConstraintName.SPLINCOL, ConstraintName.CONST,"
                                 "ConstraintName.SP_POS," # ConstraintName.BLKDIAG,
                                 "ConstraintName.SUPP, ConstraintName.NORMLIN, "
                                 "ConstraintName.TOEPLITZ, ConstraintName.CIRC")
        self.name = name

    @staticmethod
    def _arg_is_int_const(name):
        return name in [ConstraintName.SP, ConstraintName.SPCOL,
                        ConstraintName.SPLIN, ConstraintName.SPLINCOL,
                        ConstraintName.SP_POS, ConstraintName.SKPERM]

    @staticmethod
    def _arg_is_real_const(name):
        return name in [ConstraintName.NORMCOL, ConstraintName.NORMLIN]

    @staticmethod
    def _arg_is_mat_const(name):
        return name in [ConstraintName.SUPP, ConstraintName.CONST,
                        ConstraintName.CIRC, ConstraintName.TOEPLITZ,
                        ConstraintName.HANKEL, ConstraintName.BLKDIAG]

    def is_int_constraint(self):
        """
            A delegate for ConstraintGeneric.is_int_constraint.
        """
        return ConstraintName._arg_is_int_const(self.name)

    def is_real_constraint(self):
        """
            A delegate for ConstraintGeneric.is_real_constraint.
        """
        return ConstraintName._arg_is_real_const(self.name)

    def is_mat_constraint(self):
        """
            A delegate for ConstraintGeneric.is_mat_constraint.
        """
        return ConstraintName._arg_is_mat_const(self.name)

    def name_str(self):
        return ConstraintName.name_int2str(self.name)

    @staticmethod
    def name_int2str(_id):
        """
            Converts a int constraint short name to its str constant name equivalent.

            For example, name_int2str(ConstraintName.SP) returns 'sp'.
        """
        err_msg = "Invalid argument to designate a ConstraintName."
        if(not isinstance(_id, int)):
            raise ValueError(err_msg)
        if(_id == ConstraintName.SP):
            _str = 'sp'
        elif(_id == ConstraintName.SPLIN):
            _str =  'splin'
        elif(_id == ConstraintName.SPCOL):
            _str =  'spcol'
        elif(_id == ConstraintName.SPLINCOL):
            _str =  'splincol'
        elif(_id == ConstraintName.SP_POS):
            _str =  'sppos'
        elif(_id == ConstraintName.SKPERM):
            _str = 'skperm'
        elif(_id == ConstraintName.NORMCOL):
            _str =  'normcol'
        elif(_id == ConstraintName.NORMLIN):
            _str =  'normlin'
        elif(_id == ConstraintName.SUPP):
            _str =  'supp'
        elif(_id == ConstraintName.CONST):
            _str =  'const'
        elif(_id == ConstraintName.CIRC):
            _str =  'circ'
        elif(_id == ConstraintName.TOEPLITZ):
            _str =  'toeplitz'
        elif(_id == ConstraintName.HANKEL):
            _str =  'hankel'
        elif(_id == ConstraintName.BLKDIAG):
            _str =  'blockdiag'
        else:
            raise ValueError(err_msg)
        return _str

    @staticmethod
    def str2name_int(_str):
        """
            Converts a str constraint short name to its integer constant name equivalent.

            For example, str2name_int('sp') returns ConstraintName.SP.
        """
        err_msg = "Invalid argument to designate a ConstraintName."
        if(not isinstance(_str, str)):
            raise ValueError(err_msg)
        if(_str == 'sp'):
            id = ConstraintName.SP
        elif(_str == 'splin'):
            id = ConstraintName.SPLIN
        elif(_str == 'spcol'):
            id = ConstraintName.SPCOL
        elif(_str == 'splincol'):
            id = ConstraintName.SPLINCOL
        elif(_str == 'sppos'):
            id = ConstraintName.SP_POS
        elif(_str == 'skperm'):
            id = ConstraintName.SKPERM
        elif(_str == 'normcol'):
            id = ConstraintName.NORMCOL
        elif(_str == 'normlin'):
            id = ConstraintName.NORMLIN
        elif(_str == 'supp'):
            id = ConstraintName.SUPP
        elif(_str == 'const'):
            id = ConstraintName.CONST
        elif(_str == 'circ'):
            id = ConstraintName.CIRC
        elif(_str == 'toeplitz'):
            id = ConstraintName.TOEPLITZ
        elif(_str == 'hankel'):
            id = ConstraintName.HANKEL
        elif(_str == 'blockdiag'):
            id = ConstraintName.BLKDIAG
        else:
            raise ValueError(err_msg)
        return id

class ConstraintList(object):
    """
    A helper class for constructing a list of consistent pyfaust.proj.proj_gen projectors or ConstraintGeneric objects.

    NOTE: ConstraintGeneric use is not advised (these objects are not well
    documented). Use rather the projectors functors (from pyfaust.proj module).


    Example:
        >>> from pyfaust.factparams import ConstraintList
        >>> cons = ConstraintList('splin', 5, 500, 32, 'blockdiag',[(10,10), (32,32)], 32, 32);

    """
    def __init__(self, *args):
        # constraint definition tuple
        tuple_len = 4 # name, value, nrows, ncols
        i = 0
        j = 1 # the number of processed constraints
        self.clist = []
        while(i < len(args)):
              if(isinstance(args[i], ConstraintGeneric)):
                  self.clist += [ args[i] ]
                  i += 1
                  continue
              cname = ConstraintName(args[i])
              if(i+1 > len(args)):
                raise ValueError("No value/parameter given to define the "
                                 +str(j)+"-th constraint.")
              cval = args[i+1]
              if(i+2 > len(args)):
                raise ValueError("No number of rows given to define the "
                                 +str(j)+"-th constraint.")
              nrows = args[i+2]
              if(i+3 > len(args)):
                raise ValueError("No number of columns given to define the "
                                 +str(j)+"-th constraint.")
              ncols = args[i+3]
              if(cname.is_int_constraint()):
                cons = ConstraintInt(cname, nrows, ncols, cval)
              elif(cname.is_real_constraint()):
                cons = ConstraintReal(cname, nrows, ncols, cval)
              elif(cname.is_mat_constraint()):
                  if(cname.name == ConstraintName.BLKDIAG):
                      arr = np.asfortranarray(cval).astype(float)
                      cons = ConstraintMat(cname,
                                           arr,
                                           cons_value_sz=arr.size)
                  else:
                      cons = ConstraintMat(cname, cval)
              else:
                raise Exception(cname +" is not a valid name for a "
                                "ConstraintGeneric object")
              self.clist += [ cons ]
              i += tuple_len

    def __len__(self):
        return len(self.clist)

    def __add__(self, other):
        """
        Returns the concatenation of two lists (self and other) as a new ConstraintList.

        Examples:
            >>> from pyfaust.factparams import *
            >>> l1 = ConstraintList('normcol', 1, 32, 32, 'sp', 128, 32, 32,
                                    'sp', 128, 32, 32)
            >>> l2 = ConstraintList('sp', 128, 32, 32, 'sp', 128, 32, 32)
            >>> l1 + l2

        """
        if(not isinstance(other, ConstraintList)):
           raise TypeError("Can't concatenate a ConstraintList with something"
                           " else.")
        return ConstraintList(*(self.clist + other.clist))

    def __getitem__(self, ind):
        """
        x.__getitem__(y) <==> x[y]

            Examples:
                >>> from pyfaust.factparams import *
                >>> cl = ConstraintList('sp', 128, 32, 32, 'sp', 128, 32, 32)
                >>> cl[1]
                <pyfaust.factparams.ConstraintInt at 0x7f13a78fd3c8>
        """
        return self.clist.__getitem__(ind)

class MHTPParams:
    """
    This class defines the set of parameters to run the MHTP-PAL4MSA algorithm.

     See also pyfaust.fact.palm4msa_mhtp, pyfaust.fact.hierarchical_mhtp
    """
    def __init__(self, num_its=50,
                 constant_step_size=False, step_size=1e-3,
                 palm4msa_period=1000,
                 updating_lambda=True):
        """
        Constructor of the MHTPParams class.

         See also pyfaust.fact.palm4msa_mhtp, pyfaust.fact.hierarchical_mhtp

        Args:
            num_its: (int, optional) the number of iterations to run the MHTP algorithm.
            constant_step_size: (bool, optional) True to use a constant step
            for the gradient descent, False otherwise. If False the step size
            is computed dynamically along the iterations (according to a Lipschitz criterion).
            step_size: (float, optional) The step size used when constant_step_size==True. 
            palm4msa_period: (int, optional) The period (in term of iterations)
            according to the MHTP algorithm is ran (i.e.: 0 <= i < N being the PALM4MSA
            iteration, MHTP is launched every i = 0 (mod palm4msa_period).
            Hence the algorithm is ran one time at least -- at PALM4MSA iteration 0).
            updating_lambda: (bool, optional) if True then the scale factor of the Faust resulting of the factorization is updated after each iteration of MHTP (otherwise it never changes during the whole MHTP execution).

        """
        stop_crit = StoppingCriterion(num_its=num_its)
        if not isinstance(stop_crit, StoppingCriterion):
            raise TypeError("stop_crit must be a StoppingCriterion.")
        if not isinstance(constant_step_size, bool):
            raise TypeError("constant_step_size must be a bool.")
        if not isinstance(step_size, float):
            raise TypeError("step_size must be a float.")
        if not isinstance(palm4msa_period, (float, int)):
            raise TypeError("palm4msa_period must be a int.")
        if not isinstance(updating_lambda, bool):
            raise TypeError("updating_lambda must be a bool.")
        self.stop_crit = stop_crit
        self.constant_step_size = constant_step_size
        self.step_size = step_size
        self.palm4msa_period = int(palm4msa_period)
        self.updating_lambda = updating_lambda

    def __repr__(self):
        """
        The MHTPParams instance str representation.
        """
        return ("num_its: "+str(self.stop_crit.num_its)+"\r\n"+
                "constant_step_size: "+str(self.constant_step_size)+"\r\n"+
                "step_size: "+str(self.step_size)+"\r\n"+
                "palm4msa_period: "+str(self.palm4msa_period)+"\r\n"+
                "updating_lambda: " +str(self.updating_lambda)+"\r\n")


class ParamsFact(ABC):
    """
        The parent abstract class to represent the general factorization parameters.

        The class is the base parameters for Palm4MSA and Hierarchical
        factorization but as an abstract class it's not for direct use.
        The documentation is hence left empty, please refer to the subclasses.

     See also  ParamsHierarchical, ParamsPalm4MSA
    """
    DISABLED_OPT = 0
    INTERNAL_OPT = 1
    EXTERNAL_OPT = 2
    def __init__(self, num_facts, is_update_way_R2L, init_lambda,
                 constraints, step_size, constant_step_size,
                 is_verbose, factor_format='dynamic',
                 packing_RL=True, no_normalization=False,
                 no_lambda=False,
                 norm2_max_iter=100,
                 norm2_threshold=1e-6,
                 grad_calc_opt_mode=EXTERNAL_OPT,
                 **kwargs):
        self.num_facts = num_facts
        self.is_update_way_R2L = is_update_way_R2L
        self.init_lambda = init_lambda
        self.step_size = step_size
        import pyfaust.proj
        if((isinstance(constraints, list) or isinstance(constraints, tuple))
           and np.array([isinstance(constraints[i],pyfaust.proj.proj_gen) for i in
                    range(0,len(constraints))]).all()):
            # "convert" projs to constraints
            constraints = [ p.constraint for p in constraints ]
        if(isinstance(constraints, ConstraintList)):
            self.constraints = constraints.clist
        else:
            self.constraints = constraints
        self.is_verbose = is_verbose
        self.constant_step_size = constant_step_size
        self.grad_calc_opt_mode = grad_calc_opt_mode
        self.norm2_max_iter = norm2_max_iter # 0 for default value from C++ core
        self.norm2_threshold = norm2_threshold
        self.factor_format = factor_format
        if factor_format not in ['dense', 'sparse', 'dynamic']:
            raise ValueError("factor_format must be either 'dense', 'sparse' or 'dynamic'")
        self.packing_RL = packing_RL
        self.no_normalization = no_normalization
        self.no_lambda = no_lambda
        self.use_MHTP = False
        if 'use_MHTP' in kwargs.keys():
            if not (isinstance(use_MHTP, bool) and use_MHTP == False) \
                and not isinstance(use_MHTP, MHTPParams):
                raise ValueError("use_MHTP must be False or a MHTPParams")
            self.use_MHTP = use_MHTP

    def __repr__(self):
        """
            Returns object representation.
        """
        return ("num_facts="+str(self.num_facts)+'\r\n'
        "is_update_way_R2L="+str(self.is_update_way_R2L)+'\r\n'
        "init_lambda="+str(self.init_lambda)+'\r\n'
        "step_size="+str(self.step_size)+'\r\n'
        "constant_step_size="+str(self.constant_step_size)+'\r\n'
        "grad_calc_opt_mode="+str(self.grad_calc_opt_mode)+'\r\n'
        "norm2_max_iter="+str(self.norm2_max_iter)+'\r\n'
        "norm2_threshold="+str(self.norm2_threshold)+'\r\n'
        "factor_format="+str(self.factor_format)+'\r\n'
        "packing_RL="+str(self.packing_RL)+'\r\n'
        "no_normalization="+str(self.no_normalization)+'\r\n'
        "no_lambda="+str(self.no_lambda)+'\r\n'
        "is_verbose="+str(self.is_verbose)+'\r\n'
        "constraints="+str(self.constraints)+'\r\n'
        "use_MHTP="+str(self.use_MHTP)+("\r\n" if self.use_MHTP == False else
                                        ""))

    @abstractmethod
    def is_mat_consistent(self, M):
        if(not isinstance(M, np.ndarray)):
            raise ValueError("M must be a numpy ndarray")
        #print("M.shape=", M.shape)
        return M.shape[0] == self.constraints[0]._num_rows and \
                M.shape[1] == self.constraints[-1]._num_cols

    @staticmethod
    def factor_format_str2int(factor_format):
        map = {'dense': 0, 'sparse': 1, 'dynamic': 2}
        if isinstance(factor_format, str):
            if factor_format not in map.keys():
                raise ValueError("factor_format as str must be in "+repr(map.keys()))
            return map[factor_format]
        elif isinstance(factor_format, int):
            if factor_format not in map.values():
                raise ValueError("factor_format as int must be in"
                                 +repr(map.values()))
            return factor_format

    @staticmethod
    def factor_format_int2str(factor_format):
        a = ['dense', 'sparse', 'dynamic']
        if isinstance(factor_format, str):
            if factor_format not in a:
                raise ValueError("factor_format as str must be in "+a)
            return factor_format
        elif isinstance(factor_format, int):
            if factor_format not in range(len(a)):
                raise ValueError("factor_format as int must be in"
                                 +repr(range(len(a))))
            return factor_format

class ParamsHierarchical(ParamsFact):
    """
        The parent class to set input parameters for the hierarchical factorization algorithm.

        The class' goal is to instantiate a fully defined set of parameters
        for the algorithm. But it exists simplified parametrizations for the
        same algorithm as child classes.

         See also ParamsHierarchicalWHT,
        ParamsHierarchicalRectMat, pyfaust.fact.hierarchical
    """
    def __init__(self, fact_constraints, res_constraints, stop_crit1,
                 stop_crit2, is_update_way_R2L=False, init_lambda=1.0,
                 step_size=10.0**-16, constant_step_size=False,
                 is_fact_side_left=False,
                 is_verbose=False,
                 factor_format='dynamic',
                 packing_RL=True,
                 no_normalization=False,
                 no_lambda=False,
                 norm2_max_iter=100,
                 norm2_threshold=1e-6,
                 grad_calc_opt_mode=ParamsFact.EXTERNAL_OPT,
                 **kwargs):
        """
        Constructor.

        Args:
            fact_constraints: a ConstraintList object or a list of
            pyfaust.proj.proj_gen objects to define the constraints of the main
            factor at each level of the factorization hierarchy (the first one for
            the first factorization and so on).
            res_constraints: a ConstraintList object or a list of
            pyfaust.proj.proj_gen objects to define the constraints to apply to
            the residual factor at each level of the factorization hierarchy
            (the first one for the first factorization and so on).
            stop_crit1: a pyfaust.factparams.StoppingCriterion instance
            which defines the algorithm stopping criterion for the local
            optimization of the 2 terms of the last factorization
            (a main factor and a residual).
            stop_crit2: a pyfaust.factparams.StoppingCriterion instance
            which defines the algorithm stopping criterion for the global optimization.
            is_update_way_R2L: if True pyfaust.fact.palm4msa (called for each
            optimization stage) will update factors from the right to the left,
            otherwise it's done in reverse order.
            init_lambda: the scale scalar initial value for the global
            optimization (by default the value is one). It applies only to
            local optimization at each iteration (the global optimization
            lambda is updated consequently).
            step_size: the initial step of the PALM descent for both local and
            global optimization stages.
            constant_step_size: if True the step_size keeps constant along
            the algorithm iterations otherwise it is updated before every
            factor update.
            is_fact_side_left: if True the leftmost factor is factorized,
            otherwise it's the rightmost.
            is_verbose: True to enable the verbose mode.
            factor_format: 'dynamic' (by default), 'dense', or 'sparse'. If
            'dense' or 'sparse' then all factors will be respectively numpy.ndarray or
            scipy.sparse.csr_matrix. If 'dynamic' is used then the algorithm
            determines the format of each factor automatically in order to
            decrease the memory footprint of the Faust. This option is
            available only on the 2020 backend pyfaust.fact.palm4msa, pyfaust.fact.hierarchical
            or pyfaust.fact.palm4msa_mhtp, pyfaust.fact.hierarchical_mhtp.
            packing_RL: True (by default) to pre-compute R and L products
            (only available with 2020 backend of pyfaust.fact.hierarchical).
            no_normalization: False (by default), if True it disables the
            normalization of prox output matrix in PALM4MSA algorithm. Note
            that this option is experimental (only available with 2020 backend of pyfaust.fact.hierarchical).
            no_lambda: False (by default), if True it disables the lambda
            scalar factor in the PALM4MSA algorithm which consists
            basically to set it always to one (it also lowers the algorithm
            cost).
            norm2_max_iter: maximum number of iterations of power iteration
            algorithm. Used for computing 2-norm.
            norm2_threshold: power iteration algorithm threshold (default to
            1e-6). Used for computing 2-norm.
            grad_calc_opt_mode: the mode used for computing the PALM gradient. It
            can be one value among ParamsFact.EXTERNAL_OPT,
            ParamsFact.INTERNAL_OPT or ParamsFact.DISABLED_OPT. This parameter
            is experimental, its value shouln't be changed.
        """
        import pyfaust.proj
        if((isinstance(fact_constraints, list) or isinstance(fact_constraints, tuple))
           and np.array([isinstance(fact_constraints[i],pyfaust.proj.proj_gen) for i in
                    range(0,len(fact_constraints))]).all()):
            # "convert" projs to constraints
            fact_constraints = [ p.constraint for p in fact_constraints ]
        if((isinstance(res_constraints, list) or isinstance(res_constraints, tuple))
           and np.array([isinstance(res_constraints[i],pyfaust.proj.proj_gen) for i in
                    range(0,len(res_constraints))]).all()):
            # "convert" projs to constraints
            res_constraints = [ p.constraint for p in res_constraints ]
        if(not isinstance(fact_constraints, list) and not
           isinstance(fact_constraints, ConstraintList)):
            raise TypeError('fact_constraints must be a list of '
                            'ConstraintGeneric or pyfaust.proj.proj_gen or a'
                            ' ConstraintList.')
        if(not isinstance(res_constraints, list) and not
           isinstance(res_constraints, ConstraintList)):
            raise TypeError('res_constraints must be a list or a ConstraintList.')
        if(len(fact_constraints) != len(res_constraints)):
            raise ValueError('fact_constraints and res_constraints must have'
                             ' same length.')
        num_facts = len(fact_constraints)+1
        if(is_fact_side_left):
            constraints = res_constraints + fact_constraints
        else:
            constraints = fact_constraints + res_constraints

        stop_crits = [ stop_crit1, stop_crit2 ]
        super(ParamsHierarchical, self).__init__(num_facts,
                                                 is_update_way_R2L,
                                                 init_lambda,
                                                 constraints, step_size,
                                                 constant_step_size,
                                                 is_verbose,
                                                 factor_format,
                                                 packing_RL,
                                                 no_normalization,
                                                 no_lambda,
                                                 norm2_max_iter,
                                                 norm2_threshold,
                                                 grad_calc_opt_mode,
                                                 **kwargs)
        self.stop_crits = stop_crits
        self.is_fact_side_left = is_fact_side_left
        if((not isinstance(stop_crits, list) and not isinstance(stop_crits,
                                                                tuple)) or
           len(stop_crits) != 2 or
           not isinstance(stop_crits[0],StoppingCriterion) or not
           isinstance(stop_crits[1],StoppingCriterion)):
            raise TypeError('ParamsHierarchical stop_crits argument must be'
                            ' a list/tuple of two StoppingCriterion objects')
        if((not isinstance(constraints, list) and not isinstance(constraints,
                                                                tuple) and not
           (isinstance(constraints, ConstraintList))) or
           np.array([not isinstance(constraints[i],ConstraintGeneric) for i in
                    range(0,len(constraints))]).any()):
            raise TypeError('constraints argument must be a list/tuple of '
                            'ConstraintGeneric (or subclasses) objects')
        # auto-infer matrix dimension sizes according to the constraints
        if(is_fact_side_left):
            self.data_num_rows = res_constraints[-1]._num_rows
            self.data_num_cols = fact_constraints[0]._num_cols
        else:
            self.data_num_rows = constraints[0]._num_rows
            self.data_num_cols = constraints[-1]._num_cols

    def is_mat_consistent(self, M):
        if(not isinstance(M, np.ndarray)):
            raise ValueError("M must be a numpy ndarray")
        return M.shape[0] == self.data_num_rows and \
                M.shape[1] == self.data_num_cols

    def __repr__(self):
        """
            Returns object representation.
        """
        return super(ParamsHierarchical, self).__repr__()+ \
                "local stopping criterion: "+str(self.stop_crits[0])+"\r\n" \
                "global stopping criterion"+str(self.stop_crits[1])+"\r\n" \
                "is_fact_side_left:"+str(self.is_fact_side_left)

class ParamsHierarchicalDFT(ParamsHierarchical):
    """
    The simplified parameterization class for factorizing a DFT matrix using the hierarchical factorization algorithm.

     See also pyfaust.fact.hierarchical
    """

    def __init__(self, n):
        """
        Args:
            n: the log2(size) of the DFT matrix (of size 2^n x 2^n).
        """
        n = int(n)
        supports = self.support_DFT(n)
        stop_crit = StoppingCriterion(num_its=8)
        fac_cons = []
        for i in range(n):
            fac_cons += [ConstraintMat("supp", supports[i])]
        res_cons = []
        for j in range(n-1):
            supp = np.eye(*supports[0].shape, dtype=np.complex)
            for i in range(j+1, n+1):
                fi = supports[i]
                supp = supp@fi
            supp[np.nonzero(supp)] = 1
            res_cons += [ConstraintMat("supp", supp)]

        super(ParamsHierarchicalDFT, self).__init__(fac_cons,
                                                     res_cons+[ConstraintMat("supp",
                                                                            supports[-1])],
                                                     stop_crit,
                                                     stop_crit,
                                                     is_update_way_R2L=True)
        self.supports = supports

    @staticmethod
    def createParams(M, p):
        pot = np.log2(M.shape[0])
        if(pot > int(pot) or M.shape[0] != M.shape[1]):
            raise ValueError('M must be of order a power of two.')
        pot = int(pot)
        return ParamsHierarchicalDFT(pot)

    def __repr__(self):
        return super(ParamsHierarchicalDFT, self).__repr__()

    def support_DFT(self, n):
        """
        Generates the DFT supports with the additional bit-reversal permutation matrix.

        n: the log2(size) of the DFT (of size 2^n x 2^n).
        """
        size = 2 ** n
        supports = []
        for i in range(n):
            supp_bf = np.kron(np.ones((2,2)), np.eye(2 ** ((n-i)-1)))
            supports += [np.kron(np.eye(2**i), supp_bf).astype(np.complex)]
        # bit-reversal permutation
        row_ids = np.arange(size)
        col_ids = self.bit_rev_permu(n)
        br_permu = np.zeros((size,size)).astype(np.complex)
        br_permu[row_ids, col_ids] = 1
        supports += [br_permu]
        return supports

    def bit_rev_permu(self, n):
        """
        Returns the Bit-reversal permutation of index n.

        Args:
            n: the index of the permutation.

        Returns: the Bit-reversal permutation of index n as a list.
        """
        if n == 0:
            return [0]
        size = 1 << n
        v = [i for i in range(size)]
        lower_mask = int(1)
        upper_mask = int(1<<(n-1))
        shift = 0
        while(lower_mask < upper_mask):
            for i in range(0,size):
                lobit = (int(v[i]) & lower_mask) >> shift
                hibit = (int(v[i]) & upper_mask) >> (n-shift-1)
                if lobit > hibit:
                    v[i] ^= lower_mask
                    v[i] |= upper_mask
                elif lobit < hibit:
                    v[i] |= lower_mask
                    v[i] ^= upper_mask
            lower_mask <<= 1
            upper_mask >>= 1
            shift += 1
        return v


class ParamsHierarchicalWHT(ParamsHierarchical):
    """
    The simplified parameterization class for factorizing a square matrix (of order a power of two) with the hierarchical factorization algorithm.

    This type of parameters is typically used for a Hadamard matrix
    factorization.

     See also pyfaust.fact.hierarchical, pyfaust.demo.hadamard
    """
    def __init__(self, n, proj_name='splincol'):
        """
        args:
            n: the number of output factors (the input matrix to factorize must
            be of shape (2**n, 2**n)) .
            proj_name: the type of projector used, must be either
            'splincol' (default value) or 'skperm'.
        """
        if proj_name not in ['skperm', 'splincol']:
            raise ValueError('cons_name must be either splincol'
                             ' or skperm')
        cons_name = ConstraintName.str2name_int(proj_name)
        d = 2**int(n)
        stop_crit = StoppingCriterion(num_its=30)
        super(ParamsHierarchicalWHT,
              self).__init__([ConstraintInt(ConstraintName(cons_name),d,d,2)
                              for i in range(0,n-1)],
                             [ConstraintInt(ConstraintName(cons_name),d,d,int(d/2.**(i+1)))
                              for i in range(0,n-1)],
                             stop_crit, stop_crit,
                             is_update_way_R2L=True,
                             packing_RL=False)

    @staticmethod
    def createParams(M, p):
        pot = np.log2(M.shape[0])
        if(pot > int(pot) or M.shape[0] != M.shape[1]):
            raise ValueError('M must be a '
                             'square matrix of order a power of '
                             'two.')
        pot = int(pot)
        return ParamsHierarchicalWHT(pot)

    def __repr__(self):
        return super(ParamsHierarchicalWHT, self).__repr__()


# this is left here for descendant compatibility but it will be removed in a
# next version
class ParamsHierarchicalSquareMat(ParamsHierarchicalWHT):
    """
    This class is deprecated, please use ParamsHierarchicalWHT instead.
    This class will be removed in a few minor versions of pyfaust.
    """
    @staticmethod
    def _warn():
        warn("ParamsHierarchicalSquareMat is deprecated, please use"
             " ParamsHierarchicalWHT instead. This class will be deleted in a"
             " few minor versions of pyfaust.")

    def __init__(self, n, proj_name='splincol'):
        super(ParamsHierarchicalSquareMat, self).__init__(n, proj_name)
        ParamsHierarchicalSquareMat._warn()

    @staticmethod
    def createParams(M, p):
        ParamsHierarchicalSquareMat._warn()
        return ParamsHierarchicalWHT.createParams(M, p)

class ParamsHierarchicalRectMat(ParamsHierarchical):
    """
    The simplified parameterization class for factorizing a rectangular matrix with the hierarchical factorization algorithm (pyfaust.fact.hierarchical).

    The parameters m and n are the dimensions of the input matrix.

     See also pyfaust.fact.hierarchical, pyfaust.demo.bsl
    """

    DEFAULT_P_CONST_FACT = 1.4

    def __init__(self, m, n, j, k, s, rho=0.8, P=None):
        """
        Constructor for the specialized parametrization used for example in the pyfaust.demo.bsl (brain souce localization).

        For a better understanding you might refer to [1].

        [1] Le Magoarou L. and Gribonval R., "Flexible multi-layer sparse
        approximations of matrices and applications", Journal of Selected
        Topics in Signal Processing, 2016. [https://hal.archives-ouvertes.fr/hal-01167948v1]

        Args:
            m: the number of rows of the input matrix.
            n: the number of columns of the input matrix.
            j: the total number of factors.
            k: the integer sparsity per column (SPCOL, pyfaust.proj.spcol) applied to the
            rightmost factor (index j-1) of shape (m, n).
            s: the integer sparsity targeted (SP, pyfaust.proj.sp) for all the factors from the
            second (index 1) to index j-2. These factors are square of order n.
            rho: defines the integer sparsity (SP, pyfaust.proj.sp) of the i-th residual (i=0:j-2): ceil(P*rho**i).
            P: (default value is ParamsHierarchicalRectMat.DEFAULT_P_CONST_FACT) defines the integer sparsity of the i-th residual (i=0:j-2): ceil(P*rho**i).
        """
        from math import ceil
        #test args
        for arg,aname in zip([m, n, j, k, s],["m","n","j","k","s"]):
            if(not isinstance(m, int) and not isinstance(m, np.integer)):
                raise TypeError(aname+" must be an integer.")
        if(not isinstance(rho, float)):
            raise TypeError('rho must be a float')
        if(not P):
            P=ParamsHierarchicalRectMat.DEFAULT_P_CONST_FACT*m**2
        elif(not isinstance(P, float)):
            raise TypeError('P must be a float')
        S1_cons = ConstraintInt('spcol', m, n, k)
        S_cons = [S1_cons]
        for i in range(j-2):
            S_cons += [ ConstraintInt('sp', m, m, s*m) ]

        R_cons = []
        for i in range(j-1):
            R_cons += [ConstraintInt('sp', m, m, int(ceil(P*rho**i)))]

        stop_crit = StoppingCriterion(num_its=30)

        super(ParamsHierarchicalRectMat, self).__init__(S_cons, R_cons,
                                                            stop_crit,
                                                            stop_crit,
                                                            is_update_way_R2L=True,
                                                            is_fact_side_left=True)

    @staticmethod
    def createParams(M, p):
        """
        Static member function to create a ParamsHierarchicalRectMat instance by a simplified parametrization expression.

        Args:
            p: a list of the form ['rectmat', j, k, s] to create a parameter
            instance with the parameters j, k, s (see the class
            ParamsHierarchicalRectMat.__init__ for
            their definitions).

        Example:
            >>> from pyfaust.factparams import ParamsHierarchicalRectMat
            >>> num_facts = 9
            >>> k = 10
            >>> s = 8
            >>> p = ParamsHierarchicalRectMat.createParams(rand(256, 1024), ['rectmat', num_facts, k, s])
        """
        # caller is responsible to check if name in p is really 'rectmat'
        def parse_p(p):
            # p = ('rectmat', j, k, s)
            # or p is (['rectmat', j, k, s ],{'rho':rho, P: P})
            if(isinstance(p, tuple) or isinstance(p, list)):
                if(len(p) == 2 and (isinstance(p[0], list) or isinstance(p[0],
                                                                        tuple))
                  and len(p[0]) == 4 and isinstance(p[1], dict) and 'rho' in
                   p[1].keys() and 'P' in p[1].keys()):
                    # ENOTE: concatenation instead of unpacking into list
                    # because of py2 (it would be ok for py3)
                    p = list(p[0][:])+[p[1]['rho'], p[1]['P']]
                elif(len(p) == 4 and (isinstance(p, list) or isinstance(p,
                                                                        tuple))):
                    pass #nothing to do
                else:
                    raise ValueError('The valid formats for p are: '
                                     '("rectmat",j,k,s) or '
                                     '[("rectmat",j,k,s),{"rho": rho, "P": P}]'
                                     ' with j, k, s being integers and rho and'
                                     ' P being floats')
            return p
        p = parse_p(p)
        if(not isinstance(M, np.ndarray)):
            raise TypeError('M must be a numpy.ndarray.')
        p = ParamsHierarchicalRectMat(M.shape[0], M.shape[1], *p[1:])
        return p

    def __repr__(self):
        return super(ParamsHierarchicalRectMat, self).__repr__()

class ParamsPalm4MSA(ParamsFact):
    """
        The class intents to set input parameters for the Palm4MSA algorithm.

         See also pyfaust.fact.palm4msa
    """

    def __init__(self, constraints, stop_crit, init_facts=None,
                 is_update_way_R2L=False, init_lambda=1.0,
                 step_size=10.0**-16,
                 constant_step_size=False,
                 is_verbose=False,
                 norm2_max_iter=100,
                 norm2_threshold=1e-6,
                 grad_calc_opt_mode=ParamsFact.EXTERNAL_OPT,
                 **kwargs):
        """
            Constructor.

            Args:
                constraints: a pyfaust.factparams.ConstraintList
                or a Python list of pyfaust.proj.proj_gen. The number of items
                determines the number of matrix factors.
                stop_crit: a pyfaust.factparams.StoppingCriterion instance
                which defines the algorithm stopping criterion.
                init_facts: if defined, pyfaust.fact.palm4msa will initialize the factors
                with init_facts (by default, None, implies that the first
                factor to be updated is initialized to zero and the others to
                identity. Note that the so called first factor can be the
                rightmost or the leftmost depending on the is_update_way_R2L argument).
                Note also that the matrices must be np.ndarray if the backend
                argument of pyfaust.fact.palm4msa is equal to 2016, otherwise (backend==2020)
                it is possible to use np.ndarray or scipy.sparse.csr_matrix
                (depending of the ParamsPalm4MSA.factor_format attribute).
                is_update_way_R2L: if True pyfaust.fact.palm4msa will update factors from
                the right to the left, otherwise it's done in reverse order.
                init_lambda: the scale scalar initial value (by default the
                value is one).
                step_size: the initial step of the PALM descent.
                constant_step_size: if True the step_size keeps constant along
                the algorithm iterations otherwise it is updated before every
                factor update.
                is_verbose: True to enable the verbose mode.
                norm2_max_iter: maximum number of iterations of power iteration
                algorithm. Used for computing 2-norm.
                norm2_threshold: power iteration algorithm threshold (default to
                1e-6). Used for computing 2-norm.
                grad_calc_opt_mode: the mode used for computing the PALM gradient.
                It can be one value among pyfaust.factparams.ParamsFact.EXTERNAL_OPT,
                pyfaust.factparams.ParamsFact.INTERNAL_OPT or pyfaust.factparams.ParamsFact.DISABLED_OPT. This
                parameter is experimental, its value shouldn't be changed.
                no_normalization: False (by default), if True it disables the
                normalization of prox output matrix in PALM4MSA algorithm. Note
                that this option is experimental.
                no_lambda: False (by default), if True it disables the lambda
                scalar factor in the PALM4MSA algorithm which consists
                basically to set it always to one (it lowers also the algorithm
                cost).

        """
        if(not isinstance(constraints, list) and not
           isinstance(constraints, ConstraintList)):
            raise TypeError('constraints argument must be a list or a'
                            ' ConstraintList.')
        num_facts = len(constraints)
        super(ParamsPalm4MSA, self).__init__(num_facts, is_update_way_R2L,
                                             init_lambda,
                                             constraints, step_size,
                                             constant_step_size,
                                             is_verbose, grad_calc_opt_mode=grad_calc_opt_mode,
                                             **kwargs)
        if(init_facts != None and (not isinstance(init_facts, list) and not isinstance(init_facts,
                                                               tuple) or
           len(init_facts) != num_facts)):
            raise ValueError('ParamsPalm4MSA init_facts argument must be a '
                             'list/tuple of '+str(num_facts)+" (num_facts) arguments.")
        else:
            self.init_facts = init_facts
        if(not isinstance(stop_crit, StoppingCriterion)):
           raise TypeError('ParamsPalm4MSA stop_crit argument must be a StoppingCriterion '
                           'object')
        self.stop_crit = stop_crit
        #TODO: verify number of constraints is consistent with num_facts

    def is_mat_consistent(self, M):
        return super(ParamsPalm4MSA, self).is_mat_consistent(M)

    def __repr__(self):
        return super(ParamsPalm4MSA, self).__repr__()+ \
                "stopping criterion: "+str(self.stop_crit)

class ParamsPalm4MSAFGFT(ParamsPalm4MSA):
    """
    """
    def __init__(self, constraints, stop_crit, init_facts=None,
                 init_D=None,
                 is_update_way_R2L=False, init_lambda=1.0,
                 step_size=10.0**-16,
                 is_verbose=False):
        super(ParamsPalm4MSAFGFT, self).__init__(constraints, stop_crit,
                                                 init_facts, is_update_way_R2L,
                                                 init_lambda, step_size,
                                                 True, is_verbose)
        self.init_D = _init_init_D(init_D, self.constraints[0]._num_rows)

def _init_init_D(init_D, dim_sz):
    """
        Utility function for ParamsHierarchicalFGFT, ParamsPalm4MSAFGFT
    """
    def _check_init_D_is_consistent(init_D):
        if(not isinstance(init_D, np.ndarray)):
            raise ValueError("init_D must be a numpy ndarray")
        if(init_D.ndim != 1):
            raise ValueError("init_D must be a vector.")
        if(init_D.shape[0] != dim_sz):
            raise ValueError("init_D must have the same size as first "
                             "constraint's number of rows")

    if(not isinstance(init_D, np.ndarray) and init_D == None):
        init_D = np.ones(dim_sz)
    _check_init_D_is_consistent(init_D)
    return init_D




class ParamsFactFactory:
    """
        The factory for creating simplified FAuST hierarchical algorithm parameters (ParamsHierarchical).

        Note: this factory is not related to ParamsPalm4MSA, it only creates
        ParamsHierarchical instances.

         See also  ParamsHierarchicalRectMat,
        ParamsHierarchicalWHT, pyfaust.fact.hierarchical()
    """
    SIMPLIFIED_PARAM_NAMES = [
        [ "squaremat", "hadamard"],
        ["rectmat", "meg"],
        ["dft"],
    ]
    SQRMAT_ID = 0
    RECTMAT_ID = 1
    DFTMAT_ID = 2

    @staticmethod
    def createParams(M, p):
        """

        Args:
            p:
        """
        from pyfaust.factparams import \
        (ParamsHierarchicalWHT,
        ParamsHierarchicalRectMat)
        param_id = None
        c = ParamsFactFactory # class alias
        if(not c.is_a_valid_simplification(p)):
            raise TypeError('Invalid p to represent a simplified '
                            'parametrization.')
        param_id = c.get_simplification_name(p)
        if(param_id.lower() in c.SIMPLIFIED_PARAM_NAMES[c.SQRMAT_ID]):
            return ParamsHierarchicalWHT.createParams(M, p)
        elif(param_id.lower() in c.SIMPLIFIED_PARAM_NAMES[c.RECTMAT_ID]):
            return ParamsHierarchicalRectMat.createParams(M, p)
        elif(param_id.lower() in c.SIMPLIFIED_PARAM_NAMES[c.DFTMAT_ID]):
            return ParamsHierarchicalDFT.createParams(M, p)
        else:
            raise ValueError("p is not a known simplified parametrization.")

    @staticmethod
    def get_simplification_name(p):
        # to be a valid simplification form
        # p must be something among:
        # 1. a str
        # 2. a list/tuple with l[0] being a str
        # 3. a list/tuple with first elt a list/tuple such that l[0][0] is a str
        max_depth=3
        l = [p]
        for i in range(max_depth):
            if((isinstance(l, list) or isinstance(l, tuple))):
                if(isinstance(l[0], str)):
                    return l[0]
                else:
                    l = l[0]
        return None

    @staticmethod
    def is_a_valid_simplification(p):
        return ParamsFactFactory.get_simplification_name(p) != None
