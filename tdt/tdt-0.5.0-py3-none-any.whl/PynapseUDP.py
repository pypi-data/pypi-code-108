import re
import socketserver
import socket

g_udp_data: bytes = None 

class MyUDPHandler(socketserver.BaseRequestHandler): 
    def handle(self): 
        global g_udp_data
        g_udp_data = None

        try: 
            g_udp_data = self.request[0].strip() 
            sock = self.request[1] 

        except Exception as e: 
            print(' exception: {}'.format(str(e))) 

class PynapseUDP():

    def __init__(self):
    
        self.data = None
        self.data_str = ''
        self.raw_data = None
        self.pat_value = re.compile("\[(?P<session>.+)\.(?P<block>.+)\.(?P<trial>.+)\] (?P<name>.+)\=(?P<value>.+)")
        self.pat_session = re.compile("\[(?P<session>.+)\.(?P<block>.+)\.(?P<trial>.+)\] (?P<entry>.+)")
        self.pat_raw_time = re.compile("(?P<time_str>[^\s]+)[\s]{4}(?P<entry>.+)")
        HOST, PORT = '0.0.0.0', 24416 
        
        self.server = socketserver.UDPServer((HOST, PORT), MyUDPHandler)
        print('listening on port {}'.format(PORT)) 

    def process(self):
        self.data_str = ''
        self.data = None
        if self.raw_data is None:
            return
        
        self.data_str = udp.raw_data.decode('utf-8')
        
        # check if it's a value entry
        result = self.pat_value.match(self.data_str)
        if result:
            self.data = result.groupdict()
            self.data['type'] = 'Value'
        else:
            # check if it's a session entry
            result = self.pat_session.match(self.data_str)
            if result:
                self.data = result.groupdict()
                self.data['type'] = 'SessionEntry'
            else:
                # check if it's a raw entry with timestamp
                result = self.pat_raw_time.match(self.data_str)
                if result:
                    self.data = result.groupdict()
                    self.data['type'] = 'RawEntryTimestamp'
                    parts = self.data['time_str'].split(':')
                    total_seconds = float(parts[-1]) + 60 * float(parts[-2])
                    if len(parts) > 2:
                        total_seconds += float(parts[-3]) * 3600
                    self.data['time'] = total_seconds
                else:
                    self.data = {'type':'RawEntry', 'entry':self.data_str}                    
        
        if self.data is None:
            return
        
        for key, value in self.data.items():
            if key in ['session', 'block', 'trial']:
                self.data[key] = int(value)
            else:
                try:
                    self.data[key] = float(value)
                except ValueError:
                    pass
    
    def recv(self):
        global g_udp_data
        g_udp_data = None 
        try: 
            self.server.handle_request() 
        except: 
            pass
        self.raw_data = g_udp_data
        self.process()
        
if __name__ == '__main__': 
    
    udp = PynapseUDP()
    
    while True: 
        udp.recv()
        if udp.data is not None: 
            print(udp.data)

    udp.server.server_close() 
