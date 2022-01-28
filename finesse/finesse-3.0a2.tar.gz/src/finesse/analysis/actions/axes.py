"""Axes Actions such as xaxis, noaxais, etc."""

from .sweep import Sweep, get_sweep_array
import re


class Noxaxis(Sweep):
    def __init__(self, pre_step=None, post_step=None, name="noxaxis"):
        super().__init__(name=name, pre_step=pre_step, post_step=post_step)


class XNaxis(Sweep):
    def __init__(
        self, *args, relative=False, pre_step=None, post_step=None, name="XNaxis"
    ):
        if len(args) % 5 != 0:
            raise Exception(
                f"XNaxis arguments must come in groups of five: parameter, mode, start, stop, steps not {args}"
            )
        self.relative = relative
        self.N = len(args) // 5

        if self.N == 0:
            raise Exception("XNaxis requires at least one axis to be specified")
        # Here we map the XNaxis arguments to the Sweep inputs
        self.__set_args = args
        new_args = []

        for i in range(0, len(args), 5):
            new_args.append(args[i + 0])
            new_args.append(
                get_sweep_array(args[i + 2], args[i + 3], args[i + 4], args[i + 1])
            )
            new_args.append(relative)
        super().__init__(*new_args, pre_step=pre_step, post_step=post_step, name=name)

    def __getattr__(self, key):
        res = re.match("(parameter|mode|start|stop|steps)([0-9]*)", key)
        if res is None:
            super().__getattribute__(key)
        else:
            grp = res.groups()
            N = 1 if grp[1] == "" else int(grp[1])
            if N == 0:
                raise Exception("Specify an axes greater than 0")
            if N > self.N:
                raise Exception(f"This xaxis does not have {N} axes")
            idx = 5 * (N - 1)
            if grp[0] == "parameter":
                return self.__set_args[idx + 0]
            elif grp[0] == "mode":
                return self.__set_args[idx + 1]
            elif grp[0] == "start":
                return self.__set_args[idx + 2]
            elif grp[0] == "stop":
                return self.__set_args[idx + 3]
            elif grp[0] == "steps":
                return self.__set_args[idx + 4]


class Xaxis(XNaxis):
    def __init__(
        self,
        parameter,
        mode,
        start,
        stop,
        steps,
        relative=False,
        *,
        pre_step=None,
        post_step=None,
        name="xaxis",
    ):
        super().__init__(
            parameter,
            mode,
            start,
            stop,
            steps,
            relative=relative,
            pre_step=pre_step,
            post_step=post_step,
            name=name,
        )


class X2axis(XNaxis):
    def __init__(
        self,
        parameter1,
        mode1,
        start1,
        stop1,
        steps1,
        parameter2,
        mode2,
        start2,
        stop2,
        steps2,
        relative=False,
        *,
        pre_step=None,
        post_step=None,
        name="x2axis",
    ):
        super().__init__(
            parameter1,
            mode1,
            start1,
            stop1,
            steps1,
            parameter2,
            mode2,
            start2,
            stop2,
            steps2,
            relative=relative,
            pre_step=pre_step,
            post_step=post_step,
            name=name,
        )


class X3axis(XNaxis):
    def __init__(
        self,
        parameter1,
        mode1,
        start1,
        stop1,
        steps1,
        parameter2,
        mode2,
        start2,
        stop2,
        steps2,
        parameter3,
        mode3,
        start3,
        stop3,
        steps3,
        relative=False,
        *,
        pre_step=None,
        post_step=None,
        name="x3axis",
    ):
        super().__init__(
            parameter1,
            mode1,
            start1,
            stop1,
            steps1,
            parameter2,
            mode2,
            start2,
            stop2,
            steps2,
            parameter3,
            mode3,
            start3,
            stop3,
            steps3,
            relative=relative,
            pre_step=pre_step,
            post_step=post_step,
            name=name,
        )
