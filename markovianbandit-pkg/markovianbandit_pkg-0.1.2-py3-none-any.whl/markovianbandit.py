"""
This file contains method to generate random bandits and compute their whittle indices
"""
import numpy as np
from . import whittle_computation as whittle

def random_rewards(dim):
    """
    Return a random vector
    """
    return np.random.rand(dim, 2)

def random_matrix(dim, struct='dense'):
    """
    Generate a pair of transitions matrices with structure "struct"

    Struct must be:
    - dense
    - dense-unif
    - tridiag
    - (ndiag, width)
    - (ndiag-unif, width)
    """
    if struct=="dense":
        return random_matrices_dense(dim)
    if struct=="sparse":
        return random_matrices_sparse(dim)
    if struct=="tridiag":
        return random_matrices_tridiag(dim)
    if len(struct)==2 and struct[0]=="ndiag":
       return random_matrices_ndiag(dim, struct[1])
    if len(struct)==2 and struct[0]=="ndiag-unif":
        return random_matrices_ndiag_unif(dim, struct[1])
    if struct=="dense-unif":
        return random_matrices_dense_unif(dim)
    assert False, "structure non recognized"

def random_matrices_dense_unif(dim):
    """
    Generate a random dense matrix.
    """
    matrix = np.random.rand(dim, 2, dim)
    for state in range(dim):
        for action in [0,1]:
            matrix[state, action, :] /= sum(matrix[state, action, :])
    return matrix

def random_matrices_dense(dim):
    """
    Make transition matrix with uniform distribution
    :param dim : int- dim of the transition matrix
    """
    transition_matrices= np.random.exponential(size=(dim, 2, dim))
    for state in range(dim):
        for action in [0,1]:
            transition_matrices[state, action, :] /= sum(transition_matrices[state, action, :])
    return transition_matrices

def random_matrices_sparse(dim):
    """
    Make transition matrix with uni. distr. but sparse
    :param dim : int - dim of the transition matrix
    """
    transition_matrices= np.zeros((dim, 2, dim))
    for action in [0,1]:
        M = np.random.exponential(size=(dim, dim))
        keep_prob = 0.1
        mask = np.random.choice([0, 1], p=[1.0-keep_prob, keep_prob], size=(dim, dim))
        for state in range(dim):
            if len(M[state][mask[state]==1]) < 2:
                transition_matrices[state, action] = np.random.exponential(size=dim)
            else:
                transition_matrices[state, action][mask[state]==1] = M[state][mask[state]==1]
            transition_matrices[state, action, :] /= sum(transition_matrices[state, action, :])
    return transition_matrices

def random_matrices_ndiag(dim, width=1):
    """
    Generates a random probability matrix with coefficient on the diagonals +/- width
    
    Example: 
    - width = 0 is a diagonal matrix
    - width = 1 is a tri-diagonal matrix
    """
    transition_matrices = np.zeros((dim, 2, dim))
    for action in [0, 1]:
        for w in range(-width, width+1):
            transition_matrices[:,action,:] += np.diag(np.random.exponential(size=dim-abs(w)), k=w)
        for state in range(dim):
            transition_matrices[state,action,:] /= sum(transition_matrices[state,action,:])
    return transition_matrices

def random_matrices_ndiag_unif(dim, width=1):
    """
    Generates a random probability matrix with coefficient on the diagonals +/- width
    
    Example: 
    - width = 0 is a diagonal matrix
    - width = 1 is a tri-diagonal matrix
    """
    transition_matrices = np.zeros((dim, 2, dim))
    for action in [0, 1]:
        for w in range(-width, width+1):
            transition_matrices[:,action,:] += np.diag(np.random.rand(dim-abs(w)), k=w)
        for state in range(dim):
            transition_matrices[state,action,:] /= sum(transition_matrices[state,action,:])
    return transition_matrices

def random_matrices_tridiag(dim):
    """
    Make transition matrix modeled as Random Walk
    :param dim : int- dim of the transition matrix
    """
    transition_matrices= np.zeros((dim, 2, dim))
    for action in [0, 1]:
        d0 = np.random.uniform(0.2, 0.3, size=dim-2) # in order not to get disconnected chain
        d1 = np.random.uniform(0.35, 0.4, size=dim-2)
        d_1 = np.ones(dim-2) - (d0 + d1)
        p0 = np.random.uniform(0.2, 0.8)
        d0 = np.insert(d0, 0, p0)
        d1 = np.insert(d1, 0, 1-p0)
        pn = np.random.uniform(0.2, 0.8)
        d0 = np.insert(d0, dim-1, pn)
        d_1 = np.insert(d_1, dim-2, 1-pn)
        transition_matrices[:, action, :] = np.diag(d0) + np.diag(d1, k=1) + np.diag(d_1, k=-1)
        jumps = np.random.choice(range(dim), size=int(0.5*dim))
        for state in jumps:
            col = np.random.choice(range(dim))
            transition_matrices[state, action, col] = 0.1
            transition_matrices[state, action, state] -= 0.1
    return transition_matrices

def random_restless(dim, struct='dense', seed=None):
    np.random.seed(seed)
    return RestlessBandit.random_restless(dim, struct, seed)

def random_rested(dim, struct='dense', seed=None):
    return RestlessBandit.random_rested(dim, struct, seed)

def restless_bandit_from_P0P1_R0R1(P0, P1, R0, R1):
    return RestlessBandit.from_P0_P1_R0_R1(P0, P1, R0, R1)

