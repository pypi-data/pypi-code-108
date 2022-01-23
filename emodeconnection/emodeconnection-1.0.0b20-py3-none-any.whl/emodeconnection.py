###########################################################
###########################################################
## EMode - Python interface, by EMode Photonix LLC
###########################################################
## Copyright (c) 2022 EMode Photonix LLC
###########################################################

import os, socket, json, pickle, time, atexit
from subprocess import Popen
import numpy as np
import scipy.io as sio

class EMode:
    def __init__(self, sim="emode", verbose=False, roaming=False, open_existing=False, new_name=False, priority='pN'):
        '''
        Initialize defaults and connects to EMode.
        '''
        self.status = 'open'
        atexit.register(self.close)
        try:
            sim = str(sim)
        except:
            raise TypeError("input parameter 'sim' must be a string")
            return
        try:
            priority = str(priority)
        except:
            raise TypeError("input parameter 'priority' must be a string")
            return
        self.dsim = sim
        self.ext = ".eph"
        self.exit_flag = False
        self.DL = 2048
        HOST = '127.0.0.1'
        PORT_SERVER = 0
        port_path = os.path.join(os.environ['APPDATA'], 'EMode', 'port.txt')
        if os.path.exists(port_path): os.remove(port_path)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(60)
        cmd_lst = ['EMode.exe', self.LHOST, self.LPORT, str(self.PORT_SERVER)]
        if (verbose == True):
            cmd_lst.append('-v')
        if (priority != 'pN'):
            priority = priority.strip('-')
            cmd_lst.append('-'+priority)
        if roaming:
            cmd_lst.append('-r')
        self.proc = Popen(cmd_lst, stderr=None)
        
        # Read EMode port
        t0 = time.perf_counter()
        waiting = True
        wait_time = 20 # [seconds]
        while waiting:
            try:
                with open(port_path, 'r') as f:
                    PORT_SERVER = int(f.read())
            except:
                pass
            if (PORT_SERVER != 0):
                # print("Connection: %d" % PORT_SERVER, flush=True)
                break
            elif (time.perf_counter() - t0) > wait_time:
                waiting = False
            time.sleep(0.05)
        
        if not waiting:
            self.s.close()
            raise RuntimeError("EMode connection error!")
        
        time.sleep(0.1) # wait for EMode to open
        self.s.connect((HOST, PORT_SERVER))
        self.s.settimeout(None)
        self.s.sendall(b"connected with Python!")
        time.sleep(0.1) # wait for EMode
        
        if (open_existing):
            RV = self.call("EM_open", sim=sim, new_name=new_name)
        else:
            RV = self.call("EM_init", sim=sim)
        if (RV == 'ERROR'):
            raise RuntimeError("internal EMode error")
        self.dsim = RV[len("sim:"):]
        return
    
    def call(self, function, **kwargs):
        '''
        Send a command to EMode.
        '''
        sendset = {}
        if (isinstance(function, str)):
            sendset['function'] = function
        else:
            raise TypeError("input parameter 'function' must be a string")
        
        for kw in kwargs:
            data = kwargs[kw]
            if (type(data).__module__ == np.__name__):
                data = np.squeeze(data).tolist()
            
            if (isinstance(data, list)):
                if (len(data) == 1):
                    data = data[0]
            
            sendset[kw] = data
        
        if ('sim' not in kwargs):
            sendset['sim'] = self.dsim
        
        try:
            sendstr = json.dumps(sendset)
        except TypeError:
            raise TypeError("EMode function inputs must have type string, int/float, or list")
        
        try:
            self.s.sendall(bytes(sendstr, encoding="utf-8"))
            recvstr = self.s.recv(self.DL)
        except:
            # Exited due to license checkout
            self.s.shutdown(socket.SHUT_RDWR)
            self.s.close()
            self.exit_flag = True
        
        if (self.exit_flag):
            raise RuntimeError("License checkout error!")
        
        recvjson = recvstr.decode("utf-8")
        recvset = json.loads(recvjson)
        
        return recvset['RV']
    
    def get(self, variable):
        '''
        Return data from simulation file.
        '''
        if (not isinstance(variable, str)):
            raise TypeError("input parameter 'variable' must be a string")
        
        RV = self.call("EM_save", sim=self.dsim)
        
        fl = open(self.dsim+self.ext, 'rb')
        f = pickle.load(fl)
        fl.close()
        if (variable in list(f.keys())):
            data = f[variable]
        else:
            print("Data does not exist.")
            return
        
        return data
    
    def inspect(self):
        '''
        Return list of keys from available data in simulation file.
        '''
        RV = self.call("EM_save", sim=self.dsim)
        fl = open(self.dsim+self.ext, 'rb')
        f = pickle.load(fl)
        fl.close()
        fkeys = list(f.keys())
        fkeys.remove("EMode_simulation_file")
        return fkeys
    
    def close(self, **kwargs):
        '''
        Send saving options to EMode and close the connection.
        '''
        try:
            self.call("EM_close", **kwargs)
            sendjson = json.dumps({'function': 'exit'})
            self.s.sendall(bytes(sendjson, encoding="utf-8"))
            while True:
                time.sleep(0.01)
                if self.proc.poll() is None:
                    break
            time.sleep(0.25)
            self.s.shutdown(socket.SHUT_RDWR)
        except:
            pass
        self.s.close()
        self.status = 'closed'
        return
    
    def close_atexit(self, **kwargs):
        if self.status == 'open':
            self.close()
        return

def open_file(sim):
    '''
    Opens an EMode simulation file with either .eph or .mat extension.
    '''
    ext = '.eph'
    mat = '.mat'
    found = False
    for file in os.listdir():
        if ((file == sim+ext) or ((file == sim) and (sim.endswith(ext)))):
            found = True
            if (sim.endswith(ext)):
                sim = sim.replace(ext,'')
            fl = open(sim+ext, 'rb')
            f = pickle.load(fl)
            fl.close()
        elif ((file == sim+mat) or ((file == sim) and (sim.endswith(mat)))):
            found = True
            f = sio.loadmat(sim+mat)
    
    if (not found):
        print("ERROR: file not found!")
        return "ERROR"
    
    return f

def get(variable, sim='emode'):
    '''
    Return data from simulation file.
    '''
    if (not isinstance(variable, str)):
        raise TypeError("input parameter 'variable' must be a string")
    
    if (not isinstance(sim, str)):
        raise TypeError("input parameter 'sim' must be a string")
    
    f = open_file(sim=sim)
    
    if (variable in list(f.keys())):
        data = f[variable]
    else:
        print("Data does not exist.")
        return
    
    return data

def inspect(sim='emode'):
    '''
    Return list of keys from available data in simulation file.
    '''
    if (not isinstance(sim, str)):
        raise TypeError("input parameter 'sim' must be a string")
    
    f = open_file(sim=sim)
    
    fkeys = list(f.keys())
    fkeys.remove("EMode_simulation_file")
    return fkeys
