# -*- coding: utf-8 -*-

import numpy as np
import itertools
import math
import hyperclip.hyperfunc

class Hyperclip():
    """
    Hyperclip class. The volume computation has been proposed by Yunhi Cho and Seonhwa Kim (see reference).
    Two methods are provided to configure hyperplanes : :meth:`~hyperclip.Hyperclip.set_A_r` and :meth:`~hyperclip.Hyperclip.set_hyperplanes`.
    
    Parameters
    ----------
    zero : float, default=10**-7
        The zero tolerance. Used for epsilon-perturbation added to solve problematic systems.
    verbose : int, default=0
        Verbosity level. A value lower than or equal to ``-1`` deactivates any warning.
    
    References
    ----------
    .. [1] `Cho, Yunhi and Kim, Seonhwa  (2020). "Volume of Hypercubes Clipped by Hyperplanes and Combinatorial Identities." <https://doi.org/10.13001/ela.2020.5085>`_
    """
    def __init__(self,
                 zero=10**-7,
                 cython=True,
                 verbose=0):
        self.zero = zero
        self.cython = cython
        self.verbose=verbose
        
        self._list_I = None
        self._list_v = None
        self._list_prod = None
        self._list_v_star = None
    
    def set_A_R(self, A, R):
        """
        Set the hyperplanes coefficients through the A matrix and the R vector according to Cho and Kim notation.

        Parameters
        ----------
        A : array-like of shape (n_features, n_hyperplanes)
            The A matrix.
        R : array-like of shape (n_hyperplanes,)
            The R vector.

        Returns
        -------
        self

        """
        self.A = A
        self.R = R
        self.n, self.m = self.A.shape
                
        return(self)

    def set_hyperplanes(self, hyperplanes):
        """
        Set the hyperplanes through a list of hyperplanes. 
        A and R are generated consequently.

        Parameters
        ----------
        hyperplanes : list of :class:`~hyperclip.Hyperplane`
            A list of Hyperplanes objects.

        Returns
        -------
        self

        """
        self.n = hyperplanes[0].a.size
        self.m = len(hyperplanes)
        self.A = np.zeros((self.n, self.m))
        self.R = np.zeros(self.m)
        for i_hyp, hyp in enumerate(hyperplanes):
            self.A[:, i_hyp] = hyp.a.copy()
            self.R[i_hyp] = hyp.r
        
        return(self)
    
    def check(self, raise_error=True):
        """
        Check the clipping conditions according to Cho and Kim.

        Parameters
        ----------
        raise_error : bool, default=True
            If ``True``, an unsatisfied clipping condition raises an error, otherwise, a ``False`` boolean is returned.
        
        Raises
        ------
            ValueError : If a clipping condition is not satisfied.

        Returns
        -------
        c : bool
            The check result.

        """
        
        if self.cython:
            if not hyperclip.hyperfunc.clipping_condition_A(A = self.A, 
                                                            R = self.R,
                                                            zero = self.zero):
                if raise_error:
                    raise(ValueError("The clipping condition (A) is not satisfied."))
                else:
                    return(False)
            
            if not hyperclip.hyperfunc.clipping_condition_B(A = self.A,
                                                            R = self.R,
                                                            zero = self.zero):
                if raise_error:
                    raise(ValueError("The clipping condition (B) is not satisfied."))
                else:
                    return(False)
        else:
            if not self._clipping_condition_A():
                if raise_error:
                    raise(ValueError("The clipping condition (A) is not satisfied."))
                else:
                    return(False)
            
            if not self._clipping_condition_B():
                if raise_error:
                    raise(ValueError("The clipping condition (B) is not satisfied."))
                else:
                    return(False)
        
        return(True)
    
    def volume(self):
        """
        Computes the volume. If the object is not checked, a warning raises and 
        the clipping condition (B) only is checked to achive the volume computation.
        To avoid any warning message, set the verbosity lower than or equal to ``-1``.

        Returns
        -------
        None.

        """
        if self.cython:
            return(hyperclip.hyperfunc.volume(A = self.A,
                                              R = self.R, 
                                              check_A=False,
                                              zero=self.zero))
        
        if self._list_I is None:
            if self.verbose > -1:
                print('Warning : The hyperclip object is not checked. The clipping condition (B) is checked.')
            if not self._clipping_condition_B():
                raise(ValueError("The clipping condition (B) is not satisfied."))
        
        vol = 0.0
        
        for id_vertex in range(len(self._list_v)):
            I = self._list_I[id_vertex]
            v = self._list_v[id_vertex]
            prod = self._list_prod[id_vertex]
            v_star = self._list_v_star[id_vertex]
            
            v_0 = np.arange(self.n)[v == 0] + 1
            
            g_m_v = np.dot(self.A[:,self.m-1].T, v) + self.R[self.m-1]
            A_v_star_I = self._get_det_sub_A(v_star, I)
            
            numerator = (-1)**(v_0.size + v_star.sum()) 
            numerator *= ( g_m_v * A_v_star_I )**self.n
            
            denominator = math.factorial(self.n) * np.abs(A_v_star_I) * prod
            
            vol += numerator / denominator
            
        return(vol)
        
    def _clipping_condition_A(self):
        
        list_I = self._get_list_I(self.m-1)
        
        for I in list_I:
            I_bar = np.delete(np.arange(self.m) + 1, I-1)
            
            list_K = self._get_list_K(len(I)-1)
            
            list_J = self._get_list_J(list_K)
            
            for id_k in range(len(list_K)):
                K = list_K[id_k]
                
                for id_J in range(len(list_J[id_k])):
                    J = list_J[id_k][id_J]
                    
                    # compute vertex
                    v = self._compute_vertex(I, J, K)
                                        
                    # the clipping condition is True if no solutions are found
                    if self._test_vertex(v, I, I_bar):
                        return(False)
            
        return(True)

    def _clipping_condition_B(self):
    
        list_I = self._get_list_I(self.m-1)
        
        self._list_I = []
        self._list_v = []
        self._list_prod = []
        self._list_v_star = []
        
        for I in list_I:
            
            I_bar = np.delete(np.arange(self.m) + 1, I-1)
            
            list_K = self._get_list_K(len(I))
            
            list_J = self._get_list_J(list_K)
            
            
            for id_k in range(len(list_K)):
                K = list_K[id_k]
                
                for id_J in range(len(list_J[id_k])):
                    J = list_J[id_k][id_J]
                    
                    # compute vertex
                    v = self._compute_vertex(I, J, K)
                    if self._test_vertex(v, I, I_bar):
                                                    
                        v_star = np.arange(self.n)[np.all((v != 0, v!=1), axis=0)] + 1
                        v_01 = np.delete(np.arange(self.n), v_star-1) + 1
                        prod = 1
                        for t in I:
                            I_union_m_remove_t = list(I.copy())
                            I_union_m_remove_t.append(self.m)
                            I_union_m_remove_t.remove(t)
                            I_union_m_remove_t = np.sort(I_union_m_remove_t)
                            
                            prod *= self._get_det_sub_A(v_star, I_union_m_remove_t)
                        
                        for t in v_01:
                            I_union_m = list(I.copy())
                            I_union_m.append(self.m)
                            I_union_m = np.sort(I_union_m)
                            
                            v_star_union_t = list(v_star.copy())
                            v_star_union_t.append(t)
                            v_star_union_t = np.sort(v_star_union_t)
                            
                            prod *= self._get_det_sub_A(v_star_union_t, I_union_m)
                        
                        if np.isclose(prod, 0):
                            self._list_I = None
                            self._list_v = None
                            self._list_prod = None
                            self._list_v_star = None
                            return(False)
                        
                        self._list_I.append(I)
                        self._list_v.append(v)
                        self._list_prod.append(prod)
                        self._list_v_star.append(v_star)
        return(True)
    
    def _compute_vertex(self, I, J, K):
        # sys generate
        sys_A, sys_R = self._get_syst(I, J, K)
        
        # sol computation
        v = np.zeros(self.n)
        v[J-1] = 1
                
        if len(K) > 0:
            try:
                v[K-1] = np.linalg.solve(sys_A[:,:len(K)].T, -sys_R[:len(K)])
            except:
                if self.verbose > -1:
                    print('Warning : epsilon-perturbation added to solve the system.')
                
                v[K-1] = np.linalg.solve(sys_A[:,:len(K)].T + (np.random.random((len(K), len(K))) * 2 - 1) * self.zero, 
                                         -sys_R[:len(K)])
                
        
        return(v)
    
    def _test_vertex(self, v, I_equal, I_pos):
        # H=
        test = np.all(np.isclose(np.dot(self.A[:, I_equal-1].T, v) + self.R[I_equal-1], 
                                 np.zeros(len(I_equal))))
        
        # H+
        test = np.all((test, 
                       np.all(np.dot(self.A[:, I_pos-1].T, v) + self.R[I_pos-1] >= 0)))
        
        # hypercube
        test = np.all((test, np.all(v>=0), np.all(v<=1)))
        
        return(test)
    
    
    
    def _get_list_I(self, m_max):
        list_I = []
        for i_m in range(0, m_max+1):
            list_I += list(itertools.combinations(np.arange(m_max) + 1, i_m))
        
        list_I = [np.array(list(I)).astype(int) for I in list_I]
        
        return(list_I)
    
    def _get_list_K(self, card):
        
        if card < 0:
            return([])
        
        list_K = list(itertools.combinations(np.arange(self.n)+1, card))
        list_K = [np.array(list(K)).astype(int) for K in list_K]
        
        return(list_K)
    
    def _get_list_J(self, list_K):
        list_J = []
        
        for K in list_K:
            pool = np.arange(self.n) + 1
            
            if len(K) > 0:
                pool = np.delete(pool, np.array(K) - 1)
            
            list_J__K = []
            
            for n_ones in range(self.n - len(K) + 1):
                list_J__K += list(itertools.combinations(pool, n_ones))
            
            list_J__K = [np.array(list(J__K)).astype(int) for J__K in list_J__K]
            list_J.append(list_J__K)
                
        return(list_J)
            
    
    def _get_sub_A(self, I, J):
        B = np.zeros((len(I), len(J)))
        for id_i, i in enumerate(I-1):
            for id_j, j in enumerate(J-1):
                B[id_i, id_j] = self.A[i,j]
        
        # print(B)
        return(B)

    def _get_det_sub_A(self, I, J):
        return(np.linalg.det(self._get_sub_A(I, J)))
    
    def _get_syst(self, I, J, K):
        sys_A = self.A[:, I-1].copy()
        
        sys_R = self.R[I-1].copy()
        
        sys_R += sys_A[J-1].sum(axis=0)
        
        sys_A = sys_A[K-1]
        
        return(sys_A, sys_R)
        
