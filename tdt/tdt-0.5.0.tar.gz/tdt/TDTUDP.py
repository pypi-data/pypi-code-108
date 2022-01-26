import socket
import struct

import numpy as np

class TDTUDP():
    def __init__(self, host='10.1.0.100', send_type=float, recv_type=float, verbose=False,
                 sort_codes=0, bits_per_bin=4):

        self.unpack_byte = struct.Struct('>h').unpack
        self.NPACKETS = -1
        self.send_header = None

        self.TDT_UDP_HOSTNAME = host
        self.send_type = send_type
        self.recv_type = recv_type # if self.sort_codes > 0, this is ignored
        self.verbose = verbose

        self.sort_codes = sort_codes
        self.bits_per_bin = bits_per_bin
        
        # UDP command constants
        self.CMD_SEND_DATA        = 0x00
        self.CMD_GET_VERSION      = 0x01
        self.CMD_SET_REMOTE_IP    = 0x02
        self.CMD_FORGET_REMOTE_IP = 0x03

        # Important: the RZ UDP interface port is fixed at 22022
        self.UDP_PORT = 22022

        # create a UDP socket object
        self.sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM ) # UDP

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # connect the PC to the target UDP interface
        self.sock.connect((self.TDT_UDP_HOSTNAME, self.UDP_PORT))

        # configure the header. Notice that it includes the header
        # information followed by the command 2 (set remote IP)
        # and 0 (no data packets for header).
        packet = struct.pack('4B', 0x55, 0xAA, self.CMD_SET_REMOTE_IP, 0)

        # Sends the packet to the UDP interface, setting the remote IP
        # address of the UDP interface to the host PC
        self.sock.send(packet)

    def recv(self):

        # receive a data packet from the UDP interface
        packet = self.sock.recv(1024)
        if len(packet) < 2:
            return None
        
        # check that magic number is in first position of packet
        if self.unpack_byte(packet[:2]) != (0x55AA,):
            print('bad header')
            return None
        
        if self.sort_codes == 0:
            try:
                result = np.frombuffer(packet[4:], dtype=self.recv_type).byteswap()
            except:
                print('unknown type', self.recv_type)
                result = None
        else:
            # do sort unpacking
            byte_packet = np.frombuffer(packet, dtype=np.uint8)
            bits_packet = np.unpackbits(byte_packet[4:])
            rrr = np.reshape(bits_packet, (-1, 32))
            parts = np.vstack([np.flipud(np.reshape(rr, (-1, self.bits_per_bin))) for rr in rrr])
            padding = np.zeros((len(parts), 8-self.bits_per_bin), dtype=np.uint8)
            bytes_for_packing = np.hstack([padding, parts])
            chunks = np.packbits(bytes_for_packing).astype(np.uint32)
            
            # organize by channel/sort
            result = np.reshape(chunks, (-1, self.sort_codes)).T
        
        if self.verbose:
            print('received packet', result)
        
        return result

    def send(self, data=[]):

        if len(data) < 1:
            return None

        if len(data) != self.NPACKETS:
            self.NPACKETS = len(data)

            # configure the header
            self.send_header = struct.pack('4B', 0x55, 0xAA, self.CMD_SEND_DATA, self.NPACKETS)

        # send the data packet to the UDP interface.
        if self.verbose:
            print('sending packet', data, '...')
        self.sock.send(self.send_header + data.byteswap().tobytes())

if __name__ == '__main__':
    import time
    
    host = 'localhost'

    #udp = TDTUDP(host=host, send_type=np.uint32, recv_type=np.uint32)
    #udp = TDTUDP(host=host, send_type=np.float32, recv_type=np.float32)
    #udp = TDTUDP(host=host, send_type=np.uint32, sort_codes=4, bits_per_bin=4)
    udp = TDTUDP(host=host, sort_codes=4, bits_per_bin=4)
    
    # SEND ONLY EXAMPLE
    if 0:
        SEND_PACKETS = 1
        ct = 0
        while 1:
            ct += 1
            fakedata = range(ct % 10, SEND_PACKETS + ct % 10)
            if udp.send_type == float:
                fakedata = [x * 2. for x in fakedata]
            udp.send(fakedata)
            time.sleep(.1) # slow it down a bit

    # RECEIVE ONLY EXAMPLE
    if 1:
        while 1:
            data = udp.recv()
            
            # if looking at binner packets, extract sort codes
            channel = 4
            sort_code = 2
            print('CHANNEL:', channel, 'SORT:', sort_code, '\t', data[sort_code-1][channel-1], end='\t\t\t\r')

    # SEND AND RECEIVE EXAMPLE
    if 0:
        SEND_PACKETS = 8
        ct = 0
        while 1:
            ct += 1
            fakedata = range(ct % 10, SEND_PACKETS + ct % 10)
            if udp.send_type == float:
                fakedata = [x * 2. for x in fakedata]
            
            data = udp.recv()
            print(data)

            udp.send(fakedata)