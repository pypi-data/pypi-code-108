import oftest, pytest
from os import path
import numpy as np

def find_value_in_file(filename,keyword):
    with open(filename) as f:
        if keyword in f.read():
            return True
        return False

@pytest.fixture()
def load_parser_controlDict():
    dir_name = path.dirname(path.abspath(__file__))
    controlDict = path.join(dir_name,"controlDict")
    return oftest.Pyfoam_parser(controlDict)

def test_controlDict_value(load_parser_controlDict):
    parser = load_parser_controlDict
    assert parser.value("application") == "interIsoFoam"

def test_controlDict_setAndWrite(load_parser_controlDict):
    parser = load_parser_controlDict
    val = "some-unique-value"
    parser.set("writeControl",val)
    parser.writeFile()
    assert find_value_in_file(parser.filename, val)

def test_controlDict_reset(load_parser_controlDict):
    parser = load_parser_controlDict
    parser.set("writeControl","adjustableRunTime")
    parser.writeFile()
    assert find_value_in_file(parser.filename, "adjustableRunTime")


@pytest.fixture()
def load_parser_transportProperties():
    dir_name = path.dirname(path.abspath(__file__))
    transportProperties = path.join(dir_name,"transportProperties")
    return oftest.Pyfoam_parser(transportProperties)


def test_transportProperties_value(load_parser_transportProperties):
    parser = load_parser_transportProperties
    assert parser.value("water/transportModel") == "Newtonian"


def test_transportProperties_setAndWrite(load_parser_transportProperties):
    parser = load_parser_transportProperties
    val = "some-unique-value"
    parser.set("water/transportModel",val)
    parser.writeFile()
    assert find_value_in_file(parser.filename, val)

def test_transportProperties_reset(load_parser_transportProperties):
    parser = load_parser_transportProperties
    parser.set("water/transportModel","Newtonian")
    parser.writeFile()
    assert find_value_in_file(parser.filename, "Newtonian")