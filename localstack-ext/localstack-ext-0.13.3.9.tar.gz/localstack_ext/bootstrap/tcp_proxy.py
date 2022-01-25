#!/usr/bin/env python
wNbqo=dict
wNbqf=super
wNbqa=hasattr
wNbqc=Exception
wNbqW=object
wNbqM=dir
wNbqk=None
wNbqe=False
wNbqu=True
wNbqT=len
wNbqU=set
import errno
import socket
from select import select
from socket import(AF_INET,AF_INET6,IPPROTO_IPV6,IPPROTO_TCP,IPV6_V6ONLY,SO_REUSEADDR,SOCK_STREAM,SOL_SOCKET,TCP_NODELAY)
class AttrDict(wNbqo):
 def __init__(self,*args,**kwargs):
  wNbqf(AttrDict,self).__init__(*args,**kwargs)
  self.__dict__=self
def tcp_listen(six,addr,port,blk):
 s=socket.socket(AF_INET6 if six else AF_INET,SOCK_STREAM)
 if six and wNbqa(socket,"IPV6_V6ONLY"):
  s.setsockopt(IPPROTO_IPV6,IPV6_V6ONLY,0)
 s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
 s.setsockopt(IPPROTO_TCP,TCP_NODELAY,1)
 s.bind((addr,port))
 s.listen(5)
 s.setblocking(blk)
 return s
def tcp_connect(six,addr,port,blk):
 s=socket.socket(AF_INET6 if six else AF_INET,SOCK_STREAM)
 s.setsockopt(IPPROTO_TCP,TCP_NODELAY,1)
 s.connect((addr,port))
 s.setblocking(blk)
 return s
def safe_close(x):
 try:
  x.close()
 except wNbqc:
  pass
class Server(wNbqW):
 def __init__(self,opt,q):
  self.opt=opt
  self.sock=tcp_listen(opt.ip6,opt.bind_addr,opt.bind_port,0)
  self.q=q
 def pre_wait(self,rr,r,w,e):
  r.append(self.sock)
 def post_wait(self,r,w,e):
  if self.sock in r:
   cl,addr=self.sock.accept()
   cl.setblocking(0)
   self.q.append(Proxy(self.opt,cl,addr))
class Half(wNbqW):
 def __init__(self,opt,sock,addr,wNbqM):
  self.opt=opt
  self.sock=sock
  self.addr=addr
  self.wNbqM=wNbqM
  self.name="peer" if self.wNbqM else "client"
  self.queue=[]
  self.dest=wNbqk
  self.err=wNbqk
  self.ready=wNbqe
 def pre_wait(self,rr,r,w,e):
  if self.ready:
   rr.append(self.sock)
  r.append(self.sock)
  if self.queue:
   w.append(self.sock)
 def post_wait(self,r,w,e):
  if not self.err and self.sock in w and self.queue:
   self.write_some()
  if not self.err and self.sock in r:
   self.ready=wNbqu
   self.copy()
  return self.err
 def error(self,msg,e):
  self.err="Error on %s: %s: %s"%(self.name,msg,e)
  return self.err
 def write_some(self):
  try:
   n=self.sock.send(self.queue[0])
  except wNbqc as e:
   return self.error("send error",e)
  if n!=wNbqT(self.queue[0]):
   self.queue[0]=self.queue[0][n:]
  else:
   del self.queue[0]
 def copy(self):
  try:
   buf=self.sock.recv(4096)
  except socket.error as e:
   if e.errno==errno.EWOULDBLOCK:
    self.ready=wNbqe
    return
   return self.error("recv socket error",e)
  except wNbqc as e:
   return self.error("recv error",e)
  if wNbqT(buf)==0:
   return self.error("eof",0)
  self.dest.queue.append(buf)
 def close(self):
  safe_close(self.sock)
class Proxy(wNbqW):
 def __init__(self,opt,sock,addr):
  self.opt=opt
  self.cl=Half(opt,sock,addr,"i")
  peer=tcp_connect(opt.ip6,opt.addr,opt.port,0)
  self.peer=Half(opt,peer,addr,"o")
  self.cl.dest=self.peer
  self.peer.dest=self.cl
  self.err=wNbqk
 def pre_wait(self,rr,r,w,e):
  self.cl.pre_wait(rr,r,w,e)
  self.peer.pre_wait(rr,r,w,e)
 def post_wait(self,r,w,e):
  if not self.err:
   self.err=self.cl.post_wait(r,w,e)
  if not self.err:
   self.err=self.peer.post_wait(r,w,e)
  if self.err:
   self.cl.close()
   self.peer.close()
  return self.err
def server_loop(opt):
 qs=[]
 opt["ip6"]=opt.get("ip6",wNbqe)
 opt["bind_addr"]=opt.get("bind_addr","0.0.0.0")
 opt["addr"]=opt.get("addr","127.0.0.1")
 opt["bind_port"]=opt.get("bind_port",0)
 opt=AttrDict(opt)
 qs.append(Server(opt,qs))
 while qs:
  rr,r,w,e=[],[],[],[]
  for q in qs:
   q.pre_wait(rr,r,w,e)
  timeo=10.0 if not rr else 0.0
  r,w,e=select(r,w,e,timeo)
  r=wNbqU(r).union(rr)
  for q in qs:
   if q.post_wait(r,w,e):
    qs.remove(q)
def main():
 opt={"ip6":wNbqe,"bind_port":2223,"addr":"192.168.43.191","port":22}
 opt={"ip6":wNbqe,"bind_port":48429,"addr":"128.0.100.3","port":22}
 opt={"ip6":wNbqe,"port":54237,"bind_addr":"128.0.100.2","bind_port":22}
 opt={"ip6":wNbqe,"port":54237,"bind_addr":"192.168.100.3","bind_port":22}
 server_loop(opt)
if __name__=="__main__":
 main()
# Created by pyminifier (https://github.com/liftoff/pyminifier)
