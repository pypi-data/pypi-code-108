import glob
emLtW=True
emLtA=dict
emLts=open
emLtG=False
emLtj=Exception
emLtI=int
import json
import logging
import os
import subprocess
import sys
import time
from ftplib import FTP
from localstack import config
from localstack import config as localstack_config
from localstack.services.generic_proxy import GenericProxy
from localstack.utils.aws import aws_stack
from localstack.utils.common import(TMP_THREADS,ShellCommandThread,load_file,new_tmp_dir,save_file,wait_for_port_open)
from localstack.utils.run import FuncThread
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler,TLS_FTPHandler
from pyftpdlib.servers import FTPServer
from localstack_ext import config as ext_config
LOG=logging.getLogger(__name__)
ROOT_USER=("root","pass123")
FTP_USER_DEFAULT_PASSWD="12345"
FTP_USER_PERMISSIONS="elradfmwMT"
FTP_PASSIVE_PORTS=[config.EXTERNAL_SERVICE_PORTS_END-2,config.EXTERNAL_SERVICE_PORTS_END-1,config.EXTERNAL_SERVICE_PORTS_END]
USE_SUBPROCESS=emLtW
DIRECTORY_MAPPING={}
DIRECTORY_MAPPING_FILE="<data_dir>/ftp.user.dir.mapping.json"
def get_dir_mapping_key(username,server_port):
 return "{}:{}".format(username,server_port)
def apply_patches():
 extended_proto_cmds=TLS_FTPHandler.proto_cmds.copy()
 extended_proto_cmds.update({"SITE ADDUSER":emLtA(perm="m",auth=emLtW,arg=emLtW,help="Syntax: SITE <SP> ADDUSER USERNAME PASSWORD HOME PRIVS <SP>.")})
 def _on_file_received(self,file_path):
  key=get_dir_mapping_key(self.username,self.server.address[1])
  mapping=get_directory_mapping()
  configuration=mapping.get(key,{})
  if not configuration:
   return
  bucket=configuration["HomeDirectory"]
  user_dir=configuration["UserDirectory"]
  key=file_path.replace("{}/".format(user_dir),"")
  with emLts(file_path)as f:
   s3_client=aws_stack.connect_to_service("s3")
   s3_client.put_object(Bucket=bucket,Key=key,Body=f.read())
   LOG.info("Received file via FTP -- target: s3://{}/{}".format(bucket,key))
 def _site_adduser(self,line):
  user,passwd,user_dir,perm=line.split(" ")[1:]
  self.authorizer.add_user(user,passwd,user_dir,perm)
  self.respond("201 Add User OK.")
 FTPHandler.proto_cmds=extended_proto_cmds
 TLS_FTPHandler.proto_cmds=extended_proto_cmds
 FTPHandler.on_file_received=_on_file_received
 FTPHandler.ftp_SITE_ADDUSER=_site_adduser
 TLS_FTPHandler.on_file_received=_on_file_received
 TLS_FTPHandler.ftp_SITE_ADDUSER=_site_adduser
def add_ftp_user(user,server_port):
 ftp=FTP()
 ftp.connect(localstack_config.LOCALSTACK_HOSTNAME,port=server_port)
 ftp.login(ROOT_USER[0],ROOT_USER[1])
 user_dir=new_tmp_dir()
 ftp.sendcmd("SITE ADDUSER  {} {} {} {}".format(user.username,FTP_USER_DEFAULT_PASSWD,user_dir,FTP_USER_PERMISSIONS))
 ftp.quit()
 dir_mapping_key=get_dir_mapping_key(user.username,server_port)
 mapping=user.get_directory_configuration()
 mapping.update({"UserDirectory":user_dir})
 set_directory_mapping(dir_mapping_key,mapping)
def update_ftp_user(user,server_port):
 dir_mapping_key=get_dir_mapping_key(user.username,server_port)
 set_directory_mapping(dir_mapping_key,user.get_directory_configuration())
def start_ftp(port):
 if USE_SUBPROCESS:
  services=os.environ.get("SERVICES","")
  if services and "s3" not in services:
   services+=",s3"
  pythonpath=os.environ.get("PYTHONPATH")or ""
  if os.getcwd()not in pythonpath.split(":"):
   pythonpath="%s:%s"%(os.getcwd(),pythonpath)
  paths=glob.glob("%s/.venv/lib/python*/site-packages"%os.getcwd())
  if paths:
   pythonpath+=":%s"%":".join(paths)
  env_vars={"SERVICES":services,"PYTHONPATH":pythonpath}
  cmd="%s %s %s"%(sys.executable,__file__,port)
  thread=ShellCommandThread(cmd,outfile=subprocess.PIPE,env_vars=env_vars,quiet=emLtG)
  thread.start()
  time.sleep(2)
 else:
  thread=do_start_ftp(port,asynchronous=emLtW)
 time.sleep(2)
 wait_for_port_open(port,retries=10,sleep_time=1.5)
 TMP_THREADS.append(thread)
 return thread
def do_start_ftp(port,asynchronous=emLtW):
 LOG.info("Starting (S)FTP server on port %s..."%port)
 apply_patches()
 authorizer=DummyAuthorizer()
 user_dir=new_tmp_dir()
 authorizer.add_user(ROOT_USER[0],ROOT_USER[1],user_dir,perm=FTP_USER_PERMISSIONS)
 anonymous_dir=new_tmp_dir()
 authorizer.add_anonymous(anonymous_dir)
 handler=TLS_FTPHandler
 combined_file,_,_=GenericProxy.create_ssl_cert()
 handler.certfile=combined_file
 handler.authorizer=authorizer
 handler.passive_ports=FTP_PASSIVE_PORTS
 handler.masquerade_address=ext_config.LOCALHOST_IP
 def do_run(*args):
  try:
   server=FTPServer(("0.0.0.0",port),handler)
   server.serve_forever()
  except emLtj as e:
   LOG.info("Unable to run FTP server on port %s: %s"%(port,e))
   raise
 if asynchronous:
  t=FuncThread(do_run)
  t.start()
  return t
 return do_run()
def get_directory_mapping():
 result=DIRECTORY_MAPPING
 if USE_SUBPROCESS:
  dir_file=get_directory_mapping_file()
  result=json.loads(load_file(dir_file)or "{}")
 return result
def set_directory_mapping(key,value):
 mapping=get_directory_mapping()
 mapping[key]=value
 if USE_SUBPROCESS:
  dir_file=get_directory_mapping_file()
  save_file(dir_file,json.dumps(mapping))
 return value
def get_directory_mapping_file():
 return DIRECTORY_MAPPING_FILE.replace("<data_dir>",localstack_config.dirs.tmp)
def main():
 do_start_ftp(emLtI(sys.argv[1]),asynchronous=emLtG)
if __name__=="__main__":
 main()
# Created by pyminifier (https://github.com/liftoff/pyminifier)
