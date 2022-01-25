import logging
import socket
import asyncio
import struct
from typing import Dict, List


# uint8(消息类型) 1:数据包 2:数据包结束 3:数据包确认
# uint32(包号)
# uint32(子包号)

class UDPPacketType:
    Packet = 1          # 数据包
    EndPacket = 2       # 数据包结束
    ACKPacket = 3       # 数据包确认


class UDPPacket:
    def __init__(self, id: int = 0, packets: Dict[int, bytes] = {}, size: int = 0) -> None:
        self.id = id
        self.packets = packets
        self.size = size

    def add_packet(self, sub_id: int, packet: bytes):
        if self.packets.get(sub_id) is None:
            self.packets[sub_id] = packet
            self.size += 1

    def remove_packet(self, sub_id: int):
        if self.packets.get(sub_id) is not None:
            del self.packets[sub_id]
            self.size -= 1


class UDPStream:
    def __init__(self,
                 host, port,
                 target_host, target_port,
                 packet_size=539,
                 loop: asyncio.BaseEventLoop = asyncio.get_event_loop()) -> None:
        self.sock = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.target = (target_host, target_port)
        self.sock.bind((host, port))
        self.packet_size = packet_size
        self.loop = loop
        self.read_buffer: List[UDPPacket] = []
        self.read_index: Dict[int, int] = {}
        self.write_buffer: List[UDPPacket] = []
        self.max_packet_id = 0

    def start(self):
        self.read_task = self.loop.create_task(self._read_task())

    def close(self):
        self.read_task.cancel()
        self.read_task = None

    def send(self, data: bytes):
        self.sock.sendto(data, self.target)

    async def write(self, data: bytes):
        # 获取包长度
        data_len = len(data)

        # 生成包ID
        self.max_packet_id = (self.max_packet_id + 1) % 0xFFFFFFFF
        packet_id = self.max_packet_id

        # 计算子包数量
        sub_count = data_len // self.packet_size
        if data_len % self.packet_size != 0:
            sub_count += 1

        sub_packets = {}
        for i in range(sub_count - 1):
            # 生成子包
            sub_packet = struct.pack(
                "!BII", UDPPacketType.Packet, packet_id, i) + data[i * self.packet_size: (i + 1) * self.packet_size]
            # 发送数据
            self.send(sub_packet)
            sub_packets[i] = sub_packet

        # 构建结束包
        end_packet = struct.pack(
            "!BII", UDPPacketType.EndPacket, packet_id, sub_count - 1) + data[self.packet_size*(sub_count - 1):]

        # 发送结束包
        self.send(end_packet)
        sub_packets[sub_count - 1] = end_packet

        # 将包加入到缓存
        self.write_buffer.append(UDPPacket(packet_id, sub_packets, sub_count))

    async def _read_task(self):
        while True:
            try:
                # 读取一个UDP包
                data = await self.loop.sock_recv(self.sock, 0xFFFF)

                # 解析包头
                msg_type, packet_id, sub_id = struct.unpack("!BII", data[:9])

                # 根据包类型处理
                if msg_type == UDPPacketType.Packet:
                    # 发送ACK
                    ack_packet = struct.pack(
                        "!BII", UDPPacketType.ACKPacket, packet_id, sub_id)
                    self.send(ack_packet)
                
                    # 将数据放到接收缓存
                    cache_index = self.read_index.get(packet_id)
                    if cache_index is None:
                        new_packet = UDPPacket(packet_id)
                        new_packet.add_packet(sub_id, data[9:])
                        self.read_buffer.append(new_packet)
                        self.read_index[packet_id] = len(self.read_buffer)
                    else:
                        cache_packet = self.read_buffer[cache_index]
                        cache_packet.add_packet(sub_id, data[9:])
                elif msg_type == UDPPacketType.EndPacket:
                    pass
                elif msg_type == UDPPacketType.ACKPacket:
                    pass

            except KeyboardInterrupt:
                break
            except Exception as e:
                logging.error(e.with_traceback(None))
