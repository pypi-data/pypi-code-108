import serial
import sys
from xmodem import XMODEM
import os
from parse import parse
import time
import io
from tqdm import tqdm
from rumboot.OpFactory import OpFactory
import threading
import serial
import serial.rfc2217
import socket
import select
import signal
import tempfile
import subprocess

class redirector(threading.Thread):
    alive = False
    fatal = False
    callback = None
    started = 0
    max_connected_time = -1

    def configure(self, serial, socket, timeout):
        self.serial = serial
        self.socket = socket
        self.max_connected_time = timeout

    def set_callback(self, cb):
        self.callback = cb

    def cleanup(self, fatal):
        self.socket.close()
        self.fatal = fatal
        self.alive = False
        if not fatal:
            print("Client disconnected")
        else:
            print("Something bad happened. Stopping daemon")
        if self.callback != None:
            print("calling", fatal)
            self.callback(fatal)

    def check_timeout(self):
        if self.max_connected_time == -1:
            return False # No timeout
        if time.monotonic() - self.started > self.max_connected_time:
            self.socket.close()
            return True
        return False

    def readSerial(self):
        if isinstance(self.serial, serial.Serial):
            return bytearray(self.serial.read(self.serial.inWaiting()))
        else:
            raise Exception("Not pyserial!")

    def writeSerial(self, data):
        if isinstance(self.serial, serial.Serial):
            return self.serial.write(data)
        else:
            raise Exception("Not pyserial!")

    def nodelay(self, sock):
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, 1)
        sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, 1)
        sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, 2)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    def loop_once(self):
        fromserial = bytearray(b"")
        fromsocket = bytearray(b"")

        ready_to_read, ready_to_write, in_error = select.select(
            [self.socket, self.serial.fileno()],
            [self.socket, self.serial.fileno()],
            [self.socket, self.serial.fileno()],
            1)
        for sock in ready_to_read:       
            if sock == self.serial.fileno():
                fromserial = fromserial + self.readSerial()
                if self.socket in ready_to_write:
                    self.socket.sendall(fromserial)
                    sent = len(fromserial)
                    del fromserial[0:sent]
            if sock == self.socket:
                tmp = self.socket.recv(1024)
                if len(tmp) == 0:
                    self.cleanup(False)
                    return False
                fromsocket = fromsocket + bytearray(tmp)
                if self.serial.fileno() in ready_to_write:
                    ret = self.writeSerial(fromsocket)
                    del fromsocket[0:ret]
        for sock in in_error:
            if sock == self.serial.fileno():
                print("Something bad with serial port")
                self.cleanup(True)
                return False
            if sock == self.socket:
                print("Disconnect?")
                self.cleanup(False)               
                return False
        return True

    def run(self):
        self.alive = True
        self.fatal = False
        self.socket.setblocking(0)
        self.nodelay(self.socket)
        self.started = time.monotonic()
        try:
            while self.loop_once():
                if self.check_timeout():
                    print("Time's up. Kicking client...")
                    self.cleanup(False)
                    return

        except BrokenPipeError:
            self.cleanup(False)
            return
        except ConnectionResetError:
            self.cleanup(False)
            return
        except OSError:
            self.socket.close()
            self.cleanup(True)
            raise
        except Exception:
            self.cleanup(False)
            raise

