#!/usr/bin/python

import sys
import os
from sm import *
from rs import *
from rc import *
from cs import *
from ce import *
from px import *

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

def usage(b):
  for keyword in b.keys():
    (params,command,helptext) = b[keyword]
    if helptext is None:
      continue
    if len(params) == 0:
      print " %s [] %s" % (keyword,helptext)
    else:
      print " %s [requires:" % keyword,
      for p in params:
        print "%s" % p,
      print "] %s" % helptext

def proxy_capture(a):
  inHost = a["in"]
  outHost = a["out"]
  file = a["file"]
  sslRequired = False
  if a["ssl"] in ["y","yes","true"]:
    sslRequired = True
  capture(inHost,outHost,file,sslRequired)

def proxy_replayclient(a):
  outHost = a["out"]
  file = a["file"]
  sslRequired = False
  if a["ssl"] in ["y","yes","true"]:
    sslRequired = True
  mutChance = int(a["chance"])
  replayclient(outHost,file,sslRequired,mutChance)

def proxy_replayserver(a):
  inHost = a["in"]
  file = a["file"]
  sslRequired = False
  if a["ssl"] in ["y","yes","true"]:
    sslRequired = True
  mutChance = int(a["chance"])
  replayserver(inHost,file,sslRequired,mutChance)

def proxy_proxy(a):
  inHost = a["in"]
  outHost = a["out"]
  sslRequired = False
  if a["ssl"] in ["y","yes","true"]:
    sslRequired = True
  file = int(a["tamper"])
  replayserver(inHost,file,sslRequired,mutChance)

def proxy_editor(a):
  file = a["file"]
  e = conversationEditor(file)

def listCommands(a):
  print "-" * 64
  print " ",
  horizontalLength = 2
  for k in a.keys():
    if horizontalLength + len(k) + 2 > 64:
      print ""
      print " ",
      horizontalLength = 2
    print "%s" % k,
    horizontalLength += len(k) + 1
  print ""
  print "-" * 64

if __name__ == "__main__":
  continueFlag = True
  a = {}
  b = {}
  b["push"] = (["file"],"push(a)","convert a file to a .cnv which can be directly used in a pull command")
  b["pull"] = (["input","ext","count"],"pull(a)","pull #count files from input server, saving to bucket/*.extension")
  b["q"] = ([],"sys.exit(0)",None)
  b["quit"] = ([],"sys.exit(0)","exit the program")
  b["help"] = ([],"usage(b)","display a help message")
  b["h"] = ([],"usage(b)",None)
  b["capture"] = (["in","out","file","ssl"],"proxy_capture(a)","capture traffic from in -> out, saving to file. ssl is [true|false]")
  b["replay"] = (["out","file","ssl","chance"],"proxy_replayclient(a)","replay a client, connecting to out. ssl is [true|false]")
  b["replayserver"] = (["in","file","ssl","chance"],"proxy_replayserver(a)","replay a server, listening on in. ssl is [true|false]")
  b["proxy"] = (["in","tamper","ssl","out"],"proxy_proxy(a)","pretend to be a proxy server, tampering data with the tamper script")
  b["edit"] = (["file"],"proxy_editor(a)","edit the conversation in [file]")
  b["ls"] = ([],"listCommands(b)","list commands")
  listCommands(b)
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