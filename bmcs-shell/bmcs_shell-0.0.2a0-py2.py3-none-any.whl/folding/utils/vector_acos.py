'''
Created on Aug 28, 2014

@author: rch
'''

import numpy as np


def get_cos_theta(a, b):
    r'''Get the cosine of an angle between two vectors :math:`a` and :math:`b`

    .. math::
        \gamma_c =
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
    ab = np.einsum('...d,...d->...', a, b)
    sqrt_aa = np.sqrt(np.einsum('...d,...d->...', a, a))
    sqrt_bb = np.sqrt(np.einsum('...d,...d->...', b, b))
    c_ab = ab / (sqrt_aa * sqrt_bb)
    return c_ab


def get_cos_theta_du(a, a_du, b, b_du):
    r'''Get the derivatives of directional cosines
    between two vectors :math:`a` and :math:`b`.

    Given two arrays (n-dimensional) of vectors :math:`a, b` and their
    derivatives a_du and b_du with respect to the nodal displacments du
    return the derivatives of the cosine between mutual angles theta between
    a and b with respect to the node displacement du.

    .. math::
        \pard{ \gamma_c }
            {u_{Ie}}
        =
        \frac{1}
            { \left( \norm{a} \norm{b} \right)^2 }
        \left[
            \pard{ \left( a_d  b_d \right)}
                {u_{Ie}}
            \left( \norm{a} \norm{b} \right)
            -
            \pard{ \left( \norm{a} \norm{b} \right) }
                {u_{Ie}} \;
            \left( a_d b_d \right)
        \right]

    By factoring out the term
    :math:`\left( \norm{ a } \norm{ b } \right)`
    the expression reduces to a form

    .. math::
        \pard{ \gamma_c }
            {u_{Ie}}
        =
        \frac{1}
            { \norm{a}\norm{b}  }
        \left[
            \pard{ \left(a_d  b_d \right)}
                {u_{Ie}}
            -
            \pard{ \left( \norm{a}\norm{b} \right) }
                {u_{Ie}}\;
            \gamma_c
        \right]
        :label: gamma_du

    The terms with derivatives can be further elaborated to

    .. math::
        \pard{ \left(a_d  b_d \right)}
            {u_{Ie}}
        =
        \pard{a_d }
            {u_{Ie}} \;
        b_d
        +
        \pard{b_d }{u_{Ie}} \;
        a_d
        \;\;\mathrm{and}\;\;
        \pard{\left( \norm{a}\norm{b}\right) }
            {u_{Ie}}
        =
        \pard{ \norm{a} }
            {u_{Ie}} \;
        \norm{b}
        +
        \pard{ \norm{b}  }
            {u_{Ie}}\;
        \norm{a}

    The derivative of a vector norm in a summation form can be rewritten as

    .. math::
        \pard{\norm{a}}
            {u_{Ie}}
        =
        \pard{ \sqrt{ a_d a_d } }
            {u_{Ie}}
        =
        \frac{1}
            {\sqrt{ a_d a_d } }
        \left(
            \pard{a_{d}}
                {u_{Ie}}
            a_{d}
        \right)

    The corresponding code for a vectoried evaluation for the supplied
    multidimensional arrays of
    ``a, a_du, b, b_du`` looks as follows::

        ab_du = np.einsum('...dIe,...d->...Ie', a_du, b) + np.einsum('...dIe,...d->...Ie', b_du, a)
        sqrt_aa_du = 1 / sqrt_aa * np.einsum('...dIe,...d->...Ie', a_du, a)
        sqrt_bb_du = 1 / sqrt_bb * np.einsum('...dIe,...d->...Ie', b_du, b)
        sqrt_aa_x_sqrt_bb_du = (np.einsum(...Ie,...->...Ie', sqrt_aa_du, sqrt_bb) +
                                np.einsum(...Ie,...->...Ie', sqrt_bb_du, sqrt_aa)
        gamma_du = 1 / sqrt_aa_x_sqrt_bb * (ab_du - sqrt_aa_x_sqrt_bb_du * gamma)

    '''
    ab = np.einsum('...d,...d->...', a, b)
    norm_a = np.sqrt(np.einsum('...d,...d->...', a, a))
    norm_b = np.sqrt(np.einsum('...d,...d->...', b, b))
    norm_a_x_norm_b = norm_a * norm_b
    gamma = ab / norm_a_x_norm_b

    ab_du = (np.einsum('...eId,...d->...Ie', a_du, b) +
             np.einsum('...eId,...d->...Ie', b_du, a))
    gamma_norm_a_du_x_norm_b = np.einsum('...,...eId,...d->...Ie',
                                         gamma * norm_b / norm_a, a_du, a)
    gamma_norm_b_du_x_norm_a = np.einsum('...,...eId,...d->...Ie',
                                         gamma * norm_a / norm_b, b_du, b)
    gamma_norm_a_x_norm_b_du = (gamma_norm_a_du_x_norm_b +
                                gamma_norm_b_du_x_norm_a)
    gamma_du = np.einsum('...,...Ie->...Ie',
                         1. / norm_a_x_norm_b,
                         (ab_du - gamma_norm_a_x_norm_b_du))

    return gamma_du


def get_cos_theta_du2(a, a_du, b, b_du):
    r'''Given two arrays (n-dimensional) of vectors a, b and their
    derivatives a_du and b_du with respect to the nodal displacments du
    return the derivatives of the mutual angles theta between
    a and b with respect to the node displacement du.
    '''
    ab = np.einsum('...i,...i->...', a, b)
    sqrt_aa = np.sqrt(np.einsum('...i,...i->...', a, a))
    sqrt_bb = np.sqrt(np.einsum('...i,...i->...', b, b))
    sqrt_aa_x_sqrt_bb = sqrt_aa * sqrt_bb
    gamma = ab / sqrt_aa_x_sqrt_bb
    ab_du = (np.einsum('...iKj,...i->...Kj', a_du, b) +
             np.einsum('...iKj,...i->...Kj', b_du, a))

    gamma_bb__aa = gamma * sqrt_bb / sqrt_aa
    gamma_aa__bb = gamma * sqrt_aa / sqrt_bb
    gamma_aa_bb_du = (np.einsum('...,...iKj,...i->...Kj',
                                gamma_bb__aa, a_du, a) +
                      np.einsum('...,...iKj,...i->...Kj',
                                gamma_aa__bb, b_du, b))

    gamma_du = np.einsum(
        '...,...Kj->...Kj', 1. / sqrt_aa_x_sqrt_bb, (ab_du - gamma_aa_bb_du))
    return gamma_du


def get_theta(a, b):
    r'''
    Get the angle between two vectors :math:`a` and :math:`b`.
    Using the function ``get_cos_theta(a,b)`` delivering the cosine of the angle
    this method just evaluates the expression

    .. math::
        \theta = \arccos{( \gamma_c )}
        :label: theta

    realized by calling the vectorized numpy function::

        theta = np.arccos(gamma_c)

    '''
    gamma_c = get_cos_theta(a, b)
    theta = np.arccos(gamma_c)
    return theta


def get_theta_du(a, a_du, b, b_du):
    r'''
    Get the derivative of the angle between two vectors :math:`a` and :math:`b`
    with respect to ``du`` using the supplied chain derivatives ``a_du, b_du``.
    Using the function ``get_cos_theta(a,b)`` delivering the cosine of the angle
    this method evaluates the expression

    .. math::
        \frac{\partial \theta}{\partial u_{Ie}}
        =
        \frac{\partial \theta}{\partial \gamma_c}
        \cdot
        \frac{\partial \gamma_c}{\partial u_{Ie}}
        :label: theta_du

    where

    .. math::

        \frac{\partial \theta}{\partial \gamma_c}
        =
        - \frac{1}{ \sqrt{ 1 - \gamma_c^2}}

    ::

        theta_du = - 1 / np.sqrt(1 - gamma * gamma) * gamma_du
    '''
    gamma = get_cos_theta(a, b)
    gamma_du = get_cos_theta_du(a, a_du, b, b_du)
    theta_du = np.einsum(
        '...,...Ie->...Ie', -1. / np.sqrt(1. - gamma ** 2), gamma_du)
    return theta_du
