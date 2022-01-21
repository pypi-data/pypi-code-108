#!/usr/bin/env python
yqAuD=None
yqAui=True
yqAuo=Exception
yqAuS=str
yqAuB=len
yqAub=isinstance
yqAuV=dict
yqAut=hasattr
yqAuH=int
yqAuQ=False
yqAuY=bytes
import json
import logging
import os
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import traceback
import uuid
import boto3
import requests
from six.moves.BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from six.moves.socketserver import ThreadingMixIn
LOG=logging.getLogger("local_daemon")
DEFAULT_PORT_LOCAL_DAEMON=4600
DEFAULT_PORT_LOCAL_DAEMON_ROOT=4601
DEFAULT_PORT_S3=4566
DEFAULT_PORT_EC2=4566
ENDPOINT_S3="http://localhost:%s"%DEFAULT_PORT_S3
ENDPOINT_EC2="http://localhost:%s"%DEFAULT_PORT_EC2
LOCAL_BIND_ADDRESS_PATTERN="192.168.123.*"
USED_BIND_ADDRESSES=[]
MAC_NETWORK_INTERFACE="en0"
BUCKET_MARKER_LOCAL=(os.environ.get("BUCKET_MARKER_LOCAL")or "").strip()or "__local__"
class FuncThread(threading.Thread):
 def __init__(self,func,params=yqAuD):
  threading.Thread.__init__(self)
  self.daemon=yqAui
  self.params=params
  self.func=func
 def run(self):
  try:
   self.func(self.params)
  except yqAuo as e:
   log("Error in thread function: %s %s"%(e,traceback.format_exc()))
class ThreadedHTTPServer(ThreadingMixIn,HTTPServer):
 daemon_threads=yqAui
class RequestHandler(BaseHTTPRequestHandler):
 def do_POST(self):
  self.read_content()
  try:
   result=self.handle_request()
   self.send_response(200)
  except yqAuo as e:
   error_string=yqAuS(e)
   result=json.dumps({"error":error_string})
   log("Error handling request: %s - %s"%(self.request_json,e))
   self.send_response(500)
  self.send_header("Content-Length","%s"%yqAuB(result)if result else 0)
  self.end_headers()
  if yqAuB(result or ""):
   self.wfile.write(to_bytes(result))
 def handle_request(self):
  request=self.request_json
  result="{}"
  operation=request.get("op","")
  if operation=="getos":
   result={"result":get_os()}
  elif operation=="shell":
   command=request.get("command")
   result=run_shell_cmd(command)
  elif operation=="s3:download":
   result=s3_download(request)
  elif operation.startswith("root:"):
   result=forward_root_request(request)
  elif operation=="kill":
   log("Terminating local daemon process (port %s)"%DEFAULT_PORT_LOCAL_DAEMON)
   os._exit(0)
  else:
   result={"error":'Unsupported operation "%s"'%operation}
  result=json.dumps(result)if yqAub(result,yqAuV)else result
  return result
 def read_content(self):
  if yqAut(self,"data_bytes"):
   return
  content_length=self.headers.get("Content-Length")
  self.data_bytes=self.rfile.read(yqAuH(content_length))
  self.request_json={}
  try:
   self.request_json=json.loads(self.data_bytes)
  except yqAuo:
   pass
class RequestHandlerRoot(RequestHandler):
 def handle_request(self):
  request=self.request_json
  result="{}"
  operation=request.get("op")
  if operation=="root:ssh_proxy":
   result=start_ssh_forward_proxy(request)
  elif operation=="kill":
   log("Terminating local daemon process (port %s)"%DEFAULT_PORT_LOCAL_DAEMON_ROOT)
   os._exit(0)
  else:
   result={"error":'Unsupported operation "%s"'%operation}
  result=json.dumps(result)if yqAub(result,yqAuV)else result
  return result
def s3_download(request):
 bucket=request["bucket"]
 key=request["key"]
 tmp_dir=os.environ.get("TMPDIR")or tempfile.mkdtemp()
 target_file=os.path.join(tmp_dir,request.get("file_name")or "s3file.%s"%yqAuS(uuid.uuid4()))
 if not os.path.exists(target_file)or request.get("overwrite"):
  if bucket==BUCKET_MARKER_LOCAL:
   shutil.copy(key,target_file)
  else:
   s3=boto3.client("s3",endpoint_url=ENDPOINT_S3)
   log("Downloading S3 file s3://%s/%s to %s"%(bucket,key,target_file))
   s3.download_file(bucket,key,target_file)
 return{"local_file":target_file}
def forward_root_request(request):
 url="http://localhost:%s"%DEFAULT_PORT_LOCAL_DAEMON_ROOT
 response=requests.post(url,data=json.dumps(request))
 return json.loads(to_str(response.content))
def start_ssh_forward_proxy(options):
 path=os.path.dirname(__file__)
 if path not in sys.path:
  sys.path.append(path)
 from tcp_proxy import server_loop
 port=options.get("port")or get_free_tcp_port()
 host=LOCAL_BIND_ADDRESS_PATTERN.replace("*",yqAuS(yqAuB(USED_BIND_ADDRESSES)+2))
 create_network_interface_alias(host)
 USED_BIND_ADDRESSES.append(host)
 log("Starting local SSH forward proxy, %s:22 -> localhost:%s"%(host,port))
 options={"bind_port":22,"bind_addr":host,"port":port}
 FuncThread(server_loop,options).start()
 return{"host":host,"forward_port":port}
