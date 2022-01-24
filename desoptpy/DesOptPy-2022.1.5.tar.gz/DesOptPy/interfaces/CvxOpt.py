"""
http://cvxopt.org/userguide/index.html
http://cvxopt.org/userguide/solvers.html
"""
import cvxopt


def CvxOptOpt(self, x0, xL, xU, SysEq):
    def F(x=None, z=None):

        return f, Df, H

    cvxopt.solvers.cp(F)
