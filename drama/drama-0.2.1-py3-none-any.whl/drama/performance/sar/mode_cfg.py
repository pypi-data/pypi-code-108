import numpy as np

__author__ = "Paco Lopez Dekker"
__email__ = "F.LopezDekker@tudeft.nl"


class SARModeFromCfg(object):
    """ """

    def __init__(self, conf, modename="stripmap"):
        try:
            mcnf = getattr(conf, modename)
            # inc
            self.incs = np.zeros((mcnf.inc_near.size, 2))
            self.incs[:, 0] = mcnf.inc_near
            self.incs[:, 1] = mcnf.inc_far
            self.prfs = mcnf.PRF
            self.proc_bw = mcnf.proc_bw
            self.steering_rate = np.zeros(self.incs.shape[0])
            self.steering_rate[:] = np.radians(mcnf.steering_rate)
            self.burst_length = np.ones_like(self.steering_rate)
            self.burst_length[:] = mcnf.burst_length
            self.short_name = mcnf.short_name
            self.proc_tap = np.ones_like(self.steering_rate)
            self.pulse_length = mcnf.pulse_length
            self.pulse_bw = mcnf.pulse_bw
            if hasattr(mcnf, "proc_tapering"):
                self.proc_tap[:] = mcnf.proc_tapering
        except:
            mesg = "Mode %s is not defined" % modename
            raise ValueError(mesg)

    def inc2swath(self, incin, degree=True, take_fisrt=True):
        """

        Parameters
        ----------
        incin : ndarray
            indicent angles
        degree :
            True if incin is in degree, else radians are assumed (Default value = True)
        take_first :
            if True it will select the lowest subswath if the angle is included
            in more than one. If False it will take the highest one.
        take_fisrt :
             (Default value = True)

        Returns
        -------

        """
        if degree:
            incs = incin
        else:
            incs = np.degrees(incin)
        swaths = np.zeros_like(incs, dtype=np.int)
        swthiterator = range(self.prfs.size)
        if take_fisrt:
            swthiterator = reversed(swthiterator)
        for swth_ind in swthiterator:
            hits = np.where(
                np.logical_and(
                    incs > self.incs[swth_ind, 0],
                    incs <= self.incs[swth_ind, 1],
                )
            )
            swaths[hits] = (
                swth_ind + 1
            )  # The zero is kept for points outside all swathes

        return swaths
