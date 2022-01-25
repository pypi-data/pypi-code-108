import numpy as np


def T1(ground_type):
    """

    Args:
        ground_type (str): Ground type (Α, Β, Γ, or Δ)

    Returns:
        float: The lower limit of the period of the constant spectral acceleration branch

    """
    data = {'Α': 0.10, 'Β': 0.15, 'Γ': 0.20, 'Δ': 0.20}
    return data[ground_type]


def T2(ground_type):
    """

        ground_type (str): Ground type (Α, Β, Γ, or Δ)

    Returns:
        float: The upper limit of the period of the constant spectral acceleration branch

    """
    data = {'Α': 0.40, 'Β': 0.60, 'Γ': 0.80, 'Δ': 1.20}
    return data[ground_type]


def Φd(T, α, γI,  T1, T2, q, η=1.0, θ=1.0, β0=2.5):
    """

    Args:
        T (float): The vibration period of a linear single-degree-of-freedom system
        α (float): The design ground acceleration (A=α*g)
        γI (float): Importance factor (0.85, 1.0, 1.15, 1.30 for Σ1, Σ2, Σ3 and Σ4)
        T1 (float): The lower limit of the period of the constant spectral acceleration branch
        T2 (float): The upper limit of the period of the constant spectral acceleration branch
        q (float): The behaviour factor
        η (float): Correction factor when damping is not 5%
        θ (float): Foundation effect factor
        β0 (float): Spectral amplification factor. Recommended value for β0 is 2.5

    Returns:
        float: Design spectrum. Given using the expressions:

        .. math::
            :nowrap:

            \\begin{eqnarray}
                coming \\\\
                soon \\\\
            \\end{eqnarray}

    """
    condlist = [T <= T1,
                T <= T2,
                T <= 4]
    choicelist = [γI * α * (1+(T/T1)*(η * θ * β0 / q - 1)),
                  γI * α * (η * θ * β0 / q),
                  γI * α * (η * θ * β0 / q) * (T2/T)**(2/3)]
    return np.select(condlist, choicelist)


def η(ζ):
    """

    Args:
        ζ (float): the viscous damping ratio of the structure[%]

    Returns:
        float: The value of the damping correction factor. Given using the expressions:

        .. math::
            η = \sqrt{\dfrac{7}{2+ζ}} \ge 0.55
    """

    return (7. / (2. + ζ)) ** 0.5

