"""
`pytest` testing framework file for ASCII85 process
"""

import satnogsdecoders.decoder as decoder
from tests.shared_methods import check_type, load_objects


def test_answer():  # pylint: disable=too-many-locals
    """
    `pytest` entry point
    """

    testdata = bytearray([
        0x54, 0x68, 0x69, 0x73, 0x20, 0x69, 0x73, 0x20, 0x61, 0x20, 0x74, 0x65,
        0x73, 0x74, 0x2e, 0x0a, 0x3c, 0x2b, 0x6f, 0x75, 0x65, 0x2b, 0x44, 0x47,
        0x6d, 0x3e, 0x40, 0x33, 0x42, 0x5a, 0x27, 0x46, 0x2a, 0x27, 0x23, 0x0a
    ])
    testdata_keys = 2
    packets = [testdata]
    dut = 'Ascii85test'
    result = []

    for frame in packets:
        result = load_objects(decoder, dut, frame)
        count = check_type(result)
        if frame == testdata:
            assert count == testdata_keys
            assert bytearray(result['decoded'], 'ASCII') == testdata[0:15]
            assert bytearray(result['encoded'], 'ASCII') == testdata[16:35]
