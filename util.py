#!/usr/bin/python

import sys
import pickle
import getopt
import socket
from sm import *

def chunks(l, n):
  n = max(1, n)
  return [l[i:i + n] for i in range(0, len(l), n)]

def pushFile(filename):
  print "[inf: pushing %s]" % filename
  f = open(filename,"rb")
  data = f.read()
  f.close()
  sc = socketConversation()
  splitdata = chunks(data,1024)
  for d in splitdata:
    sc.appendMessage(socketConversation.DIRECTION_BACK,d)
  for s in sc.messages:
    s.setMandatory(True) # does this flag mean send it all the time?
  # cap it.
  sc.messages[len(sc.messages) - 1].disconnect = True
  sc.saveToFile(filename+".cnv")
  print "[inf: saved to %s]" % (filename + ".cnv")

def pullFile(inputserver, mask, count):
  (inputHost,inputPort) = inputserver.split(":")
  for i in range(0,count):
    forwardSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    forwardSocket.connect( (inputHost, int(inputPort)) )
    print "[connected %d]" % i,
    newFileName = mask % i
    f = open(newFileName,"wb")
    continueFlag = True
    while continueFlag:
      try:
        d = forwardSocket.recv() 
        f.write(d)
      except:
        continueFlag = False
    print "[close]"
    f.close()

def usage():
  print "m [push/pull]: convert a file to a conv or vice versa"
  print "f [filename] : specify a filename / input server to use"
  return

if __name__ == "__main__":
  try:
    optlist,args = getopt.getopt(sys.argv[1:],"m:f:o:i:c:",["mode","file","output","input","count"])
  except getopt.GetoptError as err:
    print str(err)
    usage()
    sys.exit(2)
  mode = None
  file = None
  outfileMask = None
  inputServer = None
  fuzzCount = 100
  for (o,a) in optlist:
    if o in ("-m","--mode"):
      mode = a
    elif o in ("-f","--file"):
      file = a
    elif o in ("-o","--output"):
      outfileMask = a
    elif o in ("-i","--input"):
      inputServer = a
    elif o in ("-c","--count"):
      fuzzCount = int(a)
    else:
      print "[err: unrecognized argument - %s]" % (o)
  if mode == "push" and file is not None:
    pushFile(file)
  elif mode == "pull" and inputServer is not None:
    if outfileMask is None:
      (inputHost,inputPort) = inputServer.split(":")
      outfileMask = "bucket/" + inputHost + "-%x.cnv"
    pullFile(inputServer,outfileMask,fuzzCount)