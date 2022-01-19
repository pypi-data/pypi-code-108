#!/usr/bin/python3
import sys

import pytest

sys.path.extend([f"{sys.path[0]}/..", f"{sys.path[0]}/../.."])
from niceshell import core


class TestCore:
    def test_expose_tilde(self):
        expose_tilde = core.expose_tilde
        quotes_wrapper = core.quotes_wrapper

        # Errors
        # quoted_path must be str
        with pytest.raises(TypeError):
            expose_tilde(1)
        with pytest.raises(TypeError):
            expose_tilde([])
        with pytest.raises(TypeError):
            expose_tilde([''])

        # Asserts
        assert expose_tilde(quotes_wrapper("~")) == '~'
        assert expose_tilde(quotes_wrapper("~/")) == '~/""'
        assert expose_tilde(quotes_wrapper("~/dir")) == '~/"dir"'
        assert expose_tilde(quotes_wrapper("dir ~/")) == '"dir ~/"'
        assert expose_tilde(quotes_wrapper('dir "~/')) == R'"dir \"~/"'

    def test_normalize_short_and_long_args(self):
        normalize = core.normalize_short_and_long_args
        ShortArgsOption = core.ShortArgsOption
        # Errors
        # short_args' type must be str or Iterable[str].
        with pytest.raises(TypeError):
            normalize(1)
        with pytest.raises(TypeError):
            normalize([1])

        # long_args' type must be Iterable[str].
        with pytest.raises(TypeError):
            normalize('', '')
        with pytest.raises(TypeError):
            normalize('', [1])

        # No spaces are allowed in short args which are TOGETHER
        with pytest.raises(ValueError):
            normalize(' ')
        with pytest.raises(ValueError):
            normalize("-a -b")

        # (Iterable[str]) Short args which are TOGETHER must be 1 char. long
        with pytest.raises(ValueError):
            normalize(["ab"], [])
        with pytest.raises(ValueError):
            normalize(["-ab", 'c'])

        # Invalid value of short_args_option.
        with pytest.raises(ValueError):
            normalize([], [], True)

        # No args
        assert normalize() == ''

        # (str) Short args are TOGETHER (default)
        assert normalize("a") == "-a"
        assert normalize("-a") == "-a"
        assert normalize("abcd") == "-abcd"
        assert normalize("-abcd") == "-abcd"
        # (str) Short args are APART
        assert normalize("a", [], ShortArgsOption.APART) == "-a"
        assert normalize("-a", [], ShortArgsOption.APART) == "-a"
        assert normalize("abcd", [], ShortArgsOption.APART) == "-a -b -c -d"
        assert normalize("-abcd", [], ShortArgsOption.APART) == "-a -b -c -d"
        # (str) Short args are apart with NO_DASH
        assert normalize("a", [], ShortArgsOption.NO_DASH) == "a"
        assert normalize("-a", [], ShortArgsOption.NO_DASH) == "a"
        assert normalize("abcd", [], ShortArgsOption.NO_DASH) == "a b c d"
        assert normalize("-abcd", [], ShortArgsOption.NO_DASH) == "a b c d"
        # (Iterable[str]) Short args (edge cases)
        assert normalize([]) == ''
        assert normalize(()) == ''
        assert normalize({}) == ''
        assert normalize(set()) == ''
        assert normalize(['']) == ''
        assert normalize(['', '']) == ''
        # (Iterable[str]) Short args are TOGETHER (default)
        assert normalize(["a"]) == "-a"
        assert normalize(["-a"]) == "-a"
        assert normalize(["a", "b", "c", "d"]) == "-abcd"
        assert normalize(["-a", "-b", "c", "d"]) == "-abcd"
        # (Iterable[str]) Short args are APART
        assert normalize(["a"], [], ShortArgsOption.APART
                         ) == "-a"
        assert normalize(["-a"], [], ShortArgsOption.APART
                         ) == "-a"
        assert normalize(["a", "b", "c", "d"], [], ShortArgsOption.APART
                         ) == "-a -b -c -d"
        assert normalize(["-a", "-b", "c", "d"], [], ShortArgsOption.APART
                         ) == "-a -b -c -d"
        assert normalize(["-I /path/to/smth", "-0", "P /tmp", "q"],
                         [], ShortArgsOption.APART
                         ) == "-I /path/to/smth -0 -P /tmp -q"
        # (Iterable[str]) Short args are apart with NO_DASH
        assert normalize(["a"], [], ShortArgsOption.NO_DASH
                         ) == "a"
        assert normalize(["-a"], [], ShortArgsOption.NO_DASH
                         ) == "a"
        assert normalize(["a", "b", "c", "d"], [], ShortArgsOption.NO_DASH
                         ) == "a b c d"
        assert normalize(["-a", "-b", "-c", "-d"], [], ShortArgsOption.NO_DASH
                         ) == "a b c d"
        assert normalize(["I=/path/to/smth", "P=/tmp"],
                         [], ShortArgsOption.NO_DASH
                         ) == "I=/path/to/smth P=/tmp"

        # (Iterable[str]) Long args
        assert normalize([], ["a"]) == "--a"
        assert normalize([], ["-a"]) == "--a"
        assert normalize([], ["--a"]) == "--a"
        assert normalize([], ["argument1"]) == "--argument1"
        assert normalize([], ["--argument1"]) == "--argument1"
        assert normalize(
            [],
            ["argument1", "argument2"]) == "--argument1 --argument2"
        assert normalize(
            [],
            ["--argument1", "--argument2"]) == "--argument1 --argument2"
        assert normalize(
            [],
            ["quiet", "--color=always"]) == "--quiet --color=always"

        # (Iterable[str]) Shoart and Long args
        assert normalize("qvv", ["all", "color=always"],
                         ShortArgsOption.TOGETHER
                         ) == "-qvv --all --color=always"
        assert normalize(
            ["-I /path/to/smth", "-0", "P /tmp", "q"],
            ["quiet", "--color=always"],
            ShortArgsOption.APART
        ) == "-I /path/to/smth -0 -P /tmp -q --quiet --color=always"
        assert normalize(
            ["if=/path/to/smth", "of=/dev/sda1"],
            ["version", "--help"],
            ShortArgsOption.NO_DASH
        ) == "if=/path/to/smth of=/dev/sda1 --version --help"

    def test_quotes_wrapper(self):
        wrapper = core.quotes_wrapper
        # Errors
        # path's type must be str or Iterable[str].
        with pytest.raises(TypeError):
            wrapper(1)
        with pytest.raises(TypeError):
            wrapper([])
        with pytest.raises(TypeError):
            wrapper([1])

        # Quotes
        assert wrapper('') == '""'
        assert wrapper(' ') == '" "'
        assert wrapper(set(' ')) == '" "'
        assert wrapper(['', '']) == '"" ""'
        assert wrapper('file.txt') == R'"file.txt"'
        assert wrapper('The "name".pdf') == R'"The \"name\".pdf"'
        assert wrapper("The 'name'.pdf") == R'''"The 'name'.pdf"'''
        assert wrapper('''The "na'me".pdf''') == R'''"The \"na'me\".pdf"'''
        assert wrapper(
            ["file.txt", 'The "name".pdf', "The 'name'.pdf"]
        ) == R'''"file.txt" "The \"name\".pdf" "The 'name'.pdf"'''

    def test_shell(self):
        shell = core.shell

        # Errors
        # command's type must be str or Iterable[str].
        with pytest.raises(TypeError):
            shell(1)
        with pytest.raises(TypeError):
            shell([])
        with pytest.raises(TypeError):
            shell([1])

    def test_Shell(self):
        Shell = core.Shell

        # Errors
        # command's type must be str or Iterable[str].
        with pytest.raises(TypeError):
            Shell(1)
        with pytest.raises(TypeError):
            Shell([])
        with pytest.raises(TypeError):
            Shell([1])


if __name__ == "__main__":
    pytest.main()
