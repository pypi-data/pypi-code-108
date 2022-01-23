"""
`pytest` testing framework file for CAPE-1 decoder
"""

import pytest
import satnogsdecoders.decoder as decoder
from tests.shared_methods import load_objects


def test_answer():
    """
    `pytest` entry point
    """

    valid_packets = [
        [
            # Test payload type 1 (from
            # https://www.pe0sat.vgnet.nl/download/CAPE/cape-1_02-07-2020_1940UTC.PNG,
            # modified to make valid)
            b'K5USL19000EEEF00000000',
            {
                'callsign': 'K5USL',
                'pkt_type': '1',
                'mpb_voltage': 144,
                'hpb_voltage': 0,
                'battery_1_voltage': 238,
                'battery_2_voltage': 239,
                'battery_1_current_generated': 0,
                'battery_1_current_absorbed': 0,
                'battery_2_current_absorbed': 0,
                'battery_2_current_generated': 0
            }
        ],
        [
            # Test payload type 2 (from
            # https://www.pe0sat.vgnet.nl/download/CAPE/cape-1_02-07-2020_1940UTC.PNG)
            b'K5USL200FF1C151E0A1808F5',
            {
                'callsign': 'K5USL',
                'pkt_type': '2',
                'temp_battery_1': 0,
                'temp_px_face': -1,
                'temp_nx_face': 28,
                'temp_py_face': 21,
                'temp_ny_face': 30,
                'temp_pz_face': 10,
                'temp_nz_face': 24,
                'temp_rf_amp': 8,
                'temp_battery_2': -11
            }
        ],
        [
            # Test payload type 3 (from
            # https://www.pe0sat.vgnet.nl/download/CAPE/cape-1_02-07-2020_1940UTC.PNG,
            # modified to make valid)
            b'K5USL3009005000100',
            {
                'callsign': 'K5USL',
                'pkt_type': '3',
                'panel_px_face': 0,
                'panel_nx_face': 144,
                'panel_py_face': 5,
                'panel_ny_face': 0,
                'panel_pz_face': 1,
                'panel_nz_face': 0
            }
        ],
        [
            # Test live payload - data_2482493_2020-07-03T12-17-23
            b'K5USL201FF1F19180D220900E IE 5P ',
            {
                'callsign': 'K5USL',
                'pkt_type': '2',
                'temp_battery_1': 1,
                'temp_px_face': -1,
                'temp_nx_face': 31,
                'temp_py_face': 25,
                'temp_ny_face': 24,
                'temp_pz_face': 13,
                'temp_nz_face': 34,
                'temp_rf_amp': 9,
                'temp_battery_2': 0
            }
        ],
    ]
    invalid_packets = [
        # Payload type 1 with non-hex value
        'K5USL19I00EEEF00000000',
        # Payload type 2 with non-hex value
        'K5USL200FF1C151EXA1808F5',
        # Payload type 3 with non-hex value
        'K5USL3009M05000100',
        # Unexpected callsign
        'K4USL3009M05000100'
    ]
    dut = 'Cape1'
    result = []

    for frame, expected in valid_packets:
        result = load_objects(decoder, dut, frame)
        assert result == expected

    for frame in invalid_packets:
        with pytest.raises(Exception):
            result = load_objects(decoder, dut, frame)
