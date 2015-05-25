#!/usr/bin/python

import os
import sys
import ssl
import getopt
import socket
import thread
import random
import pickle

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~ The sun is a wondrous body, like a magnificent father - if only I could be ~
# ~                       so ~grossly incandescent~                            ~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

VERSION="I AM SUN OF HOUSE ARISUN - AND I AM INVINCIBLE"

class conversationEditor:
  def __init__(self,f=None,interactive=True):
    self.seqFile = None
    self.sequence = socketConversation()
    if f:
      self.sequence.loadFromFile(f)
    if interactive:
      self.editShell()

  def editShell(self):
    continueFlag = True
    while continueFlag:
      q = raw_input(" > ").rstrip().lstrip()
      commandTokens = q.split(" ")
      c = commandTokens[0]
      if c in ("q","quit"):
        continueFlag = False

class socketConversation:
  DIRECTION_FORWARD = 1
  DIRECTION_BACK = 2

  def __init__(self,f=None):
    if f is not None:
      self.loadFromFile(f)
    else:
      self.messages = []

  def loadFromFile(self,filename):
    f = open(filename,"r")
    v = f.readline().rstrip()
    global VERSION
    if v != VERSION:
      raise "[err: version mismatch]"
    else:
      cv = f.read()
      self.messages = pickle.loads(cv)
    f.close()
  
  def saveToFile(self,filename):
    f = open(filename,"w")
    global VERSION
    f.write(VERSION)
    f.write(pickle.dumps(self.messages))
    f.close()

  def appendMessage(self,direction,message):
    self.messages += (direction,message)

def replay(_outHost,file,sslreq):
  (outHost,outPort) = _outHost.split(":")
  print "[replay: %s:%d - %s]" % (outHost,int(outPort),file)
  conv = socketConversation(file)
  print "[success]"
  if sslreq:
    forwardSocket_ = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    forwardSocket = ssl.wrap_socket(forwardSocket_,cert_reqs=ssl.CERT_NONE)
  else:
    forwardSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  forwardSocket.connect( (outHost, int(outPort)) )

# only start this when there's a connection
def captureserver(clientsock,addr,_outHost,file,tag,sslreq):
  BUFSIZE = 10240
  conv = socketConversation()
  (outHost,outPort) = _outHost.split(":")
  if sslreq:
    forwardSocket_ = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    forwardSocket = ssl.wrap_socket(forwardSocket_,cert_reqs=ssl.CERT_NONE)
  else:
    forwardSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  forwardSocket.connect( (outHost,int(outPort)) )
  forwardSocket.settimeout(1)
  clientsock.settimeout(1)
  while True:
    try:
      data = clientsock.recv(BUFSIZE)
      if not data: break
      forwardSocket.sendall(data)
      conv.appendMessage(socketConversation.DIRECTION_FORWARD,data)
    except socket.timeout:
      pass
    except ssl.SSLError, e: 
      if e.errno is None:
        pass
      else:
        print "[err: %s]" % e.message
        break
    try:
      data = forwardSocket.recv(BUFSIZE)
      if not data: break
      clientsock.sendall(data)
      conv.appendMessage(socketConversation.DIRECTION_BACK,data)
    except socket.timeout:
      pass
    except ssl.SSLError, e:
      if e.errno is None:
        pass
      else:
        print "[err: %s]" % e.message
        break
  print "[close: %04x]" % tag
  conv.saveToFile("%s-%d.cnv" % (file,tag))
  forwardSocket.close()
  clientsock.close()

def capture(_inHost,_outHost,file,sslreq):
  (inHost,inPort) = _inHost.split(":")
  (outHost,outPort) = _outHost.split(":")
  serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  serversocket.bind( (inHost,int(inPort)) )
  serversocket.listen(5)
  print "[%s:%d -> PROXY -> %s:%d] -> [%s]" % (inHost,int(inPort),outHost,int(outPort),file)
  while True:
    if sslreq:
      (clientsocket_,address) = serversocket.accept()
      clientsocket = ssl.wrap_socket(clientsocket_,server_side = True,certfile="server.crt",keyfile="server.key")
    else:
      print "attempting regular capture"
      (clientsocket,address) = serversocket.accept()
    tag = random.randint(0,0xFFFF)
    print "[open: %04x]" % tag
    thread.start_new_thread(captureserver, (clientsocket,address,_outHost,file,tag,sslreq))

def usage():
  print "-----------------------------------------"
  print " project pipedream"
  print "-----------------------------------------"
  print " -i port : listening socket"
  print " -o host:port : output socket"
  print " -m [capture|replay|edit] : select mode"
  print " -f filename : load or save to file"
  print " -s : use ssl"
  print " -h : help"
  print "-----------------------------------------"

def main():
  inHost = None
  outHost = None
  editor = False
  mode = None
  file = None
  sslRequired = False
  try:
    optlist,args = getopt.getopt(sys.argv[1:],"i:o:m:f:hs",["in","out","mode","file","help","ssl"])
  except getopt.GetoptError as err:
    print str(err)
    usage()
    sys.exit(2)
  for (o,a) in optlist:
    if o in ("-i","--in"):
      inHost = a
    elif o in ("-o","--out"):
      outHost = a
    elif o in ("-m","--mode"):
      mode = a
    elif o in ("-f","--file"):
      file = a
    elif o in ("-m","--mode"):
      mode = a
    elif o in ("-h","--help"):
      usage()
      sys.exit(2)
    elif o in ("-s","--ssl"):
      sslRequired = True
    else:
      print "error: unknown argument %s" % o
  if mode == "capture" and inHost is not None and outHost is not None and file is not None:
    capture(inHost,outHost,file,sslRequired)
  elif mode == "replay" and outHost is not None and file is not None:
    replay(outHost,file,sslRequired)
  elif mode == "edit":
    e = editFactory(file)
  else:
    usage()
    sys.exit(0)

if __name__ == "__main__":
  main()
