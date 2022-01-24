'''
Created on Aug 28, 2014

@author: rch
'''

import numpy as np



# Kronecker delta
DELTA = np.zeros((3, 3,), dtype='f')
DELTA[(0, 1, 2), (0, 1, 2)] = 1

# Levi Civita symbol
EPS = np.zeros((3, 3, 3), dtype='f')
EPS[(0, 1, 2), (1, 2, 0), (2, 0, 1)] = 1
EPS[(2, 1, 0), (1, 0, 2), (0, 2, 1)] = -1


def get_sin_theta(a, b):
    r'''Get the cosine of an angle between two vectors :math:`a` and :math:`b`

    .. math::
        \gamma_s =
        \cos{(\theta)}
        =
        \frac{ \dotp{a}{b} }
            { \norm{a} \norm{b} }
        =
        \frac{a_d b_d}
            { \sqrt{a_d a_d} \sqrt{b_d b_d} }
        :label: gamma

    It is convenient to implement this function in a vectorized
    form so that two arrays of vectors can be supplied and
    evaluated using several sum-product evaluations over their
    last index :math:`d` standing for the spatial dimension of
    the vectors.

    Such an evaluation can be conveniently done using the
    method
    `numpy.einsum(subscript_mappings, *operands)
    <http://docs.scipy.org/doc/numpy/reference/generated/numpy.einsum.html>`_.
    Given two compatible arrays (n-dimensional) :math:`a`
    and :math:`b` of vectors with last index :math:`d`
    labeling their spatial component the array :math:`\gamma_c`
    of angle cosines between each pair of vectors in :math:`a`, :math:`b`.
    gets calculated as::

        ab = np.einsum('...d,...d->...', a, b)
        sqrt_aa = np.sqrt(np.einsum('...d,...d->...', a, a))
        sqrt_bb = np.sqrt(np.einsum('...d,...d->...', b, b))
        sqrt_aa_x_sqrt_bb = sqrt_aa * sqrt_bb
        gamma = ab / sqrt_aa_x_sqrt_bb)

    '''
    c = np.einsum('...i,...j,...kij->...k', a, b, EPS)
    mag_c = np.einsum('...i,...i->...', c, c)
    print('c', c, 'mag_c', mag_c)
    mag_aa_bb = np.einsum('...i,...i,...j,...j->...', a, a, b, b)
    print('mag_ab_bb', mag_aa_bb)
    sin_theta = np.sqrt(mag_c / mag_aa_bb)

    return sin_theta


if __name__ == '__main__':

    # end_doc

    a = np.array([[1, 0, 0], [1, 0, 0], [1, 0, 0]], dtype='f')
    b = np.array([[0, 1, 0], [1, 1, 0], [1, -1, 0]], dtype='f')

    print('gamma', get_sin_theta(a, b))