def create_network_interface_alias(address,interface=yqAuD):
 sudo_cmd="sudo"
 if is_mac_os():
  interface=interface or MAC_NETWORK_INTERFACE
  run_cmd("{sudo_cmd} ifconfig {iface} alias {addr}".format(sudo_cmd=sudo_cmd,addr=address,iface=interface))
  return
 if is_linux():
  interfaces=os.listdir("/sys/class/net/")
  interfaces=[i for i in interfaces if ":" not in i]
  for interface in interfaces:
   try:
    iface_addr=get_ip_address(interface)
    log("Found network interface %s with address %s"%(interface,iface_addr))
    assert iface_addr
    assert interface not in["lo"]and not iface_addr.startswith("127.")
    run_cmd("{sudo_cmd} ifconfig {iface}:0 {addr} netmask 255.255.255.0 up".format(sudo_cmd=sudo_cmd,addr=address,iface=interface))
    return
   except yqAuo as e:
    log("Unable to create forward proxy on interface %s, address %s: %s"%(interface,address,e))
    pass
 raise yqAuo("Unable to create network interface")
def run_shell_cmd(command):
 try:
  return{"result":run_cmd(command)}
 except yqAuo as e:
  error_string=yqAuS(e)
  if yqAub(e,subprocess.CalledProcessError):
   error_string="%s: %s"%(error_string,e.output)
  return{"error":error_string}
def get_os():
 if is_mac_os():
  return "macos"
 if is_linux():
  return "linux"
 return "windows"
def run_cmd(cmd):
 log("Running command: %s"%cmd)
 return to_str(subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=yqAui))
def log(*args):
 print(*args)
 sys.stdout.flush()
def is_mac_os():
 try:
  out=to_str(subprocess.check_output("uname -a",shell=yqAui))
  return "Darwin" in out
 except subprocess.CalledProcessError:
  return yqAuQ
def is_linux():
 try:
  out=to_str(subprocess.check_output("uname -a",shell=yqAui))
  return "Linux" in out
 except subprocess.CalledProcessError:
  return yqAuQ
def get_ip_address(ifname):
 import fcntl
 s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
 return socket.inet_ntoa(fcntl.ioctl(s.fileno(),0x8915,struct.pack("256s",to_bytes(ifname[:15])))[20:24])
def get_free_tcp_port():
 tcp=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
 tcp.bind(("",0))
 addr,port=tcp.getsockname()
 tcp.close()
 return port
def to_bytes(obj):
 return obj.encode("utf-8")if yqAub(obj,yqAuS)else obj
def to_str(obj):
 return obj.decode("utf-8")if yqAub(obj,yqAuY)else obj
def start_server(port,handler):
 kill_server(port)
 try:
  log("Starting local daemon server on port %s"%port)
  httpd=ThreadedHTTPServer(("0.0.0.0",port),handler)
  httpd.serve_forever()
 except yqAuo:
  log("Local daemon server already running, or port %s not available"%port)
  pass
def kill_server(port):
 try:
  requests.post("http://localhost:%s"%port,data='{"op":"kill"}')
 except yqAuo:
  pass
def kill_servers():
 kill_server(DEFAULT_PORT_LOCAL_DAEMON)
 kill_server(DEFAULT_PORT_LOCAL_DAEMON_ROOT)
def main():
 logging.basicConfig()
 daemon_type=sys.argv[1]if yqAuB(sys.argv)>1 else "main"
 os.environ["AWS_ACCESS_KEY_ID"]=os.environ.get("AWS_ACCESS_KEY_ID")or "test"
 os.environ["AWS_SECRET_ACCESS_KEY"]=os.environ.get("AWS_SECRET_ACCESS_KEY")or "test"
 if daemon_type=="main":
  start_server(DEFAULT_PORT_LOCAL_DAEMON,RequestHandler)
 elif daemon_type=="root":
  start_server(DEFAULT_PORT_LOCAL_DAEMON_ROOT,RequestHandlerRoot)
 else:
  log("Unexpected local daemon type: %s"%daemon_type)
def get_log_file_path():
 from localstack.config import dirs
 return os.path.join(dirs.tmp,"localstack_daemon.log")
def start_in_background():
 from localstack.utils.common import run
 log_file=get_log_file_path()
 LOG.info("Logging local daemon output to %s"%log_file)
 python_cmd=sys.executable
 cmd="%s %s"%(python_cmd,__file__)
 run(cmd,outfile=log_file,asynchronous=yqAui)
 LOG.info("Attempting to obtain sudo privileges for local daemon of EC2 API "+"(required to start SSH forward proxy on privileged port 22). "+"You may be asked for your sudo password.")
 run("sudo -v",stdin=yqAui)
 def start_root_daemon(*args):
  cmd="sudo %s %s root >> %s"%(python_cmd,__file__,log_file)
  run(cmd,outfile=log_file,stdin=yqAui)
 FuncThread(start_root_daemon).start()
if __name__=="__main__":
 main()
# Created by pyminifier (https://github.com/liftoff/pyminifier)
