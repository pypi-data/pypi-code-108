import unittest
from unittest.mock import MagicMock, patch

from centaur._.pyvmps.cfg import config as env
from centaur._.pyvmps.communicator.socket_base import _apply_protocol, _num_parts, _receive, _send


class TestSocketBase(unittest.TestCase):
    """TestSocketBase."""

    def test_apply_protocol(self):
        def _test(_payload, i_of_n, expected):
            res = _apply_protocol(_payload, i_of_n)
            self.assertEqual(res, expected)

        tt = [
            {"_payload": b"123456", "i_of_n": b"1", "expected": b"0000000071123456"},
            {"_payload": b"123456", "i_of_n": b"0", "expected": b"0000000070123456"},
            {"_payload": "123456", "i_of_n": "1", "expected": b"0000000071123456"},
        ]
        for sample in tt:
            _test(**sample)

    def test_num_parts(self):
        payloads = b"123456"
        frag_list, num_parts = _num_parts(payloads)
        self.assertEqual(frag_list, [payloads])
        self.assertEqual(num_parts, [b"1"])

    # pylint: disable=no-self-use
    def test__send(self):
        sample = b"sample"
        part = b"0"
        payload_parts = MagicMock()
        payload_parts.__iter__.return_value = [sample]
        parts = MagicMock()
        parts.__iter__.return_value = [part]
        with patch("pyvmps.communicator.socket_base._apply_protocol") as mock_apply_protocol, patch(
            "pyvmps.communicator.socket_base._num_parts"
        ) as mock_num_parts:
            io_stream = MagicMock()
            payload = b"sample_payload"
            mock_num_parts.return_value = (payload_parts, parts)
            _send(io_stream, payload)
            mock_num_parts.assert_called_with(payload)
            mock_apply_protocol.assert_called_with(sample, part)
            io_stream.write.assert_called_once()
            io_stream.flush.assert_called_once()

    def test__receive(self):
        tt = [
            {"sample": b"sample"},
            {"sample": b'{"m123918029381": {"msg_type": "something"}09123809128309}}'},
            {"sample": b""},
        ]

        def _inner(sample: bytes, last: bytes = b"1"):
            msg = str(len(sample) + 1).zfill(env.GowebProtocolConst.MSG_HEADER_LENGTH).encode() + last + sample
            io_stream = MagicMock()
            to_read = iter(
                [msg[: env.GowebProtocolConst.MSG_HEADER_LENGTH], msg[env.GowebProtocolConst.MSG_HEADER_LENGTH :]]
            )
            io_stream.read.side_effect = lambda buff: next(to_read)
            with patch("pyvmps.communicator.socket_base.check_last_part", return_value=True) as mock_check_last_part:
                recv_msg = _receive(io_stream)
                mock_check_last_part.assert_called_once()
                self.assertEquals(recv_msg, sample)

        for t in tt:
            _inner(**t)
