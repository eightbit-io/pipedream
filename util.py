#!/usr/bin/python

import sys
import pickle
import getopt
from sm import *

def chunks(l, n):
  n = max(1, n)
  return [l[i:i + n] for i in range(0, len(l), n)]

def pushFile(filename):
  f = open(sys.argv[1],"rb")
  data = f.read()
  f.close()
  sc = socketConversation()
  splitdata = chunks(data,1024)
  for d in splitdata:
    sc.appendMessage(socketConversation.DIRECTION_BACK,d)
  for s in sc.messages:
    s.setMandatory(True) # does this flag mean send it all the time?
  sc.saveToFile(filename+".cnv")
  print "[inf: saved to %s]" % (sys.argv[1] + ".cnv")

def pullFile(inputserver, mask, count):
  (inputHost,inputPort) = inputserver.split(":")
  print "NOT DONE YET"

def usage():
  print "m [push/pull]: convert a file to a conv or vice versa"
  print "f [filename] : specify a filename / input server to use"
  return

if __name__ == "__main__":
  try:
    optlist,args = getopt.getopt(sys.argv[1:],"m:f:o:i:",["mode","file","output","input"])
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
    if o in ("m","mode"):
      mode = a
    elif o in ("f","file"):
      file = a
    elif o in ("o","output"):
      outfileMask = a
    elif o in ("i","input"):
      inputServer = a
    elif o in ("c","count"):
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