def rested_bandit_from_P1_R1(P1, R1):
    dim = len(P1)
    P0 = np.eye(dim)
    R0 = np.zeros(dim)
    return RestlessBandit.from_P0_P1_R0_R1(P0, P1, R0, R1)

class RestlessBandit:
    """
    Class to manage restless bandit.
    """
    def __init__(self, transition_matrices, reward_vector):
        """
        Generate a bandit model from the transition_matrices and reward_vectors.
        - transition_matrices must be an array of size (dim, 2, dim)
        - reward_vectors must be of size (dim, 2)
        """
        self.transition_matrices = np.array(transition_matrices)
        self.reward_vector = np.array(reward_vector)
        dim = len(transition_matrices)
        assert (self.transition_matrices.shape == (dim,2,dim)
                and self.reward_vector.shape == (dim, 2)), "transition and rewards dimension are not consistent"
        self.indices = None
        self.indexable = None
        self.computed_for_discount = None

    @classmethod
    def random_restless(cls, dim, struct='dense', seed=None):
        """
        Create a random dense restless bandit of dimension "dim"
        """
        np.random.seed(seed)
        transition_matrices = random_matrix(dim, struct)
        reward_vector = random_rewards(dim)
        return cls(transition_matrices, reward_vector)

    @classmethod
    def random_rested(cls, dim, struct='dense', seed=None):
        """
        Create a random dense rested bandit of dimension "dim".

        A rested bandit is a restless bandit such that P0 = 0 and R0 = 0.
        """
        np.random.seed(seed)
        transition_matrices = random_matrix(dim, struct)
        reward_vector = random_rewards(dim)
        transition_matrices[:,0,:] = np.eye(dim)
        reward_vector[:,0] = 0
        return cls(transition_matrices, reward_vector)

    @classmethod
    def from_P0_P1_R0_R1(cls, P0, P1, R0, R1):
        """
        Create a restless bandit from the transition matrices.
        """
        dim = len(P0)
        transition_matrices= np.zeros((dim, 2, dim))
        reward_vector = np.zeros((dim, 2))
        transition_matrices[:,0,:] = P0
        transition_matrices[:,1,:] = P1
        reward_vector[:,0] = R0
        reward_vector[:,1] = R1
        return cls(transition_matrices, reward_vector)

    def get_P0P1R0R1(self):
        return self.transition_matrices[:,0,:], self.transition_matrices[:,1,:], self.reward_vector[:,0], self.reward_vector[:,1]

    def transition_matrix_from_action(self, action):
        """
        Return the transition matrix for the corresponding "action" (action should be 0 or 1)
        """
        assert action == 0 or action == 1, "Action should be 0 or 1"
        return self.transition_matrices[:,action,:]

    def transition_matrix_from_policy(self, policy):
        """
        Return the transition matrix for the corresponding "action" (action should be 0 or 1)
        """
        dim = len(self.transition_matrices)
        transition_matrix = np.zeros((dim,dim), dtype=np.double)
        assert len(policy)==dim, "Policy size does not match matrix size {}!={}".format(len(policy, dim))
        for i in range(dim):
            transition_matrix[i,:] = self.transition_matrices[i,action,:]
        return transition_matrix

    def compute_whittle_indices(self, check_indexability=True, discount=1, number_of_updates='2n**0.1'):
        """
        Compute the whittle index and stores it to avoid further recomputation.
        """
        if self.indices is None or (check_indexability and self.indexable is None) or discount != self.computed_for_discount:
            self.computed_for_discount = discount
            indexable, self.indices = whittle.compute_whittle_indices(self.transition_matrices[:, 0, :], self.transition_matrices[:, 1, :],
                    self.reward_vector[:, 0], self.reward_vector[:, 1],
                    check_indexability=check_indexability, beta=discount, number_of_updates=number_of_updates)
            if check_indexability:
                self.indexable = indexable               

    def whittle_indices(self, check_indexability=True, discount=1, number_of_updates='2n**0.1'):
        """
        Returs the whittle indices (or gittins if discount < 1 and the bandit is rested)
        """
        self.compute_whittle_indices(check_indexability, discount, number_of_updates)
        return self.indices

    def is_rested_bandit(self):
        """
        Returns True if the bandit is a rested bandit (i.e. P0 = Id and R0 = 0)
        """
        dim = self.transition_matrices.shape[0]
        return np.allclose(np.eye(dim), self.transition_matrices[:,0,:]) and np.allclose(self.reward_vector[:,0], np.zeros(dim))

    def gittins_indices(self, discount, number_of_updates='2n**0.1'):
        """
        Returns the Gittins indices. This function needs the bandit to be rested
        """
        assert self.is_rested_bandit(), "The bandit needs to be rested"
        assert discount < 1, "only works for a disount < 1"
        return self.whittle_indices(check_indexability=False, discount=discount, number_of_updates=number_of_updates)

    def is_indexable(self, discount=1):
        """
        Returns true of the model is indexable
        """
        self.compute_whittle_indices(check_indexability=True, discount=discount)
        return bool(self.indexable)
    
    def is_strongly_indexable(self, discount=1):
        """
        Returns true of the model is strongly indexable, where strongly indexable is defined in https://arxiv.org/pdf/2110.02128.pdf
        """
        self.compute_whittle_indices(check_indexability=True, discount=discount)
        return self.indexable == whittle.STRONGLY_INDEXABLE

