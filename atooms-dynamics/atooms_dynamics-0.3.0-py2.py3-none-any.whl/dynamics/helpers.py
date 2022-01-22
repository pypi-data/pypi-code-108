import warnings
import numpy


def mean_square_displacement(system, another):
    """Compute MSD between the particles of one `system` and `another`"""
    warnings.warn('mean_square_displacement() is deprecated', DeprecationWarning)
    displ = []
    for pi, pj in zip(system.particle, another.particle):
        rij = pi.distance(pj, folded=False)
        displ.append(numpy.dot(rij, rij))
    dr2 = sum(displ) / len(system.particle)
    return dr2**0.5

# def periodic_boundary_conditions(r, box):
#     return numpy.where(numpy.abs(r) > box / 2, r - numpy.sign(r) * box, r)
