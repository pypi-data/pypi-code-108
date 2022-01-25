def μ(Μ, b, h, fc):
    """

    Args:
        Μ (float): Moment
        b (float): Section width
        h (float): Section depth (or effective depth)
        fc (float): Concrete compressive strength

    Returns:
        float: Normalised moment

    """
    return Μ / (b * h**2 * fc)



def ν(N, b, h, fc):
    """

    Args:
        N (float): Axial force
        b (float): Section width
        h (float): Section depth (or effective depth)
        fc (float): Concrete compressive strength

    Returns:
        float: Normalised axial force

    """
    return N / (b * h * fc)
