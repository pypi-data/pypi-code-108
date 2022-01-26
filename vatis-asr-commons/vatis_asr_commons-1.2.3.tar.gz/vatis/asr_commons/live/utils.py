from vatis.asr_commons.domain import DataPacket
from vatis.asr_commons.live.headers import PACKET_NUMBER_HEADER, SPLIT_PACKET_HEADER, FINAL_SPLIT_PACKET_HEADER


def is_last_packet(packet: DataPacket, last_sent_packet_number: int) -> bool:
    """
    Utility method to determine if the given packet is the last that should be received according to
    the last sent packet number

    :param packet: current received packet
    :param last_sent_packet_number: the number of the last sent packet
    :return: True if its the last packet to be received
    """

    if packet.get_header(PACKET_NUMBER_HEADER) == last_sent_packet_number:
        if packet.get_header(SPLIT_PACKET_HEADER, default=False):
            return packet.get_header(FINAL_SPLIT_PACKET_HEADER, default=False)
        else:
            return True
    else:
        return False
