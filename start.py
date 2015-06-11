#!/usr/bin/python

import sys
import os

def push(a):
  filename = a["file"]
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

def pull(a):
  inputserver = a["input"]
  mask = a["mask"]
  count = int(a["count"])
  (inputHost,inputPort) = inputserver.split(":")
  for i in range(0,count):
    forwardSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    forwardSocket.connect( (inputHost, int(inputPort)) )
    print "[connected %d]" % i,
    newFileName = "bucket/%d.%s" % (i,mask)
    f = open(newFileName,"wb")
    continueFlag = True
    forwardSocket.settimeout(1)
    while continueFlag is True:
      d = forwardSocket.recv(1024)
      if not d: break
      f.write(d)
    print "[close]"
    f.close()
  return

if __name__ == "__main__":
  continueFlag = True
  a = {}
  b = {}
  b["push"] = (["file"],"push(a)","convert a file to a .cnv which can be directly used in a pull command")
  b["pull"] = (["input","extension","count"],"pull(a)","pull #count files from input server, saving to bucket/*.extension")
  b["q"] = ([],"sys.exit(0)")
  while continueFlag:
    c = raw_input(" > ").rstrip().lstrip()
    commandTokens = c.split(" ")
    if commandTokens[0] == "set" and len(commandTokens) >= 3:
      varName = commandTokens[1]
      varValue = " ".join(commandTokens[2:])
      a[varName] = varValue
    elif commandTokens[0] in b.keys():
      (requiredParameter,runFunction,halpz) = b[commandTokens[0]]
      contFlag = True
      for p in requiredParameter:
        if p not in a.keys():
          contFlag = False
      if contFlag == False:
        print " %s requires more flags (%s)" % (commandTokens[0],requiredParameter)
        continue
      else:
        exec(runFunction)
    else:
      print " unknown command %s" % commandTokens[0]