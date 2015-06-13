#!/usr/bin/python

from sm import *

def prettyPrint(i,d,message):
  meow = ""
  if d == socketConversation.DIRECTION_FORWARD:
    print " [ message %4d -> len:0x%08x ]" % (i,len(message))
  else:
    print " [ message %4d <- len:0x%08d ]" % (i,len(message))
  print " [",
  # totalLength = len(message) % 8
  for i in range(0,len(message)):
    if i != 0 and i % 8 == 0:
      print " %s ]\n [" % meow,
      meow = ""
    elif i != 0 and i % 4 == 0:
      print "-",
    print "%02x" %  int(ord(message[i])),
    if message[i] in string.printable and message[i] != '\r' and message[i] != '\n':
      meow += message[i]
    else:
      meow += "."
  i += 1
  while i % 8 != 0:
    if i != 0 and i % 4 == 0:
      print "-",
    print "..",
    meow += "."
    i += 1
  print " %s ]" % meow

def prettyPrintShort(i,d,message):
  meow = ""
  if d == socketConversation.DIRECTION_FORWARD:
    print " [ %d -> len:0x%04x ]" % (i,len(message)),
  else:
    print " [ %d <- len:0x%04x ]" % (i,len(message)),
  print " [",
  for i in range(0,len(message)):
    if i != 0 and i % 8 == 0:
      print ""
    print "%02x" %  int(ord(message[i])),
    if message[i] in string.printable and message[i] != '\r' and message[i] != '\n':
      meow += message[i]
    else:
      meow += "."
    if i == 7:
      break
  while i % 7 != 0:
    if i != 0 and i % 4 == 0:
      print "-",
    print "..",
    meow += "."
    i += 1
  print " %s ]" % meow

def printSelection(m,row,column):
  meow = ""
  startI = row * 8
  maxI = startI + 8
  print " [",
  for i in range(startI,maxI):
    if i >= len(m):
      print "..",
      meow += "."
    else:
      if i % 8 == column:
        print "[%02x]" % ord(m[i]),
      else:
        print "%02x" % ord(m[i]),
      if m[i] in string.printable and m[i] != '\r' and m[i] != '\n':
        meow += m[i]
      else:
        meow += "."
  print " %s ]" % meow,

