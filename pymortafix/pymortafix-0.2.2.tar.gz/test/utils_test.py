import sys
from io import StringIO
from re import match

from pymortafix.utils import multisub, strict_input

# --- utility


def force_input(inputs):
    sys.stdin = StringIO(inputs)


# --- multisub


def test_multisub_no_seq_no_overlap():
    string = "Test 42"
    sub_dict = {}
    assert multisub(sub_dict, string) == "Test 42"
    sub_dict = {"st": "ST"}
    assert multisub(sub_dict, string) == "TeST 42"
    sub_dict = {r"\s": "_", r"\d+": "@"}
    assert multisub(sub_dict, string) == "Test_@"


def test_multisub_no_seq_overlap():
    string = "Test - Overlap"
    sub_dict = {"-": " ", r"\s+": "_"}
    assert multisub(sub_dict, string) == "Test_ _Overlap"
    sub_dict = {r"\s+": "_", "-": " "}
    assert multisub(sub_dict, string) == "Test_ _Overlap"


def test_multisub_seq():
    string = "Test -  Sequential  - Not  Bad"
    sub_dict = {r"-": ":", r"\s+:\s+": "-", r"\s+": "_"}
    assert multisub(sub_dict, string, sequential=True) == "Test-Sequential-Not_Bad"


# --- strict input


def test_strictinput_easy():
    force_input("test")
    inp = strict_input("Input: ")
    assert inp == "test"


def test_strictinput_choices():
    force_input("test\nup")
    inp = strict_input("Input: ", choices=("up", "down"))
    assert inp == "up"
    force_input("left\ndown\nup")
    inp = strict_input("Input: ", choices=("up", "down"))
    assert inp == "down"


def test_strictinput_regex():
    force_input("test-2\ntest-42")
    inp = strict_input("Input: ", regex=r"test-\d+")
    assert inp == "test-2"
    force_input("test\ntest-42")
    inp = strict_input("Input: ", regex=r"test-\d+")
    assert inp == "test-42"


def test_strictinput_check():
    force_input("uno\n1\n42")
    inp = strict_input("Input: ", check=lambda x: match(r"\d+$", x) and int(x) % 2 == 0)
    assert inp == "42"
    force_input("1\n-10\n42")
    inp = strict_input("Input: ", check=lambda x: 2 ** int(x) > 1000)
    assert inp == "42"


def test_strictinput_choices_regex():
    force_input("test\nup\ntest-42")
    inp = strict_input("Input: ", choices=("up", "down"), regex=r"test-\d+")
    assert inp == "up"
    force_input("test\nleft\ntest-42")
    inp = strict_input("Input: ", choices=("up", "down"), regex=r"test-\d+")
    assert inp == "test-42"


def test_strictinput_choices_check():
    force_input("23\n3\n42")
    inp = strict_input("Input: ", choices=("3"), check=lambda x: int(x) % 2 == 0)
    assert inp == "3"
    force_input("23\n5\n42")
    inp = strict_input("Input: ", choices=("3"), check=lambda x: int(x) % 2 == 0)
    assert inp == "42"


def test_strictinput_regex_check():
    force_input("23\nu911\n42")
    inp = strict_input("Input: ", regex=r"u\d+", check=lambda x: int(x) % 2 == 0)
    assert inp == "u911"
    force_input("23\n911\n42")
    inp = strict_input("Input: ", regex=r"u\d+", check=lambda x: int(x) % 2 == 0)
    assert inp == "42"
