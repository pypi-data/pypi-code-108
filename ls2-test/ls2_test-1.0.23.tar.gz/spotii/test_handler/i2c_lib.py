import smbus
import threading
from time import *
#i2c_sem = threading.Semaphore()
class i2c_device:
    def __init__(self, addr, port=1):
        self.addr = addr
        self.bus = smbus.SMBus(port)

# Write a single command
    def write_cmd(self, cmd):
        
        self.bus.write_byte(self.addr, cmd)
        sleep(0.0001)

# Write a command and argument
    def write_cmd_arg(self, cmd, data):
        #i2c_sem.acquire()
        self.bus.write_byte_data(self.addr, cmd, data)
        #i2c_sem.release()
        sleep(0.0001)

# Write a block of data
    def write_block_data(self, cmd, data):
        self.bus.write_block_data(self.addr, cmd, data)
        sleep(0.0001)

# Read a single byte
    def read(self):
        return self.bus.read_byte(self.addr)

# Read
    def read_data(self, cmd):
        return self.bus.read_byte_data(self.addr, cmd)

# Read a block of data
    def read_block_data(self, subAddr, number):
      #return self.bus.read_block_data(self.addr, cmd)
        #i2c_sem.acquire()
        data = self.bus.read_i2c_block_data(self.addr, subAddr, number)
        #i2c_sem.release()
        return data

# SMBUS Read a block of data
    def read_block_data_smbus(self, cmd):
        return self.bus.read_block_data(self.addr, cmd)
