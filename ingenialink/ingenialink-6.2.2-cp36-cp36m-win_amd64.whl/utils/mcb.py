import binascii
import struct


class MCB:
    """Motion Control Bus (MCB) is a high-speed serial protocol designed for getting low
    latency and high determinism in motion control systems where control loops
    work at high update rates (tens of kHz).
    """
    EXTENDED_MESSAGE_SIZE = 8

    def __init__(self):
        pass

    def __del__(self):
        pass

    def create_msg(self, node, subnode, cmd, data, size):
        """Creates a command message following the MCB protocol.

        Args:
            node (int): Reserved bits used to identify the destination device.
            subnode (int): Subsystem bits used to identify the destination device.
            cmd (int): Command to lead the message.
            data (bytes): Data to be added to the message.
            size (int): Size of data.

        Returns:
            bin: MCB command message.
        """
        node_head = (node << 4) | (subnode & 0xf)
        node_head = struct.pack('<H', node_head)

        if size > self.EXTENDED_MESSAGE_SIZE:
            cmd = cmd + 1
            head = struct.pack('<H', cmd)
            head_size = struct.pack('<H', size)
            head_size = head_size + bytes(
                [0] * (self.EXTENDED_MESSAGE_SIZE - len(head_size)))
            ret = node_head + head + head_size + struct.pack(
                '<H', binascii.crc_hqx(node_head + head + head_size, 0)) + data
        else:
            head = struct.pack('<H', cmd)
            ret = node_head + head + data + struct.pack(
                '<H', binascii.crc_hqx(node_head + head + data, 0))

        return ret

    def add_cmd(self, node, subnode, cmd, data, output):
        """Creates and adds a MCB message to a given file.

        Args:
            node (int): Reserved bits used to identify the destination device.
            subnode (int): Subsystem bits used to identify the destination device.
            cmd (int): Command to lead the message.
            data (bytes): Data to be added to the message.
            output (file): File object to store the message.
        """
        if len(data) <= self.EXTENDED_MESSAGE_SIZE:
            data = data + bytes([0] * (self.EXTENDED_MESSAGE_SIZE - len(data)))
        frame = self.create_msg(node, subnode, cmd, data, len(data))
        output.write(frame)
