# Copyright 2021 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__metaclass__ = type

from testtools.matchers import (
    Equals,
    Is,
    MatchesDict,
    MatchesListwise,
    )


class RanCommand(MatchesListwise):

    def __init__(self, args, echo=None, cwd=None, input_text=None,
                 stdout=None, stderr=None, get_output=None,
                 universal_newlines=None, **env):
        kwargs_matcher = {}
        if echo is not None:
            kwargs_matcher["echo"] = Is(echo)
        if cwd:
            kwargs_matcher["cwd"] = Equals(cwd)
        if input_text:
            kwargs_matcher["input_text"] = Equals(input_text)
        if stdout is not None:
            kwargs_matcher["stdout"] = Equals(stdout)
        if stderr is not None:
            kwargs_matcher["stderr"] = Equals(stderr)
        if get_output is not None:
            kwargs_matcher["get_output"] = Is(get_output)
        if universal_newlines is not None:
            kwargs_matcher["universal_newlines"] = Is(universal_newlines)
        if env:
            kwargs_matcher["env"] = MatchesDict(
                {key: Equals(value) for key, value in env.items()})
        super(RanCommand, self).__init__(
            [Equals((args,)), MatchesDict(kwargs_matcher)])


class RanAptGet(RanCommand):

    def __init__(self, *args):
        super(RanAptGet, self).__init__(["apt-get", "-y"] + list(args))


class RanSnap(RanCommand):

    def __init__(self, *args, **kwargs):
        super(RanSnap, self).__init__(["snap"] + list(args), **kwargs)


class RanBuildCommand(RanCommand):

    def __init__(self, args, **kwargs):
        kwargs.setdefault("cwd", "/build")
        kwargs.setdefault("LANG", "C.UTF-8")
        kwargs.setdefault("SHELL", "/bin/sh")
        super(RanBuildCommand, self).__init__(args, **kwargs)
