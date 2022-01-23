try:
    # framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'omfit_classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise

from omfit_classes.omfit_nc import OMFITnc
from omfit_classes.omfit_eqdsk import OMFITgeqdsk

__all__ = ['OMFITjsolver']


class OMFITjsolver(OMFITnc):
    """
    Class used to parse the ouput of the jsolver equilibirum code
    """

    def to_geqdsk(self, B0, R0, ip, resolution, shot=0, time=0, RBFkw={}):
        """
        maps jsolver solution to a gEQDSK file

        :param B0: scalar vacuum B toroidal at R0

        :param R0: scalar R where B0 is defined

        :param ip: toroidal current

        :param resolution: g-file grid resolution

        :param shot: used to set g-file string

        :param time: used to set g-file string

        :param RBFkw: keywords passed to internal Rbf interpolator

        :return: OMFITgeqdsk object
        """

        return OMFITgeqdsk('g%06d.%05d' % (shot, time)).from_rz(
            self['x']['data'],
            self['z']['data'],
            self['psival']['data'],
            self['p']['data'],
            self['f']['data'],
            self['q']['data'],
            B0,
            R0,
            ip,
            resolution,
            RBFkw=RBFkw,
        )


############################################
if __name__ == '__main__':
    test_classes_main_header()

    j = OMFITjsolver(OMFITsrc + '/../samples/jsolver_eqdsk_11MA_A3_R4.5.cdf')
    g = j.to_geqdsk(8.0, 4.5, 11e6, 65)