class appredirector(redirector):
    welcome = b'''
    RC Module's          __                __
   _______  ______ ___  / /_  ____  ____  / /_
  / ___/ / / / __ `__ \/ __ \/ __ \/ __ \/ __/
 / /  / /_/ / / / / / / /_/ / /_/ / /_/ / /_
/_/   \__,_/_/ /_/ /_/_.___/\____/\____/\__/

boot: Native Debug Environment
boot: host: Hit 'X' for X-Modem upload


'''

    def cleanup(self, fatal):
        #TODO: Kill the app
        self.pipe.kill()
        os.unlink(self.tempfile)
        return super().cleanup(fatal)

    def run(self):
        self.nodelay(self.socket)
        self._buf = b""
        def getc(size, timeout=10):
            ready = select.select([self.socket], [], [], timeout)
            ret = None
            if ready[0]:
                ret = self.socket.recv(size, socket.MSG_DONTWAIT)
            return ret

        def putc(data, timeout=10):
            ret = self.socket.sendall(data, socket.MSG_DONTWAIT)
            return len(data)

        self.modem = XMODEM(getc, putc, mode="xmodem1k")
        self.socket.sendall(self.welcome, socket.MSG_DONTWAIT)
        while self.socket.recv(1) != b"X":
            pass
        #Dirty Workaround: Some ethernet controllers (xilinx) on prototype board
        #Dirty Workaround: cause a huge wait when instructed to send just ONE byte
        ret = self.socket.sendall(b"CC", socket.MSG_DONTWAIT)
        tmp = tempfile.NamedTemporaryFile(mode="wb+", prefix="rumboot_daemon_temp_", delete=False)
        try:
            self.modem.recv(tmp)
        except Exception as e:
            self.socket.sendall(str(e), socket.MSG_DONTWAIT)
            return 0
        tmp.close()
        os.chmod(tmp.name, 755)
        self.pipe = subprocess.Popen([tmp.name], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.tempfile = tmp.name
        return super().run()

    def readSerial(self):
        return self.pipe.stdout.read()

    def writeSerial(self, data):
        return self.pipe.stdin.write(data)

    def loop_once(self):
        fromserial = bytearray(b"")
        fromsocket = bytearray(b"")

        ready_to_read, ready_to_write, in_error = select.select(
            [self.socket, self.pipe.stdout],
            [self.socket, self.pipe.stdin],
            [self.socket],
            1)
        for sock in ready_to_read:       
            if sock == self.pipe.stdout:
                fromserial = fromserial + self.readSerial()
                if self.socket in ready_to_write:
                    self.socket.sendall(fromserial)
                    sent = len(fromserial)
                    del fromserial[0:sent]
            if sock == self.socket:
                tmp = self.socket.recv(1024)
                if len(tmp) == 0:
                    self.cleanup(False)
                    return False
                fromsocket = fromsocket + bytearray(tmp)
                if self.pipe.stdin in ready_to_write:
                    ret = self.writeSerial(fromsocket)
                    del fromsocket[0:ret]
        for sock in in_error:
            if sock == self.serial.fileno():
                print("Something bad with serial port")
                self.cleanup(True)
                return False
            if sock == self.socket:
                print("Disconnect?")
                self.cleanup(False)               
                return False
        if self.pipe.poll() is not None:
            self.socket.sendall(f"boot: host: Back in rom, code {self.pipe.poll()}\n".encode())
            self.cleanup(False)
            return False

        return True
class server:
    client_queue = [ ]
    worker = None
    #Graveyard of zombies
    graveyard = []
    pid = os.getpid()
    binaries = []

    def __init__(self, terminal, tcplisten, timeout=-1, isnativedebug=False):
        self.serial = terminal.serial()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr, port = tcplisten.split(":")
        self.sock.bind((addr, int(port)))
        self.term = terminal
        self.max_connected_time = timeout
        self.isnativedebug = isnativedebug
        terminal.chip.hacks["skipsync"] = True

    def set_reset_seq(self, rst):
        self.rst = rst

    def preload_binaries(self, files):
        self.binaries = files

    def serve_once(self):
        def the_callback(fatal = False):
            if not fatal:
                self.serve_once()
            else:
                print("Interrupting main thread")
                os.kill(self.pid, signal.SIGINT)

        if self.worker != None:
            if self.worker.alive:
                return #We're busy here
            else:
                #Put our dead worker to the graveyard
                self.graveyard = self.graveyard + [ self.worker ]

        try:
            client = self.client_queue.pop(0)
            # Reset if using a nested damon
            self.term.reopen()
            self.serial = self.term.serial()

            try:
                self.rst.resetToHost()
            except:
                self.rst.reset()

            if self.binaries:
                text = b"U\nrumboot-daemon: Preloading your board board...\n\n\n"
                client["connection"].sendall(text)

                self.term.add_binaries(self.binaries)
                self.term.loop(break_after_uploads=True)

            if not self.isnativedebug:
                self.worker = redirector()
            else:
                self.worker = appredirector()

            self.worker.configure(self.serial, client["connection"], self.max_connected_time)
            self.worker.set_callback(the_callback)

            # We can't do it, if we're working remotely
            # Or somebody resets us manually
#            if type(self.rst).__name__ != "base":
#                self.serial.reset_input_buffer()
#                self.serial.reset_output_buffer()
            
            self.worker.start()
            print("Now serving client: ", client["dns"])
        except(IndexError):
            self.worker = None
            try:
                self.rst.power(0) # Power off board
            except:
                pass #No power control, no problem. It's optional

    def queue_client(self, connection, client_address):
        try:
            dns = socket.gethostbyaddr(client_address[0])
        except:
            dns = "<unknown>"
        print("Incoming connection: ", dns)
        client = { }
        client["connection"] = connection
        client["address"] = client_address
        client["dns"] = dns
        self.client_queue.append(client)
        pos = len(self.client_queue)
        if self.worker != None:
            pos = pos + 1

        text = b"U\nrumboot-daemon: You are client number %d in queue, please stand by\n\n\n" % pos
        connection.sendall(text)

        if self.worker == None:
            self.serve_once()


    def kill_zombies(self):
        #Kill all zombies.
        for z in self.graveyard:
            z.join()
        self.graveyard = [ ]                    

    def cleanup(self):
        if self.worker:
            self.worker.join()
        self.worker.socket.close()
        self.sock.close()

    def loop(self):
        try:
            self.rst.power(0) # Power off board, if can
        except:
            pass
        try:
            self.sock.listen()
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, 1)
            self.sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, 1)
            self.sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, 2)

            while True:
                print('waiting for a connection')
                connection, client_address = self.sock.accept()
                self.queue_client(connection, client_address)
                self.kill_zombies()
        except:
            self.cleanup()
        finally:
            self.cleanup()
