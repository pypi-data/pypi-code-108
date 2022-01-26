from collections import deque
import socket
import struct

import numpy as np

import tdt

class BH32():
    def __init__(self, host='10.1.0.101', dev_num=1, callback=None, 
                 initA=None, initB=None, use_api=False, verbose=False):

        self.USE_API = use_api
        self.TDT_BH32_HOSTNAME = host
        
        self.DEV_NUM = dev_num
        self.VERBOSE = verbose
        self.MAX_HISTORY = 100
        
        self.state_history = deque()
        
        self.input_state = [None, None]
        self.output_state = [None, None]
        self.unpack1L = struct.Struct('>L').unpack
        self.unpack4B = struct.Struct('4B').unpack
        self.pack5B = struct.Struct('5B').pack
        self.pack9B = struct.Struct('9B').pack
        self.pack1I = struct.Struct('>I').pack
        
        # BH32 command constants
        self.CMD_GET_VERSION       = 0x00
        self.CMD_SET_UNIT_NUM      = 0x01
        self.CMD_PICK_UNIT_NUM     = 0x02
        self.CMD_GET_SET_IO        = 0x03
        self.CMD_GET_SET_CONFIG    = 0x04
        self.CMD_GET_SET_TIMESTAMP = 0x05
        self.CMD_GET_SET_TRACK     = 0x06
        self.CMD_GET_SET_NETCONFIG = 0x07
        self.CMD_GET_SET_SERIAL    = 0x08
        self.CMD_GET_SET_POLL      = 0x09
        self.CMD_POLL_EVENT        = 0x0A
        self.CMD_GET_SET_TRIGGER   = 0x0B
        self.CMD_TRIGGER_EVENT     = 0x0C
        self.CMD_GET_SET_RZ_IP     = 0x0D
        
        self.CMD_POLL_TEST         = 0x7D
        self.CMD_RESET_TO_DEFAULTS = 0x7E
        self.CMD_RESET             = 0x7F
        
        if self.USE_API:
            self.syn = tdt.SynapseAPI(host)
        else:
            # Important: the RZ UDP interface port is fixed at 22022
            self.UDP_PORT = 22022

            # create a UDP socket object
            self.sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM ) # UDP

            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # connect the PC to the target BH32 interface
            self.sock.connect((self.TDT_BH32_HOSTNAME, self.UDP_PORT))

            # configure the header. Notice that it includes the header
            # information followed by the command 2 (set remote IP)
            # and 0 (no data packets for header).
            
            #self.my_ip = self.sock.getsockname()[0]
            #self.my_ip_word = tuple(np.array(self.my_ip.split('.'), dtype=np.uint8))
            #print(self.my_ip, self.my_ip_word)
            self.my_ip_word = (0, 0, 0, 0)
            
            self.header = struct.pack('7B', 0x55, 0xAB, 0x00, 0x01, 0x00, self.DEV_NUM, 0x00)
            
            self.CALLBACK = None
            self.set_trigger()
            self.recv()
            self.get_state()
            self.recv()
        
        if type(initA) is int or type(initB) is int:
            self.send_data(byteA=initA, byteB=initB)
            if not self.USE_API:
                self.recv()
        
        self.CALLBACK = callback
        if self.CALLBACK:
            while True:
                self.recv()
    
    def get_state_api(self):
        bytes = np.uint32(self.syn.getParameterValue('BH32(1)', 'AllBits'))
        byteA, byteB, byteC, byteD = self.unpack4B(self.pack1I(bytes))
        return [byteA, byteB, byteC, byteD]
    
    def get_state(self):
        if self.USE_API:
            state = self.get_state_api()
            self.output_state = state[:2]
            self.input_state = state[2:4]
        else:
            packet = self.header + self.pack5B(self.CMD_GET_SET_IO, *self.my_ip_word)
            self.sock.send(packet)
        
    def set_trigger(self):
        packet = self.header + self.pack9B(self.CMD_GET_SET_TRIGGER, 
                                           *self.my_ip_word, 0xFF, 0xFF, 0xFF, 0xFF)
        self.sock.send(packet)
        
    def send_data(self, byteA=None, byteB=None):
        if [byteA, byteB] != self.output_state:
            if self.VERBOSE:
                print('sending', byteA, byteB)
            if self.USE_API:
                self.syn.setParameterValue('BH32(1)', 'OutputMontage',
                                           (byteA << 24) + (byteB << 16))
            else:
                next_byteA = int('{:08b}'.format(byteA), 2)
                next_byteB = int('{:08b}'.format(byteB), 2)    
                packet = self.header + self.pack9B(self.CMD_GET_SET_IO, *self.my_ip_word, 
                                                   next_byteA, next_byteB, 0x00, 0x00)
                self.sock.send(packet)
    
    def do_callback(self, state):
        # state is list of all 4 input bytes
        
        # latch current input/output states and add to history
        self.output_state = state[:2]
        self.input_state = state[2:4]
        self.state_history.append(state)
        if len(self.state_history) > self.MAX_HISTORY:
            self.state_history.popleft()
        
        # do user defined callback
        new_byteA, new_byteB = self.CALLBACK(state=state, history=self.state_history)
        self.send_data(byteA=new_byteA, byteB=new_byteB)
    
    def recv(self):

        if self.USE_API:
            result = self.get_state_api()
            if self.VERBOSE:
                print('State:', result)
            if self.CALLBACK and self.input_state != result[2:4]:
                self.do_callback(result)
        else:
            # receive a data packet from the BH32 interface
            packet = self.sock.recv(1024)
        
            if len(packet) < 2:
                return None
        
            # check that magic number is in first position of packet
            # packet[3] is version (always 1)
            if self.unpack1L(packet[:4]) != (0x55AB0001,):
                print('bad header')
                return None
        
            # packet[4] is also part of device number
            if packet[5] == self.DEV_NUM:
                if self.VERBOSE:
                    print('From BH32:', end=' ')
            
            # packet[6] is group (of 255 devices), usually 0
        
            # make sure command came from the BH32
            if packet[7] & 128 != 128:
                return None
            
            msg = packet[7] & 127
        
            if msg == self.CMD_GET_SET_IO:
                result = [int('{:08b}'.format(bbb), 2) for bbb in packet[12:16]]
                self.output_state = result[:2]
                self.input_state = result[2:4]
                if self.VERBOSE:
                    print('Outputs are', self.output_state, '- inputs are', self.input_state)
            
            elif msg == self.CMD_GET_SET_TRIGGER:
                result = [int('{:08b}'.format(bbb), 2) for bbb in packet[12:16]]
                if self.VERBOSE:
                    print('Trigger mask set to', result)
                
            elif msg == self.CMD_TRIGGER_EVENT:
                result = [int('{:08b}'.format(bbb), 2) for bbb in packet[12:16]]
                if self.VERBOSE:
                    print('New state:', result)
                
                self.output_state = result[:2]
                
                # output changes are expected, only react if inputs change
                if self.CALLBACK and self.input_state != result[2:4]:
                    self.do_callback(result)
        
        return result