class conversationEditor:
  def __init__(self,f=None,interactive=True):
    self.selectToken = None
    self.sequence = None
    self.saveFile = None
    self.changeFlag = False
    print "---------------------------------------------------------------"
    self.help()
    print "---------------------------------------------------------------"
    if f:
      self.sequence = socketConversation(f)
      self.saveFile = f
    if interactive:
      self.editShell()

  def printConversation(self,start=None,end=None):
    if self.sequence is None:
      print "[err: sequence not loaded]"
      return
    else:
      if start is None or end is None:
        for i in range(0,20):
          self.sequence.messages[i].prettyPrintShort(i)
          #(d,m) = self.sequence.fetchMessage(i)
          #prettyPrintShort(i,d,m)
      else:
        for i in range(start,end):
          self.sequence.messages[i].prettyPrintShort(i)
      print " [total: %d]" % len(self.sequence.messages)

  def editPacketHelp(self):
    print " q: quit, without save"
    print " g: quit, with save (not to file)"
    print " w/s/a/d: control cursor"
    print " x [byte]: overwrite byte"
    print " +: move byte forward"
    print " -: move byte backward"

  # edit packet
  def editPacket(self,packet):
    try:
      (d,m) = self.sequence.fetchMessage(packet)
    except:
      print " [err: could not load %d]" % packet
      return
    print "---------------------------------------------------------------"
    self.editPacketHelp()
    print "---------------------------------------------------------------"
    continueFlag = True
    selectedColumn = 0
    selectedRow = 0
    maxRow = len(m) / 8 # max row counted from 0
    while continueFlag:
      printSelection(m,selectedRow,selectedColumn)
      q = raw_input(": ").rstrip().lstrip()
      commandTokens = q.split(" ")
      c = commandTokens[0]
      if c in ("q","quit"):
        continueFlag = False
      elif c in ("h","help"):
        self.editPacketHelp()
      elif c in ("+","-"):
        cPos = selectedRow * 8 + selectedColumn
        if c == "+" and cPos < len(m) - 1:
          temp1 = m[cPos]
          temp2 = m[cPos + 1]
          m[cPos] = temp2
          m[cPos + 1] = temp1
        elif c == "-" and cPos > 0:
          temp1 = m[cPos]
          temp2 = m[cPos - 1]
          m[cPos] = temp2
          m[cPos - 1] = temp1
      elif c in ("w","s"):
        if c == "w" and selectedRow > 0:
          selectedRow -= 1
        elif c == "s" and selectedRow < maxRow:
          selectedRow += 1
        selectedColumn = 0
      elif c in ("a","d"):
        if c == "a" and selectedColumn > 0:
          selectedColumn -= 1
        elif c == "d" and selectedColumn < 7 and (selectedRow * 8 + selectedColumn < len(m) - 1): # 8 width, so 6->7 is the last 'd' command
          selectedColumn += 1
      elif c == "g":
        self.sequence.saveMessage(packet,(d,m))
        self.changeFlag = True
        continueFlag = False
      elif c == "x" and len(commandTokens) == 2 and len(commandTokens[1]) == 2:
        tempM = bytearray(m)
        tempM[selectedRow * 8 + selectedColumn] = chr( int(commandTokens[1],16) )
        m = str(tempM)

  def help(self,command=None):
    global ceCommands
    if command is None:
      print " commands available:",
      cLen = 0
      for c in ceCommands.keys():
        print "%s," % c,
        cLen += len(c) + 2
        if cLen > 30:
          print ""
          print " " * len(" commands available:"),
          cLen = 0
      print ""
    else:
      print "%s" % ceCommands[command]

  def editShell(self):
    continueFlag = True
    while continueFlag:
      if self.changeFlag is True:
        print " *",
      if self.selectToken is None:
        q = raw_input(" [####] : ").rstrip().lstrip()
      else:
        q = raw_input(" [%4d] : " % self.selectToken).rstrip().lstrip()
      commandTokens = q.split(" ")
      if len(commandTokens) > 1:
        try:
          sNum = int(commandTokens[0])
          self.selectToken = sNum
          commandTokens.pop(0)
        except:
          pass
      c = commandTokens[0]
      if c in ("q","quit"):
        continueFlag = False
      elif c in ("p","print"):
        if len(commandTokens) == 1:
          if self.selectToken is None:
            if len(self.sequence.messages) >= 20:
              self.printConversation(0,20)
            else:
              self.printConversation(0,len(self.sequence.messages))
          else:
            start = self.selectToken - 10
            if start < 0: start = 0
            end = self.selectToken + 10
            if end > len(self.sequence.messages) : end = len(self.sequence.messages)
            self.printConversation(start,end)
            #(d,m) = self.sequence.fetchMessage(self.selectToken)
            #prettyPrint(self.selectToken,d,m)
        elif len(commandTokens) == 2:
          if commandTokens[1] in ("a","all"):
            self.printConversation(0,len(self.sequence.messages))
          else:
            i = int(commandTokens[1])
            try:
              (d,m) = self.sequence.fetchMessage(i)
              prettyPrint(i,d,m)
            except:
              print " [err: could not fetch message %d]" % i
      elif c in ("s","select") and len(commandTokens) == 2:
        try:
          self.selectToken = int(commandTokens[1])
          if self.selectToken > len(self.sequence.messages):
            self.selectToken = None
        except:
          self.selectToken = None
      elif c in ("s","select") and len(commandTokens) == 1:
        self.selectToken = None
      elif c in ("f","flip") and self.selectToken is not None:
        try:
          (d,m) = self.sequence.fetchMessage[self.selectToken]
          self.sequence.setMessage(self.selectToken,(2 - d + 1, m))
          self.changeFlag = True
        except:
          print " [err: could not fetch message %d]" % self.selectToken
      elif c in ("d","del","delete","rm"):
        if len(commandTokens) == 1:
          try:
            del self.sequence.messages[self.selectToken]
            if self.selectToken > len(self.sequence.messages):
              self.selectToken = None
            self.changeFlag = True
          except:
            print " [err: could not delete message %d]" % self.selectToken
          if self.selectToken > len(self.sequence.messages) - 1:
            self.selectToken = None
        else:
          try:
            del self.sequence.messages[int(commandTokens[1])]
          except:
            print " [err: could not delete message %s]" % commandTokens[1]
      elif c in ("l","load") and len(commandTokens) == 2:
        self.sequence = socketConversation(commandTokens[1])
        self.saveFile = commandTokens[1]
      elif c == "save":
        if len(commandTokens) == 2:
          self.sequence.saveToFile(commandTokens[1])
        elif self.saveFile is not None:
          self.sequence.saveToFile(self.saveFile)
        self.changeFlag = False
      elif c in ("e","edit") and self.selectToken is not None:
        self.editPacket(self.selectToken)
      elif c in ("x","export") and self.selectToken is not None and len(commandTokens) == 2:
        try:
          (d,m) = self.sequence.fetchMessage(self.selectToken)
          f = open(commandTokens[1],"wb")
          f.write(m)
          f.close()
        except:
          print " [err: probably misspelled filename]"
      elif c in ("i","import") and len(commandTokens) == 2:
        try:
          f = open(commandTokens[1],"rb")
          data = f.read()
          f.close()
          if self.selectToken is None:
            self.sequence.appendMessage(socketConversation.DIRECTION_FORWARD,data)
          else:
            self.sequence.setMessage(self.selectToken,(socketConversation.DIRECTION_FORWARD,data))
        except:
          print " [err: probably misspelled filename]"
      elif c == "-" and self.selectToken is not None:
        if self.selectToken != 0:
          temp1 = self.sequence.messages[self.selectToken]
          temp2 = self.sequence.messages[self.selectToken - 1]
          self.sequence.messages[self.selectToken - 1] = temp1
          self.sequence.messages[self.selectToken] = temp2
          self.changeFlag = True
      elif c == "+" and self.selectToken is not None:
        if self.selectToken + 1 < len(self.sequence.messages):
          temp1 = self.sequence.messages[self.selectToken]
          temp2 = self.sequence.messages[self.selectToken + 1]
          self.sequence.messages[self.selectToken + 1] = temp1
          self.sequence.messages[self.selectToken] = temp2
          self.changeFlag = True
      elif c == "swallow" and self.selectToken is not None and len(commandTokens) == 2:
        self.sequence.messages[self.selectToken].swallow(self.sequence.messages[int(commandTokens[1])].message)
        del(self.sequence.messages[int(commandTokens[1])])
      elif c == "bind" and len(commandTokens) == 2 and self.selectToken is not None:
        self.sequence.messages[self.selectToken].bindWord(commandTokens[1])
      elif c == "set" and len(commandTokens) > 2 and self.selectToken is not None:
        if commandTokens[1] == "python" and len(commandTokens) == 3:
          if commandTokens[2] == "None":
            self.sequence.messages[self.selectToken].delPython()
          else:
            self.sequence.messages[self.selectToken].setPython(commandTokens[1])
        elif commandTokens[1] == "mandatory" and len(commandTokens) == 3:
          if commandTokens[2] == "yes":
            self.sequence.messages[self.selectToken].setMandatory(True)
          elif commandTokens[2] == "no":
            self.sequence.messages[self.selectToken].setMandatory(False)
        elif commandTokens[1] == "disconnect" and len(commandTokens) == 3:
          if commandTokens[2] == "yes":
            self.sequence.messages[self.selectToken].setDisconnect(True)
          elif commandTokens[2] == "no":
            self.sequence.messages[self.selectToken].setDisconnect(False)
        elif commandTokens[1] == "static" and len(commandTokens) == 3:
          if commandTokens[2] == "yes":
            self.sequence.messages[self.selectToken].setStatic(True)
          elif commandTokens[2] == "no":
            self.sequence.messages[self.selectToken].setStatic(False)
      elif c in ("h","help"):
        if len(commandTokens) >= 2:
          self.help(commandTokens[1])
        else:
          self.help()

ceCommands = {}
ceCommands["q"] = " q : quit pipedream"
ceCommands["p"] = " p [all | num] : print whole sequence or selected message"
ceCommands["l"] = " l [file] : load sequence from file"
ceCommands["h"] = " h [command] : list commands, or display help for a given command"
ceCommands["s"] = " s [num | none] : select a given packet, or clear selection"
ceCommands["f"] = " f : flip direction of message"
ceCommands["d"] = " d : delete the currently selected packet"
ceCommands["e"] = " e : edit the currently selected packet"
ceCommands["x"] = " x [file] : export the currently selected packet to a file"
ceCommands["i"] = " i [file] : replace the currently selected packet with data from a file"
ceCommands["set"] = " set [python | mandatory | static] [yes | no] : set attributes of currently selected packet"
ceCommands["swallow"] = " swallow [num] : attach the target packet to the currently selected packet"
ceCommands["bind"] = " bind [regex] : assign a regular expression to a packet: when pipedream in replay mode receives data matching a regex, it plays the selected packet"
ceCommands["save"] = " save [filename] : save the current conversation to a file"
ceCommands["+"] = " + : move a packet forward by one position"
ceCommands["-"] = " - : move a packet backward by one position"
