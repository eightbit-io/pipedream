#!/usr/bin/python

import sys
import os

def initInterface():
  

if __name__ == "__main__":
  continueFlag = True
  a = {}
  b = {}
  while continueFlag:
    c = raw_input().rstrip().lstrip()
    commandTokens = c.split(" ")
    if commandTokens[0] == "set" and len(commandTokens) > 3:
      varName = commandTokens[1]
      varValue = " ".join(commandTokens[2:])
      a[varName] = varValue
    elif commandTokens[1] in b.keys():
      