if __name__ == '__main__':
    import time
    
    # initialize Bytes A and B to these values
    initA = 4
    initB = 11
    
    # communication is either through SynapseAPI with BH32 directly connected to RZ
    # or through UDP to BH32 on same network as RZ and this computer
    use_api = True
    if use_api:
        host = 'localhost' # SynapseAPI IP address
        dev_num = None # BH32 device number is controlled through Synapse Rig
    else:
        host = '10.1.0.101' # BH32 IP address
        dev_num = 1 # BH32 device number for direct communication
    
    '''
    Manual Operation
    '''
    
    bh = BH32(host=host, dev_num=dev_num, initA=initA, initB=initB, 
        use_api=use_api, verbose=True)
    
    # manual reads and writes
    time.sleep(.001)
    bh.recv()
    bh.send_data(byteA=7, byteB=7)
    time.sleep(.001)
    bh.recv()
    bh.send_data(byteA=15, byteB=33)
    time.sleep(.001)
    bh.recv()

    '''
    Continuous Operation
    '''
    
    # define custom function that runs when new state is received
    def callback(state=None, history=None):
        '''
        state is a list of 4 integer bytes [A, B, C, D]
        history is queue of previous states
        
        returns byteA and byteB outputs to send to BH32
        '''
        
        print('Callback received', state)
        print('history', history)
        
        # do processing here
        new_byteA = random.randint(1,7)
        new_byteB = random.randint(1,7)
        
        print('returning', new_byteA, new_byteB)
        return new_byteA, new_byteB
    
    # waits for state changes and execustes callback
    bh = BH32(host=host, dev_num=dev_num, callback=callback,
              initA=initA, initB=initB, use_api=use_api)
